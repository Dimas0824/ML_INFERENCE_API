"""
Configuration file for FastAPI EWS application
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Early Warning System API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API untuk prediksi risiko keterlambatan pembayaran"
    
    # Model Settings
    MODEL_DIR: Path = Path("models_ews")
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    
    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 20.0
    RISK_THRESHOLD_MEDIUM: float = 50.0
    RISK_THRESHOLD_HIGH: float = 75.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()