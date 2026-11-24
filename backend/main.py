from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1 endpoints
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Root endpoint for basic verification
    @application.get("/", summary="Root Health / Welcome")
    def read_root():
        return {"message": "Hello World"}

    @application.get("/health", summary="Health Check")
    def health_check():
        return {"status": "healthy", "version": settings.VERSION}

    return application

app = create_application()
