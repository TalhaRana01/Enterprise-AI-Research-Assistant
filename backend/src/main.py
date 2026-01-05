"""FastAPI application entry point for AI Research Assistant."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from src.config import settings
from src.utils.logger import get_logger, setup_logging
from src.api.routes import search_router, chat_router, papers_router, auth_router
from src.api.models.schemas import HealthResponse, ErrorResponse
from src.database import init_db

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Research Assistant API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Research Assistant API...")


# Create FastAPI app
app = FastAPI(
    title="AI Research Assistant API",
    description="""
    Enterprise-grade AI Research Assistant API powered by LangChain.
    
    **Features:**
    - 🔍 Search research papers across multiple sources
    - 💬 Ask questions about papers using RAG
    - 📄 Summarize papers in multiple formats
    - 📚 Generate citations in various styles
    - 🤖 Multi-agent system for intelligent research assistance
    
    **Endpoints:**
    - `/api/v1/search` - Search for papers
    - `/api/v1/chat` - Q&A about papers
    - `/api/v1/papers` - Paper management (summarize, cite)
    - `/health` - Health check
    """,
    version="0.1.0",
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    lifespan=lifespan
)

# CORS middleware
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include routers
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(papers_router)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.2f}s"
    )
    
    return response


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Research Assistant API",
        "version": "0.1.0",
        "docs": "/docs" if settings.enable_api_docs else "disabled",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and version information.
    """
    try:
        # Check if critical components are working
        from src.chains import get_vector_store
        
        vector_store = get_vector_store()
        info = vector_store.get_collection_info()
        
        return HealthResponse(
            status="healthy",
            version="0.1.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            version="0.1.0"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found",
            detail=f"Endpoint {request.url.path} not found",
            code="404"
        ).model_dump()
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            code="500"
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers if not settings.debug else 1
    )

