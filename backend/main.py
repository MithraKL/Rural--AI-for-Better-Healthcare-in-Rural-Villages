from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models import Village
from backend.api import (
    villages, districts, facilities, risk, predictions, explanations,
    interventions, simulation, resources, priorities, data, dashboard,
    early_warning, methodology,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RuralCare AI")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Village).count() == 0:
            logger.info("No data found — seeding synthetic demo dataset and running AI pipeline...")
            from scripts.seed_db import main as seed_main
            seed_main()
        else:
            logger.info("Existing data found (%d villages) — skipping auto-seed.", db.query(Village).count())
    finally:
        db.close()

    yield
    logger.info("Shutting down RuralCare AI")


app = FastAPI(
    title="RuralCare AI",
    description="AI-Powered Rural Healthcare Decision Intelligence — not a chatbot, not a BI dashboard. "
                 "A decision-support system that detects hidden healthcare gaps, predicts risk, explains "
                 "why, prioritizes villages, recommends interventions and optimizes limited resources.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(villages.router, prefix="/api/villages", tags=["Villages"])
app.include_router(districts.router, prefix="/api/districts", tags=["Districts"])
app.include_router(facilities.router, prefix="/api/facilities", tags=["Facilities"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(explanations.router, prefix="/api/explanations", tags=["Explainability"])
app.include_router(interventions.router, prefix="/api/interventions", tags=["Interventions"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["What-If Simulation"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resource Optimization"])
app.include_router(priorities.router, prefix="/api/priorities", tags=["Prioritization"])
app.include_router(data.router, prefix="/api/data", tags=["Data Ingestion"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(early_warning.router, prefix="/api/early-warning", tags=["Early Warning"])
app.include_router(methodology.router, prefix="/api/methodology", tags=["Methodology"])


@app.get("/")
async def root():
    return {
        "message": "RuralCare AI API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
