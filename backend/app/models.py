from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str
    method: str = "hybrid"  # "bm25", "vector", "hybrid"
    top_k: int = 10
    similarity_threshold: float = 0.2
    category: Optional[str] = None


class SearchResult(BaseModel):
    id: int            # parça (chunk) kimliği
    doc_id: int = 0    # ait olduğu dokümanın kimliği
    title: str
    content: str
    category: str
    score: float
    method: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query_time_ms: float
    total_found: int
    method: str


class ComparisonRequest(BaseModel):
    query: str
    top_k: int = 10
    similarity_threshold: float = 0.2
    category: Optional[str] = None


class ComparisonResponse(BaseModel):
    bm25: SearchResponse
    vector: SearchResponse
    hybrid: SearchResponse


class StatsResponse(BaseModel):
    total_documents: int
    categories: List[str]
    index_status: dict


# ===== Soru-Cevap (RAG) şemaları =====

class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    category: Optional[str] = None


class AskSource(BaseModel):
    doc_id: int
    title: str
    content: str
    category: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: List[AskSource]
    query_time_ms: float
