"""
FastAPI Main Application
Early Warning System untuk Prediksi Risiko Keterlambatan Pembayaran
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.config import settings
from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    ErrorResponse,
    HealthResponse
)
from app.services.model_loader import model_loader
from app.services.predictor import predictor
from app.utils.risk_analyzer import risk_analyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== STARTUP & SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Load models saat aplikasi startup"""
    try:
        logger.info("🚀 Starting application...")
        logger.info("📦 Loading ML models...")
        model_loader.load_models()
        logger.info("✅ Models loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup saat aplikasi shutdown"""
    logger.info("👋 Shutting down application...")


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler untuk HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler untuk general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ==================== ROUTES ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Early Warning System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": model_loader.is_loaded()
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Prediction"]
)
async def predict_risk(request: PredictionRequest):
    """
    Endpoint untuk prediksi risiko keterlambatan pembayaran.
    
    ### Parameters:
    - **tanggal**: Tanggal transaksi (format: YYYY-MM-DD)
    - **nominal**: Nominal transaksi dalam Rupiah (harus > 0)
    - **target_type**: Tipe target pengiriman (broadcast/rt_tertentu)
    - **rt_number**: Nomor RT (wajib jika target_type = rt_tertentu)
    
    ### Returns:
    - **risk_score**: Score risiko (0-100)
    - **risk_category**: Kategori risiko dan rekomendasi
    """
    try:
        # Check if models are loaded
        if not model_loader.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Models belum siap. Silakan coba lagi."
            )
        
        # Perform prediction
        prediction_result = predictor.predict(
            tanggal=request.tanggal,
            nominal=request.nominal,
            verbose=False  # Set True jika ingin detail per level
        )
        
        # Format result
        formatted_result = risk_analyzer.format_result(
            tanggal=request.tanggal,
            nominal=request.nominal,
            target_type=request.target_type,
            rt_number=request.rt_number or "",
            risk_score=prediction_result["risk_score"],
            details=prediction_result.get("details")
        )
        
        logger.info(
            f"Prediction successful - Date: {request.tanggal}, "
            f"Nominal: {request.nominal}, Risk: {formatted_result['risk_score']}%"
        )
        
        return {
            "success": True,
            "data": formatted_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan prediksi: {str(e)}"
        )


@app.post(
    "/predict/verbose",
    response_model=PredictionResponse,
    tags=["Prediction"]
)
async def predict_risk_verbose(request: PredictionRequest):
    """
    Endpoint untuk prediksi dengan detail per level model.
    Sama seperti /predict tetapi mengembalikan detail prediksi per level.
    """
    try:
        if not model_loader.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Models belum siap. Silakan coba lagi."
            )
        
        # Perform prediction with verbose=True
        prediction_result = predictor.predict(
            tanggal=request.tanggal,
            nominal=request.nominal,
            verbose=True
        )
        
        # Format result
        formatted_result = risk_analyzer.format_result(
            tanggal=request.tanggal,
            nominal=request.nominal,
            target_type=request.target_type,
            rt_number=request.rt_number or "",
            risk_score=prediction_result["risk_score"],
            details=prediction_result.get("details")
        )
        
        return {
            "success": True,
            "data": formatted_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan prediksi: {str(e)}"
        )


@app.get("/models/info", tags=["Models"])
async def get_models_info():
    """Get informasi tentang models yang di-load"""
    try:
        if not model_loader.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Models belum di-load"
            )
        
        return {
            "success": True,
            "data": {
                "level0_models": list(model_loader.get_level0_models().keys()),
                "level1_models": list(model_loader.get_level1_models().keys()),
                "total_features": len(model_loader.get_feature_columns()),
                "feature_columns": model_loader.get_feature_columns()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )