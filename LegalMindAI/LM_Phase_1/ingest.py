"""
Week 1: Ingestion Pipeline
Automates data flow from court websites to Pinecone.
"""
from google import genai
import os
import requests
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from juriscraper.opinions.united_states.federal_appellate import ca1
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()



def get_latest_cases(limit: int = 10, output_dir: str = "data") -> List[str]:
    """
    Scrape latest cases from court website using Juriscraper.
    
    Args:
        limit: Maximum number of cases to download
        output_dir: Directory to save PDF files
        
    Returns:
        List of downloaded PDF file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    site = ca1.Site()
    print("🔄 Scraping court website...")
    site.parse()

    names = site.case_names
    urls = site.download_urls
    dates = getattr(site, 'case_dates', [None] * len(names))

    downloaded_paths = []
    
    for i, (case_name, url, date) in enumerate(zip(names, urls, dates)):
        if i >= limit:
            break

        if url:
            print(f"📥 Downloading: {case_name}")
            # Clean the name for the file system
            safe_name = "".join([c for c in case_name if c.isalnum() or c in (' ', '_', '-')]).strip()
            path = os.path.join(output_dir, f"{safe_name.replace(' ', '_')[:100]}.pdf")

            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(path, 'wb') as f:
                    f.write(response.content)
                downloaded_paths.append(path)
                print(f"✅ Saved: {path}")
            except Exception as e:
                print(f"❌ Failed to download {case_name}: {e}")

    return downloaded_paths


def process_and_index_pdfs(
    pdf_paths: List[str],
    index_name: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> None:
    """
    Process PDFs, chunk them, embed, and upload to Pinecone.
    
    Args:
        pdf_paths: List of PDF file paths to process
        index_name: Name of Pinecone index
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    # Initialize Pinecone - strip to remove hidden spaces/newlines
    raw_api_key = os.environ.get("PINECONE_API_KEY", "")
    api_key = raw_api_key.strip()
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment variables")
    
    # Initialize embeddings - strip to remove hidden spaces/newlines
    raw_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    gemini_key = raw_gemini_key.strip()
    if not gemini_key:
        raise ValueError("❌ GEMINI_API_KEY not found in environment variables")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=gemini_key)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Process each PDF
    for pdf_path in pdf_paths:
        print(f"\n📄 Processing: {pdf_path}")
        
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Extract case name from filename
            case_name = os.path.basename(pdf_path).replace('.pdf', '').replace('_', ' ')
            
            # Add metadata to each document
            for doc in documents:
                doc.metadata.update({
                    "case_name": case_name,
                    "source_file": pdf_path,
                    "ingestion_date": datetime.now().isoformat()
                })
            
            # Split into chunks
            splits = text_splitter.split_documents(documents)
            print(f"   Created {len(splits)} chunks")
            
            # Upsert to Pinecone
            vectorstore = PineconeVectorStore.from_documents(
                splits,
                embeddings,
                index_name=index_name
            )
            print(f"   ✅ Indexed {len(splits)} chunks to Pinecone")
            
        except Exception as e:
            print(f"   ❌ Error processing {pdf_path}: {e}")
            continue


def create_pinecone_index(index_name: str, dimension: int = 768) -> None:
    """
    Create Pinecone index if it doesn't exist.
    
    Args:
        index_name: Name of the index to create
        dimension: Embedding dimension (768 for text-embedding-004)
    """
    # Use .strip() to remove hidden spaces or newlines that cause 401 errors
    raw_api_key = os.environ.get("PINECONE_API_KEY", "")
    api_key = raw_api_key.strip()
    
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment variables")
    
    # Explicitly pass the stripped key
    pc = Pinecone(api_key=api_key)
    
    try:
        # This is where the 401 crash happens
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"🆕 Creating Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index '{index_name}' created successfully")
        else:
            print(f"ℹ️  Index '{index_name}' already exists")
    except Exception as e:
        print(f"❌ Pinecone Authentication Failed: {e}")
        print("   💡 Check your PINECONE_API_KEY in .env file")
        print("   💡 Verify the key is valid in your Pinecone dashboard")
        raise


if __name__ == "__main__":
    # Configuration
    INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "legalmind-index")
    CASE_LIMIT = int(os.environ.get("CASE_LIMIT", "10"))
    
    print("🚀 Starting LegalMind AI Ingestion Pipeline\n")
    
    # Step 1: Create/verify Pinecone index
    create_pinecone_index(INDEX_NAME, dimension=768)
    
    # Step 2: Scrape and download cases
    pdf_files = get_latest_cases(limit=CASE_LIMIT)
    
    if not pdf_files:
        print("⚠️  No PDFs downloaded. Using existing PDFs in data/ directory.")
        import glob
        pdf_files = glob.glob("data/*.pdf")
    
    if not pdf_files:
        print("❌ No PDF files found to process.")
        exit(1)
    
    # Step 3: Process and index
    print(f"\n📊 Processing {len(pdf_files)} PDF files...")
    process_and_index_pdfs(pdf_files, INDEX_NAME)
    
    print("\n✅ Ingestion pipeline completed successfully!")

