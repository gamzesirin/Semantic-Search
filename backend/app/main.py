from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models import (
    SearchRequest, SearchResponse, SearchResult,
    ComparisonRequest, ComparisonResponse, StatsResponse
)
from app.search_engine import SearchEngine


# Global arama motoru
search_engine = SearchEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatıldığında arama motorunu başlat."""
    search_engine.initialize(max_docs=5000)
    yield
    print("Uygulama kapatılıyor...")


app = FastAPI(
    title="SemanticSearch API",
    description="Türkçe Hibrit Doküman Arama Sistemi — BM25, FAISS, ChromaDB ve RRF Hibrit Arama",
    version="1.0.0",
    lifespan=lifespan
)

# CORS ayarları (React frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "SemanticSearch API çalışıyor", "status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Tek yöntemle arama yap."""
    if not search_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Arama motoru henüz başlatılmadı")

    try:
        results, query_time = search_engine.search(
            query=request.query,
            method=request.method,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            category=request.category
        )

        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            query_time_ms=query_time,
            total_found=len(results),
            method=request.method
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare", response_model=ComparisonResponse)
async def compare(request: ComparisonRequest):
    """Üç yöntemle aynı anda arama yap ve karşılaştır."""
    if not search_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Arama motoru henüz başlatılmadı")

    try:
        # BM25
        bm25_results, bm25_time = search_engine.search_bm25(
            request.query, request.top_k, request.category
        )
        # FAISS (Vektör)
        faiss_results, faiss_time = search_engine.search_faiss(
            request.query, request.top_k, request.similarity_threshold, request.category
        )
        # Hibrit (RRF)
        hybrid_results, hybrid_time = search_engine.search_hybrid(
            request.query, request.top_k, request.similarity_threshold, request.category
        )

        return ComparisonResponse(
            bm25=SearchResponse(
                results=[SearchResult(**r) for r in bm25_results],
                query_time_ms=bm25_time,
                total_found=len(bm25_results),
                method="bm25"
            ),
            vector=SearchResponse(
                results=[SearchResult(**r) for r in faiss_results],
                query_time_ms=faiss_time,
                total_found=len(faiss_results),
                method="vector"
            ),
            hybrid=SearchResponse(
                results=[SearchResult(**r) for r in hybrid_results],
                query_time_ms=hybrid_time,
                total_found=len(hybrid_results),
                method="hybrid"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    """Sistem istatistiklerini döndür."""
    if not search_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Arama motoru henüz başlatılmadı")

    stats_data = search_engine.get_stats()
    return StatsResponse(**stats_data)


@app.get("/api/categories")
async def categories():
    """Mevcut kategorileri döndür."""
    if not search_engine.is_initialized:
        raise HTTPException(status_code=503, detail="Arama motoru henüz başlatılmadı")

    return {"categories": search_engine.categories}
