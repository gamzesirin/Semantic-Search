# SemanticSearch — Türkçe Doküman Soru-Cevap ve Hibrit Arama Sistemi

Türkçe haber dokümanları üzerinde **parçalama (chunking)**, **hibrit arama** (sözcüksel + anlamsal) ve **yapay zeka ile soru-cevap (RAG)** sunan tam yığın (full-stack) bir uygulama.

Kullanıcı bir soru sorar → sistem dokümanları parçalara ayırıp gömülmelerle indekslemiştir → hibrit arama ile en ilgili parçaları getirir → **Google Gemini** bu parçalara dayanarak kaynak atıflı bir Türkçe cevap üretir.

## Özellikler

Uygulama üç farklı modda çalışır (arayüzde sekmelerle ayrılmıştır):

| Mod             | Ne yapar                                              | Yöntem                                                   |
| --------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| **Soru Sor**    | Soruya dokümanlara dayalı, kaynak atıflı cevap üretir | Hibrit arama (retrieval) + Gemini (generation) = **RAG** |
| **Arama**       | Soruyla en ilgili doküman parçalarını listeler        | BM25 / Vektör / ChromaDB / Hibrit (seçilebilir)          |
| **Karşılaştır** | Aynı sorguyu 3 yöntemle aynı anda çalıştırır          | BM25 + Vektör + Hibrit yan yana                          |

## Mimari

- **Parçalama (chunking):** Dokümanlar cümle bazlı, örtüşmeli parçalara bölünür (`chunker.py`); indeksler bütün doküman yerine **parçalar** üzerine kurulur, her sonuç `doc_id` ile ana dokümana bağlanır.
- **Gömülme:** `sentence-transformers` — `paraphrase-multilingual-MiniLM-L12-v2` (384 boyut, Türkçe destekli, normalize edilmiş)
- **Vektör arama:** FAISS (`IndexFlatIP`, kosinüs) + ChromaDB (HNSW, cosine)
- **Sözcüksel arama:** `rank-bm25` (BM25Okapi) + Türkçe tokenizasyon
- **Hibrit birleştirme:** Reciprocal Rank Fusion (RRF, k=60) — BM25 + FAISS sonuçları üzerinde
- **Soru-Cevap (RAG):** Google Gemini (`gemini-2.5-flash`) — yalnızca getirilen kaynaklara dayanan, `[Kaynak N]` atıflı cevaplar
- **Backend:** FastAPI
- **Frontend:** React 18 + axios
- **Veri:** ~4200 Türkçe haber → ~4400 parça, 7 kategori (Ekonomi, Magazin, Sağlık, Siyaset, Spor, Teknoloji, Yaşam)

## Klasör Yapısı

```
SemanticSearch/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI endpoint'leri (+ .env yükleme)
│   │   ├── search_engine.py     Chunking + BM25 / FAISS / Chroma / Hibrit
│   │   ├── chunker.py           Parçalama stratejileri (cümle / kelime)
│   │   ├── qa_engine.py         Gemini ile RAG cevap üretimi
│   │   ├── embeddings.py        SentenceTransformer sarmalayıcısı
│   │   ├── data_loader.py       CSV yükleme + temizleme
│   │   └── models.py            Pydantic şemaları
│   ├── data/turkish_news.csv    (otomatik indirilir)
│   ├── indexes/                 (otomatik üretilir: embeddings.npy + chroma_db/)
│   ├── .env.example             GEMINI_API_KEY şablonu
│   └── requirements.txt
└── frontend/
    ├── public/index.html
    ├── src/
    │   ├── App.js
    │   ├── components/          ModeTabs, SearchBar, FilterPanel, MetricsDisplay,
    │   │                        SearchResults, ComparisonPanel, AnswerPanel,
    │   │                        ExampleQuestions
    │   └── services/api.js
    └── package.json
```

## Kurulum

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Gemini API anahtarı (Soru Sor modu için gerekli)

[Google AI Studio](https://aistudio.google.com/apikey)'dan ücretsiz bir API anahtarı al, sonra `backend/.env` dosyasını oluştur:

```bash
# backend/.env
GEMINI_API_KEY=.....
# İsteğe bağlı model seçimi:
# GEMINI_MODEL=gemini-2.5-flash
```

> `.env` dosyası `.gitignore`'dadır — anahtarın asla repoya gönderilmez.
> Anahtar olmadan **Arama** ve **Karşılaştır** çalışır; yalnızca **Soru Sor** modu 503 döner.

### 3. Frontend

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

İlk çalıştırmada veri kümesi indirilir, gömülme modeli iner, dokümanlar parçalanır ve indeksler kurulur (~3-5 dakika, CPU). Sonraki çalıştırmalarda her şey önbellekten yüklenir (~30 saniye).

**Terminal 2 — Frontend (port 3000):**

```bash
cd frontend
npm start
```

Tarayıcı `http://localhost:3000` adresinde açılır.

## API Uç Noktaları

| Yöntem | Yol               | Açıklama                                                        |
| ------ | ----------------- | --------------------------------------------------------------- |
| GET    | `/`               | Sağlık kontrolü                                                 |
| GET    | `/api/stats`      | Doküman/parça sayısı, indeks durumu, model bilgisi              |
| GET    | `/api/categories` | Mevcut kategoriler                                              |
| POST   | `/api/search`     | Tek yöntemle arama (`bm25` / `vector` / `chroma` / `hybrid`)    |
| POST   | `/api/compare`    | BM25 + FAISS + Hibrit aynı anda                                 |
| POST   | `/api/ask`        | **Soru-Cevap (RAG):** hibrit arama + Gemini ile dayanaklı cevap |

`/docs` adresinde Swagger arayüzü hazırdır.

### Örnek istekler

Arama:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"merkez bankası faiz kararı","method":"hybrid","top_k":10}'
```

Soru-Cevap:

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Merkez Bankası faiz kararında ne oldu?","top_k":5}'
```

Örnek cevap:

```json
{
	"answer": "Merkez Bankası faiz koridorunun üst bandını çeyrek puan indirerek yüzde 8,50'ye çekti. [Kaynak 1]",
	"sources": [{ "doc_id": 20, "title": "...", "content": "...", "category": "Ekonomi", "score": 0.0325 }],
	"query_time_ms": 2165.5
}
```

## Demo Senaryoları

1. **Soru-Cevap:** _"Merkez Bankası faiz kararında ne oldu?"_ → kaynak atıflı, dokümana dayalı cevap. Arayüzdeki **örnek sorular**a tıklayarak da deneyebilirsin.
2. **Anlamsal vs sözcüksel:** **Arama** modunda `"ekonomik büyüme"` sorgusunu BM25 ve Vektör ile karşılaştır — vektör arama "GSYİH", "milli gelir" gibi anlamca yakınları da yakalar.
3. **Hibrit birleştirme:** **Karşılaştır** modunda `"yapay zeka"` → RRF'in BM25 + vektör listelerini nasıl birleştirdiğini gör.
4. **Kaynak doğrulama:** Soru Sor cevabındaki `[Kaynak N]` atıflarını altta listelenen kaynaklarla karşılaştır — sistem uydurmaz, yalnızca veride olanı söyler.

> Not: Veri kümesi ~2017 dönemi haberlerinden oluşur; güncel olayları değil, veride geçen konuları sor.

## Sorun Giderme

- **`ModuleNotFoundError: No module named 'app'`** — backend'i `backend/` klasöründen çalıştır: `python -m uvicorn app.main:app`.
- **Soru Sor 503 / "GEMINI_API_KEY ayarlı değil"** — `backend/.env` içine geçerli bir anahtar ekle ve backend'i yeniden başlat.
- **Gemini `429 RESOURCE_EXHAUSTED` / kota 0** — anahtarının o model için ücretsiz kotası yok; `.env`'de `GEMINI_MODEL` değerini desteklenen başka bir modelle değiştir (ör. `gemini-2.5-flash`).
- **CORS hatası** — `app/main.py` içindeki `allow_origins` listesinde frontend portu (3000/3001) olmalı.
- **Bellek yetersiz** — `app/main.py` içindeki `search_engine.initialize(max_docs=5000)` değerini düşür.
- **Veri kümesi indirilemedi** — `data_loader.py` otomatik olarak örnek haberlerle devam eder; üretim için `backend/data/turkish_news.csv`'yi manuel ekle.
- **Windows konsolunda kodlama hatası** — backend'i `PYTHONIOENCODING=utf-8` ile başlat.
