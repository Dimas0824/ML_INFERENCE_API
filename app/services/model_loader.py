"""
Service untuk loading ML models
"""
import json
import joblib
from pathlib import Path
from typing import Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """Class untuk load dan manage ML models"""
    
    def __init__(self):
        self.level0_models: Dict[str, Any] = {}
        self.level1_models: Dict[str, Any] = {}
        self.model_info: Dict[str, Any] = {}
        self.feature_columns: list = []
        self.feature_stats: Dict[str, Any] = {}
        self._loaded = False
    
    def load_models(self) -> bool:
        """
        Load semua model dari directory
        
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            model_dir = Path(settings.MODEL_DIR)
            
            if not model_dir.exists():
                raise FileNotFoundError(f"Model directory tidak ditemukan: {model_dir}")
            
            logger.info(f"Loading models from: {model_dir}")
            
            # Load Level 0 Models
            self.level0_models = {
                "gb": joblib.load(model_dir / "gb_regressor.pkl"),
                "rf": joblib.load(model_dir / "rf_regressor.pkl"),
            }
            logger.info(f"✓ Loaded {len(self.level0_models)} Level 0 models")
            
            # Load Level 1 Models
            self.level1_models = {
                "meta_ridge": joblib.load(model_dir / "meta_ridge.pkl")
            }
            logger.info(f"✓ Loaded {len(self.level1_models)} Level 1 models")
            
            # Load Model Info
            with open(model_dir / "model_info.json", "r") as f:
                self.model_info = json.load(f)
            
            self.feature_columns = self.model_info["feature_columns"]
            self.feature_stats = self.model_info["feature_stats"]
            
            logger.info(f"✓ Loaded model info with {len(self.feature_columns)} features")
            
            self._loaded = True
            return True
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check apakah models sudah di-load"""
        return self._loaded
    
    def get_level0_models(self) -> Dict[str, Any]:
        """Get Level 0 models"""
        if not self._loaded:
            raise RuntimeError("Models belum di-load. Panggil load_models() terlebih dahulu.")
        return self.level0_models
    
    def get_level1_models(self) -> Dict[str, Any]:
        """Get Level 1 models"""
        if not self._loaded:
            raise RuntimeError("Models belum di-load. Panggil load_models() terlebih dahulu.")
        return self.level1_models
    
    def get_feature_columns(self) -> list:
        """Get feature columns"""
        if not self._loaded:
            raise RuntimeError("Models belum di-load. Panggil load_models() terlebih dahulu.")
        return self.feature_columns
    
    def get_feature_stats(self) -> Dict[str, Any]:
        """Get feature statistics"""
        if not self._loaded:
            raise RuntimeError("Models belum di-load. Panggil load_models() terlebih dahulu.")
        return self.feature_stats


# Global instance
model_loader = ModelLoader()