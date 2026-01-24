"""
Week 2-3: LangGraph Workflow with Self-Correction
Implements the Agentic RAG system with stateful graph and self-correction loops.
"""
from google import genai
import os
from typing import TypedDict, List, Literal, Optional
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langgraph.graph import StateGraph, END

load_dotenv()


# ============================================================================
# STATE DEFINITION
# ============================================================================

class GraphState(TypedDict):
    """State object that persists throughout the graph execution."""
    question: str  # Original user query
    generation: str  # Latest answer draft
    documents: List[str]  # Retrieved legal chunks
    loop_step: int  # Counter to prevent infinite loops
    rewrite_count: int  # Counter for query rewrites
    needs_retrieval: bool  # Whether retrieval is needed
    hallucination_grade: str  # Result of hallucination check: "pass" or "fail"
    answer_grade: str  # Result of answer check: "pass" or "fail"


# ============================================================================
# LLM INITIALIZATION (2025 Google GenAI SDK)
# ============================================================================

_gemini_client: Optional[genai.Client] = None

def get_gemini_client():
    """Initialize Gemini 2025 Client (singleton pattern)."""
    global _gemini_client
    if _gemini_client is None:
        raw_api_key = os.environ.get("GEMINI_API_KEY", "")
        api_key = raw_api_key.strip()
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables")
        try:
            _gemini_client = genai.Client(api_key=api_key)
        except Exception as e:
            raise ValueError(f"❌ Failed to initialize Gemini client: {e}")
    return _gemini_client


def call_gemini(prompt: str, model: str = "gemini-2.0-flash", system_instruction: Optional[str] = None) -> str:
    """
    Call Gemini using the 2025 SDK.
    
    Args:
        prompt: The user prompt/query
        model: Model name (default: gemini-2.0-flash for speed/accuracy balance)
        system_instruction: Optional system instruction
        
    Returns:
        Response text from Gemini
    """
    client = get_gemini_client()
    
    try:
        # Build the contents - combine system instruction and prompt if provided
        contents = prompt
        if system_instruction:
            # For the new SDK, we can include system instruction in the prompt
            contents = f"{system_instruction}\n\n{prompt}"
        
        response = client.models.generate_content(
            model=model,
            contents=contents
        )
        
        # Extract text from response
        return response.text.strip()
    except Exception as e:
        raise Exception(f"❌ Gemini API call failed: {e}")


def get_embeddings():
    """Initialize embeddings model."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)


def get_vectorstore(index_name: str = None):
    """Initialize Pinecone vector store."""
    if index_name is None:
        index_name = os.environ.get("PINECONE_INDEX_NAME", "legalmind-index")
    
    # Strip to remove hidden spaces/newlines that cause 401 errors
    raw_api_key = os.environ.get("PINECONE_API_KEY", "")
    api_key = raw_api_key.strip()
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment variables")
    
    embeddings = get_embeddings()
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )


# ============================================================================
# NODE: ROUTER
# ============================================================================

def route_question(state: GraphState) -> GraphState:
    """
    Classify query type: General legal info or specific case law.
    Updates state with routing decision.
    """
    question = state["question"]
    
    system_instruction = "You are a legal research assistant. Classify questions as either 'general' or 'retrieval'."
    prompt = f"""Classify the following question:

Question: {question}

Classify as either:
- "general" if it's asking for general legal information, definitions, or concepts
- "retrieval" if it requires specific case law, precedents, statutes, or case citations

Respond with ONLY one word: "general" or "retrieval"
"""
    
    response_text = call_gemini(prompt, system_instruction=system_instruction)
    classification = response_text.lower()
    
    if "general" in classification:
        state["needs_retrieval"] = False
    else:
        state["needs_retrieval"] = True
    
    return state


def decide_route(state: GraphState) -> Literal["general", "retrieval"]:
    """Decision function for routing after question classification."""
    if state.get("needs_retrieval", True):
        return "retrieval"
    else:
        return "general"


# ============================================================================
# NODE: GENERAL ANSWER
# ============================================================================

def general_answer(state: GraphState) -> GraphState:
    """Provide direct answer for general legal questions."""
    question = state["question"]
    
    system_instruction = """You are a knowledgeable legal research assistant. 
Provide accurate, clear answers to general legal questions.
If you don't know something, say so rather than guessing."""
    
    prompt = question
    
    response_text = call_gemini(prompt, system_instruction=system_instruction)
    
    state["generation"] = response_text
    state["needs_retrieval"] = False
    return state


# ============================================================================
# NODE: QUERY REWRITER
# ============================================================================

def rewrite_query(state: GraphState) -> GraphState:
    """
    Rewrite query to be more legal-centric if retrieval fails.
    Adds terms like "statute", "precedent", "case law", etc.
    """
    question = state["question"]
    rewrite_count = state.get("rewrite_count", 0)
    
    if rewrite_count >= 2:
        # Stop rewriting after 2 attempts
        return state
    
    system_instruction = "You are a legal research assistant. Rewrite queries to be more legal-centric and specific for case law retrieval."
    
    prompt = f"""Rewrite the following legal question to be more specific and legal-centric.
Add relevant legal terminology such as "statute", "precedent", "case law", "ruling", or "legal doctrine"
if appropriate. Make it more suitable for retrieving relevant case documents.

Original question: {question}

Rewritten question:"""
    
    rewritten = call_gemini(prompt, system_instruction=system_instruction)
    
    state["question"] = rewritten
    state["rewrite_count"] = rewrite_count + 1
    print(f"🔄 Query rewritten (attempt {rewrite_count + 1}): {rewritten}")
    
    return state


# ============================================================================
# NODE: RETRIEVER
# ============================================================================

def retrieve(state: GraphState) -> GraphState:
    """
    Retrieve relevant documents from Pinecone using hybrid search.
    Uses semantic + keyword matching.
    """
    question = state["question"]
    vectorstore = get_vectorstore()
    
    try:
        # Retrieve documents with hybrid search
        # Pinecone supports hybrid search with both dense (semantic) and sparse (keyword) vectors
        # For now, using standard similarity search (semantic)
        docs = vectorstore.similarity_search_with_score(question, k=5)
        
        # Extract document content
        documents = [doc[0].page_content for doc in docs]
        state["documents"] = documents
        
        if documents:
            print(f"📚 Retrieved {len(documents)} documents")
        else:
            print("⚠️  No documents retrieved")
            
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        state["documents"] = []
    
    return state


# ============================================================================
# NODE: GENERATOR
# ============================================================================

def generate(state: GraphState) -> GraphState:
    """
    Generate answer based on retrieved documents and question.
    """
    question = state["question"]
    documents = state.get("documents", [])
    loop_step = state.get("loop_step", 0)
    state["loop_step"] = loop_step + 1
    
    # Combine documents into context
    context = "\n\n---\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
    
    system_instruction = """You are a legal research assistant. Answer questions based ONLY on the provided legal documents.

Guidelines:
- Base your answer strictly on the retrieved documents
- Cite specific cases, statutes, or precedents when mentioned in the documents
- If the documents don't contain enough information, say so
- Use clear, professional legal language
- Do not make up facts or citations not present in the documents"""
    
    prompt = f"""Question: {question}

Relevant Legal Documents:
{context if context else "No documents retrieved."}

Please provide a comprehensive answer based on the documents above:"""
    
    response_text = call_gemini(prompt, system_instruction=system_instruction)
    
    state["generation"] = response_text
    print(f"📝 Generated answer (loop step {state['loop_step']})")
    return state


# ============================================================================
# NODE: HALLUCINATION GRADER
# ============================================================================

def grade_hallucination(state: GraphState) -> GraphState:
    """
    Check if the generation is strictly supported by retrieved documents.
    Updates state with grade result.
    """
    generation = state.get("generation", "")
    documents = state.get("documents", [])
    
    if not generation or not documents:
        state["hallucination_grade"] = "fail"
        print("❌ Hallucination check: FAILED (no generation or documents)")
        return state
    
    context = "\n\n---\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
    
    system_instruction = "You are a strict fact-checker. Evaluate if answers are fully supported by provided documents."
    
    grading_prompt = f"""Determine if the following answer is fully supported by the provided documents.

Answer to check:
{generation}

Supporting Documents:
{context}

Evaluate:
- Is EVERY factual claim in the answer directly supported by the documents?
- Are all citations and case names present in the documents?
- Is there any information in the answer that cannot be traced back to the documents?

Respond with ONLY one word: "pass" if fully supported, "fail" if there are unsupported claims or hallucinations.
"""
    
    grade_text = call_gemini(grading_prompt, system_instruction=system_instruction)
    grade = grade_text.lower()
    
    if "pass" in grade:
        state["hallucination_grade"] = "pass"
        print("✅ Hallucination check: PASSED")
    else:
        state["hallucination_grade"] = "fail"
        print("❌ Hallucination check: FAILED - regeneration needed")
    
    return state


# ============================================================================
# NODE: ANSWER GRADER
# ============================================================================

def grade_answer(state: GraphState) -> GraphState:
    """
    Check if the generation answers the user's specific legal question.
    Updates state with grade result.
    """
    question = state.get("question", "")
    generation = state.get("generation", "")
    
    if not generation:
        state["answer_grade"] = "fail"
        print("❌ Answer check: FAILED (no generation)")
        return state
    
    system_instruction = "You are evaluating if answers properly address legal questions."
    
    grading_prompt = f"""Evaluate if an answer properly addresses a legal question.

Original Question:
{question}

Generated Answer:
{generation}

Determine if the answer:
- Directly addresses the specific question asked
- Provides relevant legal information related to the question
- Is sufficiently comprehensive for the question

Respond with ONLY one word: "pass" if the question is answered, "fail" if it doesn't answer the question properly.
"""
    
    grade_text = call_gemini(grading_prompt, system_instruction=system_instruction)
    grade = grade_text.lower()
    
    if "pass" in grade:
        state["answer_grade"] = "pass"
        print("✅ Answer check: PASSED")
    else:
        state["answer_grade"] = "fail"
        print("❌ Answer check: FAILED - query rewrite needed")
    
    return state


# ============================================================================
# DECISION NODES
# ============================================================================

def decide_to_generate(state: GraphState) -> Literal["generate", "end"]:
    """Decide whether to generate or end based on retrieval results."""
    documents = state.get("documents", [])
    loop_step = state.get("loop_step", 0)
    
    if loop_step >= 5:
        print("⚠️  Maximum loop steps reached")
        return "end"
    
    if documents:
        return "generate"
    else:
        # No documents retrieved, still try to generate but might fail
        return "generate"


def decide_after_hallucination_check(state: GraphState) -> Literal["grade_answer", "generate"]:
    """Decide next step after hallucination check."""
    grade = state.get("hallucination_grade", "fail")
    loop_step = state.get("loop_step", 0)
    
    if loop_step >= 5:
        return "grade_answer"  # Even if failed, check answer
    
    if grade == "pass":
        return "grade_answer"
    else:
        return "generate"  # Regenerate


def decide_after_answer_check(state: GraphState) -> Literal["rewrite_query", "end"]:
    """Decide next step after answer check."""
    grade = state.get("answer_grade", "fail")
    rewrite_count = state.get("rewrite_count", 0)
    
    if grade == "pass":
        return "end"  # Success!
    
    if rewrite_count >= 2:
        print("⚠️  Maximum rewrite attempts reached")
        return "end"
    
    return "rewrite_query"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_legal_rag_graph():
    """Build and return the LangGraph workflow."""
    
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("route_question", route_question)
    workflow.add_node("general_answer", general_answer)
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_node("grade_hallucination", grade_hallucination)
    workflow.add_node("grade_answer", grade_answer)
    
    # Set entry point
    workflow.set_entry_point("route_question")
    
    # Route based on question type
    workflow.add_conditional_edges(
        "route_question",
        decide_route,
        {
            "general": "general_answer",
            "retrieval": "retrieve"
        }
    )
    
    # General answer goes to end
    workflow.add_edge("general_answer", END)
    
    # Retrieval path
    workflow.add_conditional_edges(
        "retrieve",
        decide_to_generate,
        {
            "generate": "generate",
            "end": END
        }
    )
    
    # After generation, check for hallucinations
    workflow.add_edge("generate", "grade_hallucination")
    
    # After hallucination check, route based on result
    workflow.add_conditional_edges(
        "grade_hallucination",
        decide_after_hallucination_check,
        {
            "grade_answer": "grade_answer",
            "generate": "generate"  # Regenerate if hallucination detected
        }
    )
    
    # After answer check, route based on result
    workflow.add_conditional_edges(
        "grade_answer",
        decide_after_answer_check,
        {
            "end": END,  # Success!
            "rewrite_query": "rewrite_query"  # Rewrite and try again
        }
    )
    
    # After rewriting, retrieve again
    workflow.add_edge("rewrite_query", "retrieve")
    
    # Compile graph
    app = workflow.compile()
    
    return app


# ============================================================================
# MAIN FUNCTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    app = create_legal_rag_graph()
    
    initial_state = {
        "question": "What is the standard of review for appeals in the First Circuit?",
        "generation": "",
        "documents": [],
        "loop_step": 0,
        "rewrite_count": 0,
        "needs_retrieval": True,
        "hallucination_grade": "",
        "answer_grade": ""
    }
    
    print("🚀 Running LegalMind AI Agentic RAG System\n")
    result = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(result["generation"])
    print("\n" + "="*60)

