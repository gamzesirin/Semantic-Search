"""
Veri kümesini indirir, gömülmeleri hesaplar ve indeksleri kurar.

Sunucuyu çalıştırmadan önce tüm ağır işleri (veri indirme, embedding,
FAISS, ChromaDB) bir kerede yapmak için kullanın:

    cd backend
    venv\\Scripts\\activate           # Windows
    source venv/bin/activate         # Mac/Linux
    python setup_data.py [--max-docs 5000]

Bu adımdan sonra `python -m uvicorn app.main:app` çalıştırıldığında
her şey önbellekten yüklenir (~30 saniye).
"""

import argparse
import os
import sys

# backend/ klasörünü import yoluna ekle (script doğrudan çalıştırıldığında)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.search_engine import SearchEngine


def main():
    parser = argparse.ArgumentParser(description="SemanticSearch veri ve indeks hazırlama")
    parser.add_argument(
        "--max-docs",
        type=int,
        default=5000,
        help="İndekslenecek maksimum doküman sayısı (varsayılan: 5000)",
    )
    args = parser.parse_args()

    engine = SearchEngine()
    engine.initialize(max_docs=args.max_docs)

    stats = engine.get_stats()
    print("\n" + "=" * 60)
    print("HAZIRLIK TAMAMLANDI")
    print("=" * 60)
    print(f"Toplam doküman      : {stats['total_documents']}")
    print(f"Kategoriler         : {', '.join(stats['categories'])}")
    print(f"Embedding modeli    : {stats['index_status']['embedding_model']}")
    print(f"Embedding boyutu    : {stats['index_status']['embedding_dimension']}")
    print(f"FAISS vektörleri    : {stats['index_status']['faiss_vectors']}")
    print(f"ChromaDB dokümanlar : {stats['index_status']['chroma_count']}")
    print("\nArtık `python -m uvicorn app.main:app --reload` ile sunucuyu başlatabilirsiniz.")


if __name__ == "__main__":
    main()
