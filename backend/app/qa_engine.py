"""
Soru-Cevap (RAG) motoru — Google Gemini ile.

Hibrit arama ile getirilen ilgili doküman parçalarını (chunk) bağlam olarak
Gemini'ye verir ve kullanıcının sorusuna SADECE bu kaynaklara dayanan,
kaynak atıflı bir Türkçe cevap ürettirir.

Ortam değişkeni gereklidir:
    GEMINI_API_KEY=...   (Google AI Studio: https://aistudio.google.com/apikey)
"""

import os
from typing import List, Dict, Tuple

# Cevap üretiminde kullanılacak Gemini modeli (hızlı ve ekonomik)
QA_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = (
    "Sen bir Türkçe doküman soru-cevap asistanısın. "
    "Görevin, kullanıcının sorusunu YALNIZCA sana verilen kaynak metinlere "
    "dayanarak yanıtlamaktır.\n\n"
    "Kurallar:\n"
    "1. Cevabı yalnızca kaynaklardaki bilgilerden üret; dışarıdan bilgi ekleme, uydurma.\n"
    "2. Cevap kaynaklarda yoksa açıkça 'Bu bilgi mevcut dokümanlarda bulunamadı.' de.\n"
    "3. Cevabını Türkçe, kısa ve net yaz.\n"
    "4. Hangi kaynağı kullandıysan cümle sonunda [Kaynak N] biçiminde belirt.\n"
)


class QAUnavailableError(RuntimeError):
    """Cevap üretimi yapılamadığında (ör. anahtar yok) fırlatılır."""


def _build_context(context_chunks: List[Dict]) -> str:
    """Getirilen parçaları numaralı kaynak bloğuna dönüştür."""
    blocks = []
    for i, c in enumerate(context_chunks):
        blocks.append(
            f"[Kaynak {i + 1}] (Başlık: {c['title']}, Kategori: {c['category']})\n"
            f"{c['content']}"
        )
    return "\n\n".join(blocks)


def answer_question(question: str,
                    context_chunks: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Soruyu, verilen parçaları bağlam olarak kullanarak yanıtla.

    Dönüş: (cevap_metni, kullanılan_kaynaklar)
    """
    if not context_chunks:
        return ("Bu bilgi mevcut dokümanlarda bulunamadı.", [])

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise QAUnavailableError(
            "GEMINI_API_KEY ortam değişkeni ayarlı değil. "
            "Cevap üretimi için bir Gemini API anahtarı gereklidir."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise QAUnavailableError(
            "google-genai paketi yüklü değil. 'pip install google-genai' çalıştırın."
        ) from e

    context = _build_context(context_chunks)
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=QA_MODEL,
            contents=f"Kaynaklar:\n{context}\n\nSoru: {question}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1024,
                temperature=0.2,
                # 2.5 modellerinde "düşünme" token'ını kapat — tüm bütçe cevaba gitsin
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception as e:
        raise QAUnavailableError(f"Gemini cevabı üretilemedi: {e}") from e

    answer = (response.text or "").strip()
    if not answer:
        answer = "Bu bilgi mevcut dokümanlarda bulunamadı."

    return answer, context_chunks
