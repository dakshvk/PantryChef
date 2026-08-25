"""
LegalMind AI - Main Entry Point
Agentic RAG system for legal research using LangGraph, Gemini, and Pinecone.
"""
import os
import sys
from dotenv import load_dotenv
from graph import create_legal_rag_graph
from google import genai


load_dotenv()


def main():
    """Main entry point for LegalMind AI."""
    
    # Check environment variables
    required_vars = ["GEMINI_API_KEY", "PINECONE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with these variables.")
        sys.exit(1)
    
    # Initialize the graph
    print("🔧 Initializing LegalMind AI graph...")
    app = create_legal_rag_graph()
    
    # Get user question
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("\n⚖️  Enter your legal question: ").strip()
    
    if not question:
        print("❌ No question provided.")
        sys.exit(1)
    
    # Initialize state
    initial_state = {
        "question": question,
        "generation": "",
        "documents": [],
        "loop_step": 0,
        "rewrite_count": 0,
        "needs_retrieval": True,
        "hallucination_grade": "",
        "answer_grade": ""
    }
    
    print(f"\n📋 Question: {question}")
    print("\n🚀 Processing...\n")
    print("="*60)
    
    try:
        # Run the graph
        result = app.invoke(initial_state)
        
        # Display results
        print("\n" + "="*60)
        print("📄 FINAL ANSWER")
        print("="*60)
        print(result["generation"])
        print("\n" + "="*60)
        
        # Display metadata if available
        if result.get("documents"):
            print(f"\n📚 Retrieved {len(result['documents'])} documents")
        if result.get("loop_step", 0) > 0:
            print(f"🔄 Total loop steps: {result['loop_step']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

