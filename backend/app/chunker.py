"""
Doküman parçalama (chunking) stratejileri.

Büyük dokümanları anlamsal aramaya uygun küçük, örtüşmeli parçalara böler.
İki strateji desteklenir:
  - "sentence": cümle bazlı (kısa haber/metinler için ideal)
  - "word":     sabit kelime penceresi bazlı (uzun dokümanlar için ideal)

Örtüşme (overlap), bir parçanın sonundaki bağlamın bir sonraki parçada da
yer almasını sağlar; böylece cümle/paragraf sınırına denk gelen cevaplar kaybolmaz.
"""

import re
from typing import List


def split_sentences(text: str) -> List[str]:
    """Metni cümlelere ayır (basit, Türkçe uyumlu)."""
    if not text:
        return []
    # Nokta, ünlem, soru işaretinden sonra gelen boşlukta böl
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_by_sentences(text: str, sentences_per_chunk: int = 2,
                       overlap: int = 1) -> List[str]:
    """Cümle bazlı, örtüşmeli parçalama."""
    sents = split_sentences(text)
    if not sents:
        return []
    if len(sents) <= sentences_per_chunk:
        return [" ".join(sents)]

    chunks = []
    step = max(1, sentences_per_chunk - overlap)
    i = 0
    while i < len(sents):
        chunk = " ".join(sents[i:i + sentences_per_chunk]).strip()
        if chunk:
            chunks.append(chunk)
        if i + sentences_per_chunk >= len(sents):
            break
        i += step
    return chunks


def chunk_by_words(text: str, chunk_size: int = 200,
                   overlap: int = 50) -> List[str]:
    """Sabit kelime penceresi bazlı, örtüşmeli parçalama."""
    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_size:
        return [text.strip()]

    chunks = []
    step = max(1, chunk_size - overlap)
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
        i += step
    return chunks


def chunk_document(text: str, strategy: str = "sentence", **kwargs) -> List[str]:
    """
    Seçilen stratejiye göre metni parçalara böl.

    strategy="sentence" -> sentences_per_chunk, overlap
    strategy="word"     -> chunk_size, overlap
    """
    if not isinstance(text, str) or not text.strip():
        return []

    if strategy == "sentence":
        return chunk_by_sentences(text, **kwargs)
    elif strategy == "word":
        return chunk_by_words(text, **kwargs)
    else:
        raise ValueError(f"Bilinmeyen parçalama stratejisi: {strategy}")
