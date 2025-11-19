"""
Utility untuk analisis dan kategorisasi risiko
"""
from typing import Dict, Any, Optional
from app.config import settings


class RiskAnalyzer:
    """Class untuk mengkategorisasi dan menganalisis risiko"""
    
    @staticmethod
    def categorize_risk(risk_score: float) -> Dict[str, Any]:
        """
        Kategorisasi risiko berdasarkan score.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Dict berisi kategori dan rekomendasi
        """
        if risk_score < settings.RISK_THRESHOLD_LOW:
            return {
                "status": "RENDAH",
                "emoji": "✅",
                "rekomendasi": "Risiko rendah. Transaksi dapat dilanjutkan dengan aman.",
                "tindakan": [
                    "Lakukan monitoring rutin"
                ]
            }
        
        elif risk_score < settings.RISK_THRESHOLD_MEDIUM:
            return {
                "status": "SEDANG",
                "emoji": "⚠️",
                "rekomendasi": "Risiko sedang. Perlu monitoring berkala.",
                "tindakan": [
                    "Monitor pembayaran secara berkala",
                    "Kirim reminder H-3 jatuh tempo"
                ]
            }
        
        elif risk_score < settings.RISK_THRESHOLD_HIGH:
            return {
                "status": "TINGGI",
                "emoji": "🔴",
                "rekomendasi": "PERINGATAN: Risiko tinggi keterlambatan!",
                "tindakan": [
                    "Aktifkan reminder otomatis",
                    "Follow-up intensif H-7 dan H-3",
                    "Pertimbangkan metode pembayaran alternatif"
                ]
            }
        
        else:
            return {
                "status": "SANGAT TINGGI",
                "emoji": "🚨",
                "rekomendasi": "PERINGATAN KRITIS! Risiko sangat tinggi!",
                "tindakan": [
                    "TUNDA transaksi jika memungkinkan",
                    "Follow-up personal sebelum transaksi",
                    "Siapkan prosedur penagihan",
                    "Pertimbangkan pembayaran di muka"
                ]
            }
    
    @staticmethod
    def format_result(
        tanggal: str,
        nominal: int,
        target_type: str,
        rt_number: str,
        risk_score: float,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format hasil prediksi dengan lengkap.
        
        Args:
            tanggal: Tanggal transaksi
            nominal: Nominal transaksi
            target_type: Tipe target (broadcast/rt_tertentu)
            rt_number: Nomor RT (optional)
            risk_score: Risk score hasil prediksi
            details: Detail prediksi (optional)
            
        Returns:
            Dict berisi hasil lengkap
        """
        risk_category = RiskAnalyzer.categorize_risk(risk_score)
        
        result = {
            "tanggal": tanggal,
            "nominal": nominal,
            "target_type": target_type,
            "rt_number": rt_number,
            "risk_score": round(risk_score, 2),
            "risk_category": risk_category
        }
        
        if details:
            result["prediction_details"] = details
        
        return result


# Global instance
risk_analyzer = RiskAnalyzer()