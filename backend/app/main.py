from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import projects, documents, segments, translations, glossaries, tm, jobs

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered translation platform API for software localization and product labels",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(segments.router, prefix=settings.api_prefix)
app.include_router(translations.router, prefix=settings.api_prefix)
app.include_router(glossaries.router, prefix=settings.api_prefix)
app.include_router(tm.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.

    Returns API status and version information.
    No authentication required.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )


@app.get("/", tags=["root"])
def root():
    """
    Root endpoint.

    Returns API information and documentation links.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "projects": f"{settings.api_prefix}/projects",
            "documents": f"{settings.api_prefix}/documents",
            "segments": f"{settings.api_prefix}/segments",
            "translations": f"{settings.api_prefix}/translations",
            "glossaries": f"{settings.api_prefix}/glossaries",
            "translation_memory": f"{settings.api_prefix}/tm",
            "jobs": f"{settings.api_prefix}/jobs"
        }
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )
