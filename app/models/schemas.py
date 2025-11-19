"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Literal


class PredictionRequest(BaseModel):
    """Request schema untuk prediksi"""
    tanggal: str = Field(
        ..., 
        description="Tanggal transaksi (format: YYYY-MM-DD)",
        examples=["2025-01-15"]
    )
    nominal: int = Field(
        ..., 
        gt=0,
        description="Nominal transaksi dalam Rupiah",
        examples=[500000]
    )
    target_type: Literal["broadcast", "rt_tertentu"] = Field(
        ...,
        description="Tipe target pengiriman",
        examples=["broadcast"]
    )
    rt_number: Optional[str] = Field(
        None,
        description="Nomor RT (wajib jika target_type = rt_tertentu)",
        examples=["001"]
    )
    
    @validator('tanggal')
    def validate_date(cls, v):
        """Validasi format tanggal"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Format tanggal harus YYYY-MM-DD")
    
    @validator('rt_number', always=True)
    def validate_rt_number(cls, v, values):
        """Validasi rt_number jika target_type = rt_tertentu"""
        if values.get('target_type') == 'rt_tertentu' and not v:
            raise ValueError("rt_number wajib diisi jika target_type adalah rt_tertentu")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "tanggal": "2025-01-15",
                "nominal": 500000,
                "target_type": "broadcast",
                "rt_number": None
            }
        }


class RiskCategory(BaseModel):
    """Model untuk kategori risiko"""
    status: str = Field(..., description="Status risiko (RENDAH/SEDANG/TINGGI/SANGAT TINGGI)")
    emoji: str = Field(..., description="Emoji indikator")
    rekomendasi: str = Field(..., description="Rekomendasi tindakan")
    tindakan: list[str] = Field(..., description="List tindakan yang disarankan")


class PredictionResponse(BaseModel):
    """Response schema untuk hasil prediksi"""
    success: bool = Field(..., description="Status keberhasilan prediksi")
    data: dict = Field(..., description="Data hasil prediksi")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "tanggal": "2025-01-15",
                    "nominal": 500000,
                    "target_type": "broadcast",
                    "rt_number": None,
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
        }


class ErrorResponse(BaseModel):
    """Response schema untuk error"""
    success: bool = Field(False, description="Status keberhasilan")
    error: str = Field(..., description="Pesan error")
    detail: Optional[str] = Field(None, description="Detail error (optional)")


class HealthResponse(BaseModel):
    """Response schema untuk health check"""
    status: str = Field(..., description="Status aplikasi")
    timestamp: str = Field(..., description="Waktu pengecekan")
    models_loaded: bool = Field(..., description="Status model ML")