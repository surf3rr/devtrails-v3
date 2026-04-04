"""
Fraud Detection Engine — Main Application Entry Point
Parametric Insurance Platform for Gig Workers
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import claims, training, history
from app.core.config import settings
from app.db.database import init_db
from app.ml.model_manager import ModelManager

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("fraud_engine.log"),
    ],
)
logger = logging.getLogger(__name__)


# ─── Application Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, clean up on shutdown."""
    logger.info("Starting Fraud Detection Engine...")
    await init_db()
    model_manager = ModelManager()
    model_manager.load_or_train()
    app.state.model_manager = model_manager
    logger.info("Engine ready.")
    yield
    logger.info("Shutting down Fraud Detection Engine.")
    
# ─── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Fraud Detection Engine",
    description="Parametric insurance fraud detection for gig workers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(claims.router, prefix="/api", tags=["Claims"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(training.router, prefix="/api", tags=["Training"])


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "fraud-detection-engine"}
