# SemanticSearch — Türkçe Hibrit Doküman Arama Sistemi

BM25 (sözcüksel) + FAISS / ChromaDB (anlamsal) + RRF (hibrit) ile Türkçe haber arama.

## Mimari

- **Backend:** FastAPI + sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`, 384 boyut) + FAISS (IndexFlatIP) + ChromaDB (HNSW, cosine) + rank-bm25
- **Frontend:** React 18 + axios
- **Veri:** ~4200 Türkçe haber, 7 kategori (Ekonomi, Magazin, Sağlık, Siyaset, Spor, Teknoloji, Yaşam)
- **Hibrit birleştirme:** Reciprocal Rank Fusion (k=60), BM25 + FAISS sonuçları üzerinde

## Klasör Yapısı

```
SemanticSearch/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI endpoint'leri
│   │   ├── search_engine.py     BM25 / FAISS / Chroma / Hibrit
│   │   ├── embeddings.py        SentenceTransformer sarmalayıcısı
│   │   ├── data_loader.py       CSV yükleme + temizleme
│   │   └── models.py            Pydantic şemaları
│   ├── data/turkish_news.csv    (otomatik indirilir)
│   ├── indexes/                 (otomatik üretilir: embeddings.npy + chroma_db/)
│   └── requirements.txt
└── frontend/
    ├── public/index.html
    ├── src/
    │   ├── App.js
    │   ├── components/          SearchBar, FilterPanel, MetricsDisplay,
    │   │                        SearchResults, ComparisonPanel
    │   └── services/api.js
    └── package.json
```

## Kurulum

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Çalıştırma

İki terminal gerekir.

**Terminal 1 — Backend (port 8000):**

```bash
cd backend
venv\Scripts\activate            # Windows
python -m uvicorn app.main:app --reload --port 8000
```

İlk çalıştırmada veri kümesi indirilir, gömülmeler hesaplanır ve indeksler kurulur (~3-5 dakika, CPU). Sonraki çalıştırmalarda her şey önbellekten yüklenir (~30 saniye).

**Terminal 2 — Frontend (port 3000):**

```bash
cd frontend
npm start
```

Tarayıcı `http://localhost:3000` adresinde açılır.

## API Uç Noktaları

| Yöntem | Yol | Açıklama |
|---|---|---|
| GET  | `/`              | Sağlık kontrolü |
| GET  | `/api/stats`     | Doküman sayısı, indeks durumu, model bilgisi |
| GET  | `/api/categories`| Mevcut kategoriler |
| POST | `/api/search`    | Tek yöntemle arama (`bm25` / `vector` / `chroma` / `hybrid`) |
| POST | `/api/compare`   | BM25 + FAISS + Hibrit aynı anda |

`/docs` adresinde Swagger arayüzü hazırdır.

### Örnek istek

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"merkez bankası faiz kararı","method":"hybrid","top_k":10}'
```

## Demo Senaryoları

1. **Anlamsal vs sözcüksel:** `"ekonomik büyüme"` sorgusunu BM25 ve vektör modunda karşılaştır — vektör arama "GSYİH", "milli gelir" gibi eşanlamlıları da yakalar.
2. **Hibrit birleştirme:** `"yapay zeka eğitim"` için **3 Yöntemle Karşılaştır** butonu — RRF'in iki listeyi nasıl birleştirdiği görülür.
3. **Kategori filtresi:** Aynı sorguyu farklı kategorilerle çalıştırarak filtrelemenin etkisini gör.
4. **Eşik etkisi:** Benzerlik eşiğini 0.1 → 0.7 arasında değiştirerek hassasiyet/kapsam ödünleşimini gözlemle.

## Sorun Giderme

- **`ModuleNotFoundError: No module named 'app'`** — backend'i `backend/` klasöründen çalıştır: `python -m uvicorn app.main:app`.
- **CORS hatası** — `app/main.py` içindeki `allow_origins` listesinde frontend portu (3000/3001) olmalı.
- **Bellek yetersiz** — `app/main.py` içindeki `search_engine.initialize(max_docs=5000)` değerini düşür.
- **Veri kümesi indirilemedi** — `data_loader.py` otomatik olarak 20 örnek haberle devam eder; üretim için `backend/data/turkish_news.csv`'yi manuel ekle.
