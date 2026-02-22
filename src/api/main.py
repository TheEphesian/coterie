"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.api.routes import characters_router, players_router, apr_router, imports_router, boons_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Modern Python API for Grapevine LARP character management",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        characters_router,
        prefix=f"{settings.api_prefix}",
        tags=["characters"],
    )
    
    app.include_router(
        players_router,
        prefix=f"{settings.api_prefix}",
        tags=["players"],
    )
    
    app.include_router(
        apr_router,
        prefix=f"{settings.api_prefix}",
        tags=["apr"],
    )
    
    app.include_router(
        imports_router,
        prefix=f"{settings.api_prefix}",
        tags=["imports"],
    )
    
    app.include_router(
        boons_router,
        prefix=f"{settings.api_prefix}",
        tags=["boons"],
    )
    
    return app


# Create application instance
app = create_application()


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
