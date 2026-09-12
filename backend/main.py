from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, Base
from backend.routers import health_records, villages, workers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Rural Healthcare Management System")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Rural Healthcare Management System",
    description="Intelligent nervous system for rural healthcare connecting data to decisions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_records.router, prefix="/api/v1/health-records", tags=["Health Records"])
app.include_router(villages.router, prefix="/api/v1/villages", tags=["Villages"])
app.include_router(workers.router, prefix="/api/v1/workers", tags=["Health Workers"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Rural Healthcare Management System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
