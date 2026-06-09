"""
FastAPI application entry point for FMCG BI Assistant backend.
"""
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database import init_db, health_check
from api.routes import router as api_router
import api.routes as api_routes

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    # Initialize AI workflow
    try:
        from ai_agent import FMCGAgentWorkflow
        workflow = FMCGAgentWorkflow(db_path=settings.AI_DATABASE_PATH)
        api_routes.workflow = workflow
        logger.info("AI workflow initialized")
    except Exception as e:
        logger.error(f"AI workflow initialization failed: {str(e)}")
        logger.warning("Running without AI agents - chat endpoints will fail")
    
    # Check database health
    if health_check():
        logger.info("Database connection healthy")
    else:
        logger.warning("Database health check failed")
    
    logger.info(f"{settings.APP_NAME} started successfully")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# ==================== Create FastAPI App ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI backend for FMCG BI Assistant",
    version=settings.VERSION,
    lifespan=lifespan
)


# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Error Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.DEBUG else None
        }
    )


# ==================== Request Logging Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    import time
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response


# ==================== Routes ====================

app.include_router(api_router)


# ==================== Root Endpoint ====================

@app.get("/", tags=["root"])
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "api_docs": "/docs",
        "api_prefix": settings.API_PREFIX
    }


@app.get("/docs", tags=["docs"], include_in_schema=False)
async def swagger_docs_redirect():
    """Redirect to Swagger docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# ==================== Ready Check ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
