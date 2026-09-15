from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware.subscription import SubscriptionCheckMiddleware
from app.core.scheduler import start_scheduler, stop_scheduler
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start APScheduler background task manager
    start_scheduler()
    yield
    # Shutdown: stop APScheduler
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Middleware configuration
app.add_middleware(SubscriptionCheckMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root API endpoints
@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
