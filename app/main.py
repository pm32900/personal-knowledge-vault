from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import setup_logging, get_logger
from app.database import init_db
from app.core.exceptions import AppException
from app.api.v1 import auth, notes, rag, search

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(
        "app_exception",
        path=request.url.path,
        status_code=exc.status_code,
        message=exc.message
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "unexpected_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("application_startup", version=settings.APP_VERSION)
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        # Don't crash the app, but log the error


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(notes.router, prefix="/api/v1/notes", tags=["Notes"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }