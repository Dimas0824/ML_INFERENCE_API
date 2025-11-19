"""
Service untuk melakukan prediksi
"""
import numpy as np
from typing import Dict, Any
import logging

from app.services.model_loader import model_loader
from app.services.feature_builder import feature_builder

logger = logging.getLogger(__name__)


class Predictor:
    """Class untuk melakukan prediksi menggunakan stacking ensemble"""
    
    def __init__(self):
        pass
    
    def predict(self, tanggal: str, nominal: int, verbose: bool = False) -> Dict[str, Any]:
        """
        Prediksi risiko terlambat menggunakan multi-level stacking ensemble.
        
        Args:
            tanggal: Tanggal transaksi (YYYY-MM-DD)
            nominal: Nominal transaksi (Rupiah)
            verbose: Return detail prediksi per level
            
        Returns:
            Dict berisi hasil prediksi dan detail (jika verbose=True)
        """
        try:
            # Build features
            base_dict = feature_builder.build_base_features(tanggal, nominal)
            X = feature_builder.prepare_features(base_dict)
            
            result = {
                "risk_score": 0.0,
                "details": {} if verbose else None
            }
            
            # Get models
            level0_models = model_loader.get_level0_models()
            level1_models = model_loader.get_level1_models()
            
            # === LEVEL 0: Base Models ===
            level0_preds = []
            level0_details = {}
            
            for name, model in level0_models.items():
                pred = model.predict(X)[0]
                level0_preds.append(pred)
                level0_details[name] = float(pred)
                logger.debug(f"Level 0 - {name}: {pred:.4f}")
            
            level0_array = np.array(level0_preds).reshape(1, -1)
            level0_avg = float(np.mean(level0_preds))
            
            if verbose:
                result["details"]["level0"] = level0_details
                result["details"]["level0_average"] = level0_avg
            
            # === LEVEL 1: Meta Model ===
            level1_preds = []
            level1_details = {}
            
            for name, model in level1_models.items():
                pred = model.predict(level0_array)[0]
                level1_preds.append(pred)
                level1_details[name] = float(pred)
                logger.debug(f"Level 1 - {name}: {pred:.4f}")
            
            # Final prediction
            final_pred = float(np.mean(level1_preds))
            
            if verbose:
                result["details"]["level1"] = level1_details
            
            result["risk_score"] = final_pred
            
            logger.info(f"Prediction completed: risk_score={final_pred:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise
    
    def predict_batch(self, requests: list) -> list:
        """
        Prediksi batch untuk multiple inputs.
        
        Args:
            requests: List of dict dengan keys 'tanggal' dan 'nominal'
            
        Returns:
            List of prediction results
        """
        try:
            results = []
            for req in requests:
                result = self.predict(
                    tanggal=req["tanggal"],
                    nominal=req["nominal"],
                    verbose=req.get("verbose", False)
                )
                results.append(result)
            
            logger.info(f"Batch prediction completed: {len(results)} items")
            return results
            
        except Exception as e:
            logger.error(f"Error during batch prediction: {e}")
            raise


# Global instance
predictor = Predictor()