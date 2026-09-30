from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
import config

# Chatbot imports
from app.chatbot.retrieval.retrieval import ChatbotRetriever
from app.chatbot.llm.answer_generator import AnswerGenerator

# Semantic Search imports
from app.semantic_search.search.semantic_search import SemanticSearchEngine
from app.semantic_search.search.ranking import ResultRanker

router = APIRouter(prefix="/api", tags=["Query"])

class QueryRequest(BaseModel):
    query: str = Field(..., description="User search / question query string.")
    session_id: str = Field(default="default", description="User session identifier.")
    top_k: Optional[int] = Field(default=None, description="Number of top results to retrieve.")

class SourceModel(BaseModel):
    source_num: int
    document: str
    page: Any
    text: str
    doc_id: Optional[str] = ""
    chunk_id: Optional[str] = ""

class ChatbotResponse(BaseModel):
    answer: str
    sources: List[SourceModel]

class SemanticResultModel(BaseModel):
    rank: int
    document: str
    page: Any
    text: str
    score: float

class SemanticSearchResponse(BaseModel):
    results: List[SemanticResultModel]

class UnifiedQueryResponse(BaseModel):
    chatbot: ChatbotResponse
    semantic_search: SemanticSearchResponse

@router.post("/query", response_model=UnifiedQueryResponse)
async def query_systems(payload: QueryRequest):
    """
    Execute unified query across BOTH independent intelligence systems:
    1. Chatbot RAG Pipeline (Returns AI Direct Answer & Document Sources)
    2. Semantic Search Pipeline (Returns Ranked Matching Passages & Scores)
    """
    query_str = payload.query.strip() if payload.query else ""
    if not query_str:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    k = payload.top_k or config.TOP_K
    if k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be a positive integer.")

    # --- PIPELINE 1: CHATBOT RETRIEVAL & ANSWER GENERATION ---
    try:
        retriever = ChatbotRetriever()
        cb_chunks = retriever.retrieve(query=query_str, top_k=k)
        answer_gen = AnswerGenerator()
        answer, sources = answer_gen.generate_answer(query=query_str, retrieved_chunks=cb_chunks)
        chatbot_data = {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        chatbot_data = {
            "answer": f"Error executing AI Chatbot pipeline: {str(e)}",
            "sources": []
        }

    # --- PIPELINE 2: SEMANTIC VECTOR SEARCH & RANKING ---
    try:
        search_engine = SemanticSearchEngine()
        raw_matches = search_engine.search(query=query_str, top_k=k)
        ranked_results = ResultRanker.rank_results(raw_matches)
        semantic_data = {
            "results": ranked_results
        }
    except Exception as e:
        semantic_data = {
            "results": []
        }

    # Return unified response with Chatbot first, Semantic Search second
    return {
        "chatbot": chatbot_data,
        "semantic_search": semantic_data
    }
