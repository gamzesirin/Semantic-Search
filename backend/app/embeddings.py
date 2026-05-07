import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import os


class EmbeddingModel:
    """Türkçe destekli gömülme modeli yönetimi."""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Model seçenekleri:
        - paraphrase-multilingual-MiniLM-L12-v2 (384 boyut, hızlı, Türkçe destekli)
        - distiluse-base-multilingual-cased-v2 (512 boyut, orta hız)
        """
        print(f"Gömülme modeli yükleniyor: {model_name}...")
        cache_dir = os.path.join(os.path.dirname(__file__), '..', 'model_cache')
        os.makedirs(cache_dir, exist_ok=True)

        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model yüklendi. Boyut: {self.dimension}")

    def encode(self, texts: List[str], batch_size: int = 64,
               show_progress: bool = True) -> np.ndarray:
        """Metinleri vektörlere dönüştür."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True  # Kosinüs benzerliği için normalize et
        )
        return np.array(embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Tek bir sorguyu vektöre dönüştür."""
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )
        return np.array(embedding, dtype=np.float32)
