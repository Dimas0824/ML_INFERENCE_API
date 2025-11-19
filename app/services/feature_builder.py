"""
Service untuk feature engineering
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any
import logging

from app.services.model_loader import model_loader

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Class untuk build features dari input"""
    
    def __init__(self):
        pass
    
    def build_base_features(self, tanggal: str, nominal: int) -> Dict[str, Any]:
        """
        Membentuk fitur dari input admin.
        
        Args:
            tanggal: Tanggal transaksi (format: YYYY-MM-DD)
            nominal: Nominal transaksi
            
        Returns:
            Dict berisi semua features
        """
        try:
            dt = datetime.strptime(tanggal, "%Y-%m-%d")
            feature_stats = model_loader.get_feature_stats()
            
            features = {
                # === TEMPORAL FEATURES ===
                "Bulan": dt.month,
                "Hari": dt.day,
                "Hari_Minggu": dt.weekday(),
                "Quarter": (dt.month - 1) // 3 + 1,
                "Is_Weekend": 1 if dt.weekday() >= 5 else 0,
                "Is_Akhir_Bulan": 1 if dt.day >= 28 else 0,
                "Is_Awal_Bulan": 1 if dt.day <= 3 else 0,
                "Hari_Dari_Awal_Bulan": dt.day,
                
                # === NOMINAL ===
                "Nominal_Transaksi": nominal,
                
                # === BEHAVIOR FEATURES (mean dari training) ===
                "Total_Transaksi": feature_stats["Total_Transaksi"]["mean"],
                "Rata_Nominal": feature_stats["Rata_Nominal"]["mean"],
                "Frekuensi_Per_Hari": feature_stats["Frekuensi_Per_Hari"]["mean"],
                "Durasi_Aktif_Hari": feature_stats["Durasi_Aktif_Hari"]["mean"],
                "Rata_Interval_Hari": feature_stats["Rata_Interval_Hari"]["mean"],
                "Jumlah_Terlambat": feature_stats["Jumlah_Terlambat"]["mean"],
                "Persentase_Terlambat": feature_stats["Persentase_Terlambat"]["mean"],
                
                # === TRANSACTION TYPE ===
                "Is_TopUp": feature_stats["Is_TopUp"]["mean"],
                "Is_QRIS": feature_stats["Is_QRIS"]["mean"],
                "Is_Transfer": feature_stats["Is_Transfer"]["mean"],
                
                # === PROPORSI TRANSAKSI ===
                "Prop_TopUp": feature_stats["Prop_TopUp"]["mean"],
                "Prop_QRIS": feature_stats["Prop_QRIS"]["mean"],
                "Prop_Transfer": feature_stats["Prop_Transfer"]["mean"],
                
                # === AKTIVITAS ===
                "Aktivitas_Bulan_Ini": feature_stats["Aktivitas_Bulan_Ini"]["mean"],
                "Aktivitas_Quarter_Ini": feature_stats["Aktivitas_Quarter_Ini"]["mean"],
            }
            
            logger.debug(f"Built features for date={tanggal}, nominal={nominal}")
            return features
            
        except Exception as e:
            logger.error(f"Error building features: {e}")
            raise
    
    def prepare_features(self, input_dict: Dict[str, Any]) -> np.ndarray:
        """
        Pastikan urutan fitur sama dengan training.
        
        Args:
            input_dict: Dictionary berisi features
            
        Returns:
            numpy array dengan urutan kolom yang benar
        """
        try:
            feature_columns = model_loader.get_feature_columns()
            
            # Buat DataFrame dengan urutan kolom yang benar
            df = pd.DataFrame(
                [[input_dict.get(col, 0) for col in feature_columns]],
                columns=feature_columns
            )
            
            logger.debug(f"Prepared features with shape: {df.shape}")
            return df.values
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise


# Global instance
feature_builder = FeatureBuilder()