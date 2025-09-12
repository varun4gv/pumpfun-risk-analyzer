"""
Pump.fun Risk Analyzer - Backend API
A comprehensive risk analysis system for pump.fun tokens
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import init_db
from .models import TokenRisk, TokenAnalysis, Alert
from .services import RiskAnalyzer, AlertService, TokenService
from .utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
risk_analyzer: Optional[RiskAnalyzer] = None
alert_service: Optional[AlertService] = None
token_service: Optional[TokenService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global risk_analyzer, alert_service, token_service
    
    # Startup
    logger.info("Starting Pump.fun Risk Analyzer...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    risk_analyzer = RiskAnalyzer()
    alert_service = AlertService()
    token_service = TokenService()
    
    # Start background tasks
    asyncio.create_task(risk_analyzer.start_monitoring())
    asyncio.create_task(alert_service.start_alert_processor())
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if risk_analyzer:
        await risk_analyzer.stop_monitoring()
    if alert_service:
        await alert_service.stop_alert_processor()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Pump.fun Risk Analyzer",
    description="A comprehensive risk analysis system for pump.fun tokens",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pump.fun Risk Analyzer API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "risk_analyzer": risk_analyzer is not None,
            "alert_service": alert_service is not None,
            "token_service": token_service is not None
        }
    }


@app.post("/api/token/analyze")
async def analyze_token(
    token_address: str,
    background_tasks: BackgroundTasks
) -> TokenAnalysis:
    """Analyze a token for risk factors"""
    if not risk_analyzer:
        raise HTTPException(status_code=503, detail="Risk analyzer not available")
    
    try:
        # Start analysis in background
        analysis = await risk_analyzer.analyze_token(token_address)
        
        # Store results
        background_tasks.add_task(
            token_service.store_analysis,
            token_address,
            analysis
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing token {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/token/{token_address}/risk")
async def get_token_risk(token_address: str) -> TokenRisk:
    """Get current risk assessment for a token"""
    if not token_service:
        raise HTTPException(status_code=503, detail="Token service not available")
    
    try:
        risk = await token_service.get_token_risk(token_address)
        if not risk:
            raise HTTPException(status_code=404, detail="Token not found")
        
        return risk
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token risk {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/token/{token_address}/holders")
async def get_token_holders(token_address: str) -> Dict:
    """Get token holder distribution"""
    if not token_service:
        raise HTTPException(status_code=503, detail="Token service not available")
    
    try:
        holders = await token_service.get_token_holders(token_address)
        return {"token_address": token_address, "holders": holders}
        
    except Exception as e:
        logger.error(f"Error getting token holders {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/token/{token_address}/transactions")
async def get_token_transactions(
    token_address: str,
    limit: int = 100,
    offset: int = 0
) -> Dict:
    """Get recent transactions for a token"""
    if not token_service:
        raise HTTPException(status_code=503, detail="Token service not available")
    
    try:
        transactions = await token_service.get_token_transactions(
            token_address, limit, offset
        )
        return {
            "token_address": token_address,
            "transactions": transactions,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting token transactions {token_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(
    risk_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict:
    """Get recent alerts"""
    if not alert_service:
        raise HTTPException(status_code=503, detail="Alert service not available")
    
    try:
        alerts = await alert_service.get_alerts(risk_level, limit, offset)
        return {
            "alerts": alerts,
            "limit": limit,
            "offset": offset,
            "risk_level": risk_level
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alerts/subscribe")
async def subscribe_to_alerts(
    email: str,
    risk_threshold: str = "medium",
    token_addresses: Optional[List[str]] = None
) -> Dict:
    """Subscribe to risk alerts"""
    if not alert_service:
        raise HTTPException(status_code=503, detail="Alert service not available")
    
    try:
        subscription = await alert_service.create_subscription(
            email, risk_threshold, token_addresses
        )
        return {
            "message": "Subscription created successfully",
            "subscription_id": subscription.id
        }
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats() -> Dict:
    """Get platform statistics"""
    if not token_service:
        raise HTTPException(status_code=503, detail="Token service not available")
    
    try:
        stats = await token_service.get_platform_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
