# Early Warning System API

RESTful API untuk prediksi risiko keterlambatan pembayaran menggunakan Machine Learning Multi-Level Stacking Ensemble.

## 📁 Struktur Proyek

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & routes
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic validation models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── model_loader.py     # ML model loader
│   │   ├── feature_builder.py  # Feature engineering
│   │   └── predictor.py        # Prediction logic
│   └── utils/
│       ├── __init__.py
│       └── risk_analyzer.py    # Risk categorization
├── models_ews/                 # Directory untuk model files
│   └── Regression_V2/
│       ├── gb_regressor.pkl
│       ├── rf_regressor.pkl
│       ├── meta_ridge.pkl
│       └── model_info.json
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Buat file `.env`:

```env
MODEL_DIR=/path/to/your/models_ews/Regression_V2
```

### 3. Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "models_loaded": true
}
```

### 2. Predict Risk

```http
POST /predict
Content-Type: application/json

{
  "tanggal": "2025-01-15",
  "nominal": 500000,
  "target_type": "broadcast",
  "rt_number": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tanggal": "2025-01-15",
    "nominal": 500000,
    "target_type": "broadcast",
    "rt_number": null,
    "risk_score": 35.42,
    "risk_category": {
      "status": "SEDANG",
      "emoji": "⚠️",
      "rekomendasi": "Risiko sedang. Perlu monitoring berkala.",
      "tindakan": [
        "Monitor pembayaran secara berkala",
        "Kirim reminder H-3 jatuh tempo"
      ]
    }
  }
}
```

### 3. Predict Risk (Verbose)

```http
POST /predict/verbose
```

Sama seperti `/predict` tetapi mengembalikan detail prediksi per level model.

### 4. Models Info

```http
GET /models/info
```

**Response:**
```json
{
  "success": true,
  "data": {
    "level0_models": ["gb", "rf"],
    "level1_models": ["meta_ridge"],
    "total_features": 24,
    "feature_columns": ["Bulan", "Hari", ...]
  }
}
```

## 🔧 Configuration

Edit `app/config.py` untuk mengubah settings:

```python
class Settings(BaseSettings):
    APP_NAME: str = "Early Warning System API"
    APP_VERSION: str = "1.0.0"
    MODEL_DIR: Path = Path("/path/to/models")
    
    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 20.0
    RISK_THRESHOLD_MEDIUM: float = 50.0
    RISK_THRESHOLD_HIGH: float = 75.0
```

## 📊 Risk Categories

| Risk Score | Status | Emoji | Rekomendasi |
|-----------|--------|-------|-------------|
| 0 - 20% | RENDAH | ✅ | Risiko rendah. Transaksi aman. |
| 20 - 50% | SEDANG | ⚠️ | Perlu monitoring berkala. |
| 50 - 75% | TINGGI | 🔴 | Aktifkan reminder & follow-up intensif. |
| 75 - 100% | SANGAT TINGGI | 🚨 | Tunda transaksi & siapkan prosedur penagihan. |

## 🧪 Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Predict (broadcast)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "tanggal": "2025-01-15",
    "nominal": 500000,
    "target_type": "broadcast",
    "rt_number": null
  }'

# Predict (RT tertentu)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "tanggal": "2025-01-15",
    "nominal": 500000,
    "target_type": "rt_tertentu",
    "rt_number": "001"
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/predict"
payload = {
    "tanggal": "2025-01-15",
    "nominal": 500000,
    "target_type": "broadcast",
    "rt_number": None
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Risk Score: {result['data']['risk_score']}%")
print(f"Status: {result['data']['risk_category']['status']}")
```

### Using JavaScript (Fetch)

```javascript
const url = "http://localhost:8000/predict";
const payload = {
  tanggal: "2025-01-15",
  nominal: 500000,
  target_type: "broadcast",
  rt_number: null
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log("Risk Score:", data.data.risk_score);
    console.log("Status:", data.data.risk_category.status);
  });
```

## 🔐 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t ews-api .
docker run -p 8000:8000 -v /path/to/models:/models ews-api
```
