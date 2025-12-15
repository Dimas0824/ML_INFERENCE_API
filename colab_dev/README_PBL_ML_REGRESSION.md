# PBL ML Regression Risk - Sistem Prediksi Keterlambatan Pembayaran

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

## Daftar Isi

- [Ringkasan](#ringkasan)
- [Fitur](#fitur)
- [Struktur Proyek](#struktur-proyek)
- [Spesifikasi Dataset](#spesifikasi-dataset)
- [Arsitektur Model](#arsitektur-model)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Artefak Model](#artefak-model)
- [Lisensi](#lisensi)
- [Kontak & Dukungan](#kontak--dukungan)

---

## Ringkasan

Proyek ini mengimplementasikan **Model Regresi Stacking Ensemble** untuk memprediksi skor risiko keterlambatan pembayaran. Sistem ini menggunakan pendekatan Early Warning System (EWS) untuk menilai risiko transaksi berdasarkan perilaku pembayaran historis, pola temporal, dan karakteristik transaksi.

### Tujuan Utama

- 🎯 Mempersiapkan set fitur minimal untuk inferensi EWS
- 🤖 Melatih beberapa model regresi (XGBoost, CatBoost, LightGBM)
- 📊 Mengimplementasikan stacking ensemble dengan meta-model RandomForestRegressor
- 💾 Menghasilkan artefak model siap produksi untuk deployment API

### Variabel Target

**`Risk_Score`** - Variabel kontinu yang merepresentasikan risiko keterlambatan pembayaran (skala 0-100)

---

## Fitur

### Kategori Fitur

Model menggunakan **27 fitur yang direkayasa** dalam lima kategori:

#### 1. Fitur Temporal (8)

```
Bulan, Hari, Hari_Minggu, Quarter, Is_Weekend, 
Is_Akhir_Bulan, Is_Awal_Bulan, Hari_Dari_Awal_Bulan
```

#### 2. Fitur Perilaku (7)

```
Total_Transaksi, Rata_Nominal, Frekuensi_Per_Hari, 
Durasi_Aktif_Hari, Rata_Interval_Hari, 
Jumlah_Terlambat, Persentase_Terlambat
```

#### 3. Fitur Jenis Transaksi (6)

```
Is_TopUp, Is_QRIS, Is_Transfer, 
Prop_TopUp, Prop_QRIS, Prop_Transfer
```

#### 4. Fitur Aktivitas (2)

```
Aktivitas_Bulan_Ini, Aktivitas_Quarter_Ini
```

#### 5. Fitur Nominal (1)

```
Nominal_Transaksi
```

### Kolom yang Dikecualikan

Kolom berikut dihapus sebelum pelatihan:

```python
excluded_cols = [
    'No_Reff', 'Timestamp', 'Tanggal', 'Nama_Penerima', 
    'Nama_Pengirim', 'Jenis_Transaksi', 'Quarter_Label', 
    'Warning_Level', 'Kategori_Pembayaran', 'Minggu_Ke'
]
```

---

## Struktur Proyek

```
PBL_ML_REGRESSION_RISK/
│
├── notebooks/
│   └── PBL_ML_Regression_Risk_V1.ipynb    # Notebook pelatihan utama
│
├── Dataset/
│   ├── dataset_feature_engineered.csv      # Data pelatihan utama
│   ├── dataset_sintetis.csv                # Data sintetis (opsional)
│   ├── sintetis_diversity/                 # Data sintetis tambahan
│   ├── transaction_data(RealData).csv      # Data transaksi mentah
│   └── warga_mapping.csv                   # Pemetaan warga
│
├── models_ews/
│   └── Regression/
│       ├── gb_regressor.pkl                # Model XGBoost
│       ├── rf_regressor.pkl                # Model RandomForest
│       ├── meta_ridge.pkl                  # Meta-model (stacking)
│       ├── model_info.json                 # Metadata fitur
│       ├── evaluation.json                 # Metrik performa
│       ├── gb_feature_importance.csv       # Feature importance XGBoost
│       ├── rf_feature_importance.csv       # Feature importance RandomForest
│       └── model_comparison.csv            # Tabel perbandingan model
│
├── requirements.txt                        # Dependensi Python
└── README.md                              # File ini
```

---

## Spesifikasi Dataset

### Dataset Utama

**File:** `dataset_feature_engineered.csv`  
**Lokasi:** `./Dataset/` atau path Google Drive  
**Format:** CSV dengan header

### Konfigurasi

Perbarui path dataset di notebook:

```python
# Untuk Google Colab
csv_path = "/content/drive/MyDrive/PBL SEM 5/Dataset ML/V2/DATASET/dataset_feature_engineered.csv"

# Untuk environment lokal
csv_path = "./Dataset/dataset_feature_engineered.csv"
```

### Pembagian Data

- **Set Pelatihan:** 80%
- **Set Pengujian:** 20%
- **Random State:** 42 (untuk reprodusibilitas)

---

## Arsitektur Model

### Struktur Ensemble

```
┌─────────────────────────────────────────┐
│         Fitur Input (27)                │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┬─────────────┐
     │                   │             │
┌────▼────┐      ┌──────▼──────┐  ┌──▼────────┐
│ XGBoost │      │  CatBoost   │  │ LightGBM  │
│Regressor│      │  Regressor  │  │Regressor  │
└────┬────┘      └──────┬──────┘  └──┬────────┘
     │                   │             │
     └─────────┬─────────┴─────────────┘
               │
       ┌───────▼───────┐
       │ RandomForest  │
       │ Meta-Regressor│
       └───────┬───────┘
               │
        ┌──────▼──────┐
        │ Skor Risiko │
        └─────────────┘
```

### Model Dasar

#### 1. XGBoost Regressor

```python
XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
```

#### 2. CatBoost Regressor

```python
CatBoostRegressor(
    iterations=100,
    depth=5,
    learning_rate=0.1,
    random_state=42,
    verbose=False
)
```

*Early stopping diaktifkan dengan patience 10 iterasi*

#### 3. LightGBM Regressor

```python
LGBMRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
```

*Early stopping diaktifkan dengan patience 10 iterasi*

### Meta-Model

```python
RandomForestRegressor(
    n_estimators=50,
    random_state=42
)
```

---

## Instalasi

### Prasyarat

- Python 3.10, 3.11, atau 3.12
- pip package manager
- Virtual environment (direkomendasikan)

### Langkah 1: Clone Repository

```bash
git clone <repository-url>
cd PBL_ML_REGRESSION_RISK
```

### Langkah 2: Buat Virtual Environment

```bash
python -m venv venv

# Aktivasi di Windows
venv\Scripts\activate

# Aktivasi di Linux/Mac
source venv/bin/activate
```

### Langkah 3: Instal Dependensi

```bash
pip install -r requirements.txt
pip install catboost lightgbm questionary
```

### Dependensi Inti

```txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0
catboost>=1.2.0
joblib>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Penggunaan

### Menjalankan Notebook

#### Opsi 1: Jupyter Notebook

```bash
jupyter notebook notebooks/PBL_ML_Regression_Risk_V1.ipynb
```

#### Opsi 2: JupyterLab

```bash
jupyter lab
```

#### Opsi 3: Google Colab

1. Upload notebook ke Google Drive
2. Buka dengan Google Colab
3. Mount Google Drive di cell pertama
4. Perbarui path sesuai kebutuhan

### Langkah Konfigurasi

#### 1. Perbarui Path Dataset

```python
# Temukan cell ini di notebook
csv_path = "./Dataset/dataset_feature_engineered.csv"  # Perbarui path
```

#### 2. Perbarui Direktori Output Model

```python
# Temukan cell ini sebelum penyimpanan model
model_dir = "./models_ews/Regression"  # Perbarui path
os.makedirs(model_dir, exist_ok=True)
```

#### 3. Eksekusi Cell Secara Berurutan

Jalankan semua cell dari atas ke bawah untuk:

- Memuat dan mengeksplorasi data
- Mempersiapkan fitur
- Melatih model dasar
- Membangun stacking ensemble
- Mengevaluasi performa
- Menyimpan artefak model

---

## Artefak Model

### File yang Dihasilkan

Setelah pelatihan berhasil, artefak berikut dibuat:

| File | Deskripsi | Penggunaan |
|------|-----------|------------|
| `gb_regressor.pkl` | Model XGBoost | Model dasar untuk prediksi |
| `rf_regressor.pkl` | Model RandomForest | Model dasar untuk prediksi |
| `meta_ridge.pkl` | Meta-model | Regressor stacking final |
| `model_info.json` | Metadata fitur | Daftar fitur dan statistik |
| `evaluation.json` | Metrik performa | Hasil evaluasi model |
| `gb_feature_importance.csv` | Importance XGBoost | Analisis fitur |
| `rf_feature_importance.csv` | Importance RandomForest | Analisis fitur |
| `model_comparison.csv` | Perbandingan model | Perbandingan performa |

### Struktur model_info.json

```json
{
  "feature_columns": [
    "Bulan", "Hari", "Hari_Minggu", "..."
  ],
  "feature_stats": {
    "Bulan": {"mean": 6.5, "std": 3.4},
    "Hari": {"mean": 15.2, "std": 8.7},
    "..."
  },
  "target_column": "Risk_Score",
  "model_type": "stacking_regressor",
  "training_date": "2024-12-15",
  "n_features": 27
}
```

### Evaluasi Model

Model dievaluasi menggunakan tiga metrik utama:

- **MAE (Mean Absolute Error)** - Rata-rata perbedaan absolut antara prediksi dan nilai aktual
- **RMSE (Root Mean Squared Error)** - Akar kuadrat dari rata-rata perbedaan kuadrat
- **R² (Coefficient of Determination)** - Proporsi varians yang dijelaskan oleh model

Hasil disimpan dalam `evaluation.json` dan `model_comparison.csv` setelah pelatihan.

### Feature Importance

Fitur yang paling berkontribusi dianalisis dan disimpan dalam:

- `gb_feature_importance.csv` (Feature importance XGBoost)
- `rf_feature_importance.csv` (Feature importance RandomForest)

File-file ini membantu memahami fitur mana yang memiliki dampak paling besar pada prediksi skor risiko

---
