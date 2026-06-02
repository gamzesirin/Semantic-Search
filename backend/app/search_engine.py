import numpy as np
import pandas as pd
import faiss
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional, Tuple
import time
import os
import re

from app.embeddings import EmbeddingModel
from app.data_loader import load_and_prepare_data
from app.chunker import chunk_document


class SearchEngine:
    """BM25, FAISS, ChromaDB ve Hibrit arama motorlarını yöneten sınıf.

    İndeksler doküman değil, doküman PARÇALARI (chunk) üzerine kurulur.
    Her arama sonucu, ait olduğu dokümana `doc_id` ile bağlanır.
    """

    # Parçalama ayarları (cümle bazlı, örtüşmeli)
    CHUNK_STRATEGY = "sentence"
    CHUNK_KWARGS = {"sentences_per_chunk": 2, "overlap": 1}

    def __init__(self):
        self.documents = None       # Ana dokümanlar (referans/gösterim)
        self.chunks = None          # Parçalar (indekslenen birim)
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
        print("\n[1/6] Veri yükleniyor...")
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.documents = load_and_prepare_data(data_dir, max_docs=max_docs)
        self.categories = sorted(self.documents['category'].unique().tolist())

        # 2. Dokümanları parçalara böl (chunking)
        print("\n[2/6] Dokümanlar parçalara bölünüyor (chunking)...")
        self._build_chunks()

        # 3. Gömülme modeli yükle
        print("\n[3/6] Gömülme modeli yükleniyor...")
        self.embedding_model = EmbeddingModel()

        # 4. Gömülmeleri oluştur veya yükle (parçalar üzerinden)
        print("\n[4/6] Gömülmeler oluşturuluyor...")
        embeddings = self._get_or_create_embeddings()

        # 5. Vektör indekslerini oluştur
        print("\n[5/6] FAISS ve ChromaDB indeksleri oluşturuluyor...")
        self._build_faiss_index(embeddings)
        self._build_chroma_collection(embeddings)

        # 6. BM25 indeksi oluştur
        print("\n[6/6] BM25 indeksi oluşturuluyor...")
        self._build_bm25_index()

        self.is_initialized = True
        print("\n" + "=" * 60)
        print(f"Başlatma tamamlandı! {len(self.documents)} doküman, "
              f"{len(self.chunks)} parça indekslendi.")
        print(f"Kategoriler: {self.categories}")
        print("=" * 60)

    def _build_chunks(self):
        """Her dokümanı parçalara böl ve düz bir parça tablosu oluştur."""
        rows = []
        chunk_id = 0
        for _, doc in self.documents.iterrows():
            pieces = chunk_document(
                doc['content'],
                strategy=self.CHUNK_STRATEGY,
                **self.CHUNK_KWARGS,
            )
            if not pieces:
                pieces = [str(doc['content'])]
            for piece in pieces:
                rows.append({
                    "chunk_id": chunk_id,
                    "doc_id": int(doc['id']),
                    "title": doc['title'],
                    "category": doc['category'],
                    "chunk_text": piece,
                })
                chunk_id += 1

        self.chunks = pd.DataFrame(rows).reset_index(drop=True)
        avg = len(self.chunks) / max(1, len(self.documents))
        print(f"{len(self.documents)} dokuman -> {len(self.chunks)} parca "
              f"(dokuman basina ort. {avg:.1f} parca)")

    def _chunk_texts(self) -> List[str]:
        """Gömülme/indeks için parça metinleri (başlık + parça birleşik)."""
        return (self.chunks['title'] + ". " + self.chunks['chunk_text']).tolist()

    def _get_or_create_embeddings(self) -> np.ndarray:
        """Gömülmeleri dosyadan yükle veya yeniden oluştur."""
        index_dir = os.path.join(os.path.dirname(__file__), '..', 'indexes')
        os.makedirs(index_dir, exist_ok=True)
        embeddings_path = os.path.join(index_dir, 'embeddings.npy')

        if os.path.exists(embeddings_path):
            print("Kaydedilmiş gömülmeler yükleniyor...")
            embeddings = np.load(embeddings_path)
            if len(embeddings) == len(self.chunks):
                print(f"Yüklendi: {embeddings.shape}")
                return embeddings
            print("Parça sayısı uyumsuz, gömülmeler yeniden oluşturuluyor...")

        # Başlık + parça birleştirerek gömülme oluştur
        texts = self._chunk_texts()
        embeddings = self.embedding_model.encode(texts)

        np.save(embeddings_path, embeddings)
        print(f"Gömülmeler kaydedildi: {embeddings.shape}")

        return embeddings

    def _build_faiss_index(self, embeddings: np.ndarray):
        """FAISS indeksi oluştur (parçalar üzerine)."""
        dimension = embeddings.shape[1]

        # Düz (Flat) indeks — tam arama, en doğru sonuç
        # Küçük veri kümelerinde (<50K) IVF'ye gerek yok
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product (normalize = kosinüs)
        self.faiss_index.add(embeddings)

        print(f"FAISS indeksi oluşturuldu: {self.faiss_index.ntotal} vektör, {dimension} boyut")

    def _build_chroma_collection(self, embeddings: np.ndarray):
        """ChromaDB koleksiyonu oluştur (parçalar üzerine)."""
        chroma_dir = os.path.join(os.path.dirname(__file__), '..', 'indexes', 'chroma_db')
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

        # Parçaları ekle (ChromaDB batch limiti ~41666)
        batch_size = 5000
        for i in range(0, len(self.chunks), batch_size):
            end_idx = min(i + batch_size, len(self.chunks))
            batch_df = self.chunks.iloc[i:end_idx]
            batch_embeddings = embeddings[i:end_idx]

            self.chroma_collection.add(
                ids=[str(cid) for cid in batch_df['chunk_id'].tolist()],
                embeddings=batch_embeddings.tolist(),
                documents=(batch_df['title'] + ". " + batch_df['chunk_text']).tolist(),
                metadatas=[
                    {"title": row['title'], "category": row['category'],
                     "doc_id": int(row['doc_id'])}
                    for _, row in batch_df.iterrows()
                ]
            )

        print(f"ChromaDB koleksiyonu oluşturuldu: {self.chroma_collection.count()} parça")

    def _build_bm25_index(self):
        """BM25 indeksi oluştur (parçalar üzerine)."""
        corpus = (self.chunks['title'] + " " + self.chunks['chunk_text']).tolist()
        tokenized_corpus = [self._tokenize_turkish(doc) for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"BM25 indeksi oluşturuldu: {len(tokenized_corpus)} parça")

    def _tokenize_turkish(self, text: str) -> List[str]:
        """Basit Türkçe tokenizasyon."""
        text = text.lower()
        # Türkçe karakterleri koru, noktalama işaretlerini kaldır
        text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', ' ', text)
        tokens = text.split()
        # Çok kısa kelimeleri filtrele
        tokens = [t for t in tokens if len(t) > 1]
        return tokens

    def _format_result(self, row, score: float, method: str) -> Dict:
        """Bir parça satırını API sonucu sözlüğüne dönüştür."""
        content = str(row['chunk_text'])
        if len(content) > 300:
            content = content[:300] + "..."
        return {
            "id": int(row['chunk_id']),
            "doc_id": int(row['doc_id']),
            "title": row['title'],
            "content": content,
            "category": row['category'],
            "score": round(float(score), 4),
            "method": method,
        }

    def search_bm25(self, query: str, top_k: int = 10,
                    category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """BM25 ile sözcüksel arama (parçalar üzerinde)."""
        start_time = time.time()

        tokenized_query = self._tokenize_turkish(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Kategori filtresi (vektörel maskeleme — hızlı)
        if category and category != "all":
            mask = self.chunks['category'].values != category
            scores[mask] = 0.0

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                row = self.chunks.iloc[idx]
                results.append(self._format_result(row, scores[idx], "bm25"))

        query_time = (time.time() - start_time) * 1000
        return results, round(query_time, 2)

    def search_faiss(self, query: str, top_k: int = 10,
                     similarity_threshold: float = 0.0,
                     category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """FAISS ile vektör araması (parçalar üzerinde)."""
        start_time = time.time()

        query_vector = self.embedding_model.encode_query(query)

        # Kategori filtresi varsa daha fazla aday çek
        search_k = top_k * 4 if category and category != "all" else top_k
        scores, indices = self.faiss_index.search(query_vector, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            if float(score) < similarity_threshold:
                continue

            row = self.chunks.iloc[idx]
            if category and category != "all" and row['category'] != category:
                continue

            results.append(self._format_result(row, score, "faiss"))
            if len(results) >= top_k:
                break

        query_time = (time.time() - start_time) * 1000
        return results, round(query_time, 2)

    def search_chroma(self, query: str, top_k: int = 10,
                      similarity_threshold: float = 0.0,
                      category: Optional[str] = None) -> Tuple[List[Dict], float]:
        """ChromaDB ile vektör araması (parçalar üzerinde)."""
        start_time = time.time()

        query_vector = self.embedding_model.encode_query(query)

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
            for i, chunk_id in enumerate(chroma_results['ids'][0]):
                distance = chroma_results['distances'][0][i] if chroma_results['distances'] else 0
                # ChromaDB kosinüs mesafesi döndürür, benzerliğe çevir
                similarity = 1 - distance

                if similarity < similarity_threshold:
                    continue

                idx = int(chunk_id)
                if idx < len(self.chunks):
                    row = self.chunks.iloc[idx]
                    results.append(self._format_result(row, similarity, "chroma"))

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

        # Her iki yöntemle ara (parça bazında)
        bm25_results, _ = self.search_bm25(query, top_k=top_k * 2, category=category)
        faiss_results, _ = self.search_faiss(query, top_k=top_k * 2,
                                             similarity_threshold=similarity_threshold,
                                             category=category)

        # RRF birleştirme (k=60, standart değer) — parça id'si üzerinden
        k = 60
        rrf_scores = {}

        for rank, result in enumerate(bm25_results):
            cid = result['id']
            rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)

        for rank, result in enumerate(faiss_results):
            cid = result['id']
            rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)

        all_results = {}
        for result in bm25_results + faiss_results:
            if result['id'] not in all_results:
                all_results[result['id']] = result

        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        results = []
        for cid in sorted_ids[:top_k]:
            if cid in all_results:
                result = all_results[cid].copy()
                result['score'] = round(rrf_scores[cid], 4)
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
                "total_chunks": len(self.chunks) if self.chunks is not None else 0,
                "bm25": self.bm25 is not None,
                "faiss": self.faiss_index is not None,
                "faiss_vectors": self.faiss_index.ntotal if self.faiss_index else 0,
                "chroma": self.chroma_collection is not None,
                "chroma_count": self.chroma_collection.count() if self.chroma_collection else 0,
                "embedding_model": self.embedding_model.model_name if self.embedding_model else None,
                "embedding_dimension": self.embedding_model.dimension if self.embedding_model else None,
            }
        }
