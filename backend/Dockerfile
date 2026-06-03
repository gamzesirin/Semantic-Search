# Backend (FastAPI + ML) için Docker imajı — Dokploy bununla build eder.
FROM python:3.12-slim

WORKDIR /app

# hnswlib/chromadb gibi bazı paketler derleme gerektirebilir → derleyici kur.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Önce sadece requirements'ı kopyala (Docker katman önbelleği için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

EXPOSE 8000

# Tek worker: model + indeksler belleğe bir kez yüklensin (çok worker = OOM riski).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
