import numpy as np
import faiss
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional, Tuple
import time
import os
import re

from app.embeddings import EmbeddingModel
from app.data_loader import load_and_prepare_data


class SearchEngine:
    """BM25, FAISS, ChromaDB ve Hibrit arama motorlarını yöneten sınıf."""

    def __init__(self):
        self.documents = None
        self.embedding_model = None
        self.bm25 = None
        self.faiss_index = None
        self.chroma_collection = None
        self.is_initialized = False
        self.categories = []

    def initialize(self, max_docs: int = 5000):
        """Tüm arama motorlarını başlat."""
        print("=" * 60)
        print("SemanticSearch Başlatılıyor...")
        print("=" * 60)

        # 1. Veri yükle
        print("\n[1/5] Veri yükleniyor...")
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.documents = load_and_prepare_data(data_dir, max_docs=max_docs)
        self.categories = sorted(self.documents['category'].unique().tolist())

        # 2. Gömülme modeli yükle
        print("\n[2/5] Gömülme modeli yükleniyor...")
        self.embedding_model = EmbeddingModel()

        # 3. Gömülmeleri oluştur veya yükle
        print("\n[3/5] Gömülmeler oluşturuluyor...")
        embeddings = self._get_or_create_embeddings()

        # 4. İndeksleri oluştur
        print("\n[4/5] FAISS indeksi oluşturuluyor...")
        self._build_faiss_index(embeddings)

        print("\n[5/5] ChromaDB koleksiyonu oluşturuluyor...")
        self._build_chroma_collection(embeddings)

        # BM25 indeksi oluştur
        print("\nBM25 indeksi oluşturuluyor...")
        self._build_bm25_index()

        self.is_initialized = True
        print("\n" + "=" * 60)
        print(f"Başlatma tamamlandı! {len(self.documents)} doküman indekslendi.")
        print(f"Kategoriler: {self.categories}")
        print("=" * 60)

    def _get_or_create_embeddings(self) -> np.ndarray:
        """Gömülmeleri dosyadan yükle veya yeniden oluştur."""
        index_dir = os.path.join(os.path.dirname(__file__), '..', 'indexes')
        os.makedirs(index_dir, exist_ok=True)
        embeddings_path = os.path.join(index_dir, 'embeddings.npy')

        if os.path.exists(embeddings_path):
            print("Kaydedilmiş gömülmeler yükleniyor...")
            embeddings = np.load(embeddings_path)
            if len(embeddings) == len(self.documents):
                print(f"Yüklendi: {embeddings.shape}")
                return embeddings
            print("Boyut uyumsuz, yeniden oluşturuluyor...")

        # Başlık + içerik birleştirerek gömülme oluştur
        texts = (self.documents['title'] + ". " + self.documents['content']).tolist()
        embeddings = self.embedding_model.encode(texts)

        # Kaydet
        np.save(embeddings_path, embeddings)
        print(f"Gömülmeler kaydedildi: {embeddings.shape}")

        return embeddings

    def _build_faiss_index(self, embeddings: np.ndarray):
        """FAISS indeksi oluştur."""
        dimension = embeddings.shape[1]

        # Düz (Flat) indeks — tam arama, en doğru sonuç
        # Küçük veri kümelerinde (<50K) IVF'ye gerek yok
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product (normalize edilmiş = kosinüs)
        self.faiss_index.add(embeddings)

        print(f"FAISS indeksi oluşturuldu: {self.faiss_index.ntotal} vektör, {dimension} boyut")

    def _build_chroma_collection(self, embeddings: np.ndarray):
        """ChromaDB koleksiyonu oluştur."""
        chroma_dir = os.path.join(os.path.dirname(__file__), '..', 'indexes', 'chroma_db')

        # Önceki koleksiyonu temizle
        client = chromadb.PersistentClient(path=chroma_dir)

        # Varsa sil, yeniden oluştur
        try:
            client.delete_collection("turkish_news")
        except Exception:
            pass

        self.chroma_collection = client.create_collection(
            name="turkish_news",
            metadata={"hnsw:space": "cosine"}
        )

        # Dokümanları ekle (ChromaDB batch limiti 41666)
        batch_size = 5000
        for i in range(0, len(self.documents), batch_size):
            end_idx = min(i + batch_size, len(self.documents))
            batch_df = self.documents.iloc[i:end_idx]
            batch_embeddings = embeddings[i:end_idx]

            self.chroma_collection.add(
                ids=[str(idx) for idx in batch_df['id'].tolist()],
                embeddings=batch_embeddings.tolist(),
                documents=(batch_df['title'] + ". " + batch_df['content']).tolist(),
                metadatas=[
                    {"title": row['title'], "category": row['category']}
                    for _, row in batch_df.iterrows()
                ]
            )

        print(f"ChromaDB koleksiyonu oluşturuldu: {self.chroma_collection.count()} doküman")

    def _build_bm25_index(self):
        """BM25 indeksi oluştur."""
        # Basit tokenizasyon (Türkçe için)
        corpus = (self.documents['title'] + " " + self.documents['content']).tolist()
        tokenized_corpus = [self._tokenize_turkish(doc) for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"BM25 indeksi oluşturuldu: {len(tokenized_corpus)} doküman")

    def _tokenize_turkish(self, text: str) -> List[str]:
        """Basit Türkçe tokenizasyon."""
        text = text.lower()
        # Türkçe karakterleri koru, noktalama işaretlerini kaldır
        text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', ' ', text)
        tokens = text.split()
        # Çok kısa kelimeleri filtrele
        tokens = [t for t in tokens if len(t) > 1]
        return tokens

    def search_bm25(self, query: str, top_k: int = 10,
                    category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """BM25 ile sözcüksel arama."""
        start_time = time.time()

        tokenized_query = self._tokenize_turkish(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Kategori filtresi
        if category and category != "all":
            for i, row in self.documents.iterrows():
                if row['category'] != category:
                    scores[i] = 0.0

        # En yüksek skorlu dokümanları bul
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                row = self.documents.iloc[idx]
                results.append({
                    "id": int(row['id']),
                    "title": row['title'],
                    "content": row['content'][:300] + "..." if len(row['content']) > 300 else row['content'],
                    "category": row['category'],
                    "score": round(float(scores[idx]), 4),
                    "method": "bm25"
                })

        query_time = (time.time() - start_time) * 1000  # ms
        return results, round(query_time, 2)

    def search_faiss(self, query: str, top_k: int = 10,
                     similarity_threshold: float = 0.0,
                     category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """FAISS ile vektör araması."""
        start_time = time.time()

        # Sorguyu vektöre çevir
        query_vector = self.embedding_model.encode_query(query)

        # FAISS'te ara
        search_k = top_k * 3 if category and category != "all" else top_k
        scores, indices = self.faiss_index.search(query_vector, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            if float(score) < similarity_threshold:
                continue

            row = self.documents.iloc[idx]

            # Kategori filtresi
            if category and category != "all" and row['category'] != category:
                continue

            results.append({
                "id": int(row['id']),
                "title": row['title'],
                "content": row['content'][:300] + "..." if len(row['content']) > 300 else row['content'],
                "category": row['category'],
                "score": round(float(score), 4),
                "method": "faiss"
            })

            if len(results) >= top_k:
                break

        query_time = (time.time() - start_time) * 1000
        return results, round(query_time, 2)

    def search_chroma(self, query: str, top_k: int = 10,
                      similarity_threshold: float = 0.0,
                      category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """ChromaDB ile vektör araması."""
        start_time = time.time()

        # Sorguyu vektöre çevir
        query_vector = self.embedding_model.encode_query(query)

        # ChromaDB'de ara
        where_filter = None
        if category and category != "all":
            where_filter = {"category": category}

        chroma_results = self.chroma_collection.query(
            query_embeddings=query_vector.tolist(),
            n_results=top_k,
            where=where_filter
        )

        results = []
        if chroma_results and chroma_results['ids'] and chroma_results['ids'][0]:
            for i, doc_id in enumerate(chroma_results['ids'][0]):
                distance = chroma_results['distances'][0][i] if chroma_results['distances'] else 0
                # ChromaDB kosinüs mesafesi döndürür, benzerliğe çevir
                similarity = 1 - distance

                if similarity < similarity_threshold:
                    continue

                idx = int(doc_id)
                if idx < len(self.documents):
                    row = self.documents.iloc[idx]
                    results.append({
                        "id": int(row['id']),
                        "title": row['title'],
                        "content": row['content'][:300] + "..." if len(row['content']) > 300 else row['content'],
                        "category": row['category'],
                        "score": round(float(similarity), 4),
                        "method": "chroma"
                    })

        query_time = (time.time() - start_time) * 1000
        return results, round(query_time, 2)

    def search_hybrid(self, query: str, top_k: int = 10,
                      similarity_threshold: float = 0.0,
                      category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """
        Hibrit arama: BM25 + FAISS sonuçlarını RRF ile birleştir.
        RRF (Reciprocal Rank Fusion): score = sum(1 / (k + rank))
        """
        start_time = time.time()

        # Her iki yöntemle ara
        bm25_results, _ = self.search_bm25(query, top_k=top_k * 2, category=category)
        faiss_results, _ = self.search_faiss(query, top_k=top_k * 2,
                                             similarity_threshold=similarity_threshold,
                                             category=category)

        # RRF birleştirme (k=60, standart değer)
        k = 60
        rrf_scores = {}

        for rank, result in enumerate(bm25_results):
            doc_id = result['id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

        for rank, result in enumerate(faiss_results):
            doc_id = result['id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

        # Tüm sonuçları bir sözlüğe topla
        all_results = {}
        for result in bm25_results + faiss_results:
            if result['id'] not in all_results:
                all_results[result['id']] = result

        # RRF skorlarına göre sırala
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        results = []
        for doc_id in sorted_ids[:top_k]:
            if doc_id in all_results:
                result = all_results[doc_id].copy()
                result['score'] = round(rrf_scores[doc_id], 4)
                result['method'] = 'hybrid'
                results.append(result)

        query_time = (time.time() - start_time) * 1000
        return results, round(query_time, 2)

    def search(self, query: str, method: str = "hybrid", top_k: int = 10,
               similarity_threshold: float = 0.0,
               category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """Genel arama fonksiyonu."""
        if method == "bm25":
            return self.search_bm25(query, top_k, category)
        elif method == "vector" or method == "faiss":
            return self.search_faiss(query, top_k, similarity_threshold, category)
        elif method == "chroma":
            return self.search_chroma(query, top_k, similarity_threshold, category)
        elif method == "hybrid":
            return self.search_hybrid(query, top_k, similarity_threshold, category)
        else:
            raise ValueError(f"Bilinmeyen arama yöntemi: {method}")

    def get_stats(self) -> dict:
        """Sistem istatistiklerini döndür."""
        return {
            "total_documents": len(self.documents) if self.documents is not None else 0,
            "categories": self.categories,
            "index_status": {
                "bm25": self.bm25 is not None,
                "faiss": self.faiss_index is not None,
                "faiss_vectors": self.faiss_index.ntotal if self.faiss_index else 0,
                "chroma": self.chroma_collection is not None,
                "chroma_count": self.chroma_collection.count() if self.chroma_collection else 0,
                "embedding_model": self.embedding_model.model_name if self.embedding_model else None,
                "embedding_dimension": self.embedding_model.dimension if self.embedding_model else None,
            }
        }
