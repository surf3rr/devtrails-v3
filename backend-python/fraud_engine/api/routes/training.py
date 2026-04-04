"""
Training API — POST /train-model
Triggers retraining of the ML model on synthetic or DB-sourced data.
"""

import logging
import numpy as np
from fastapi import APIRouter, Request

from fraud_engine.core.schemas import TrainResponse
from fraud_engine.ml.model_manager import (
    ModelManager,
    generate_synthetic_training_data,
    build_feature_vector,
    DISRUPTION_TYPES,
)
from fraud_engine.db.database import AsyncSessionLocal, ClaimRecord
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/train-model", response_model=TrainResponse)
async def train_model(request: Request):
    """
    Retrain the Isolation Forest anomaly detection model.

    The model is trained on:
    1. All existing claims in the database (if any)
    2. Supplemented with synthetic data to ensure sufficient volume

    This endpoint is idempotent — safe to call multiple times.
    """
    model_manager: ModelManager = request.app.state.model_manager

    # ── Collect real claims from DB ──────────────────────────────────────────
    real_samples = []
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ClaimRecord))
        records = result.scalars().all()

        for r in records:
            try:
                vec = build_feature_vector(
                    claim_frequency_30d=0,           # Simplified for retraining
                    location_deviation_km=0.0,
                    hours_after_event=0.0,
                    claimed_loss_amount=r.claimed_loss_amount,
                    disruption_type=r.disruption_type,
                )
                real_samples.append(vec)
            except Exception as e:
                logger.warning(f"Skipping record {r.claim_id}: {e}")

    # ── Build training matrix ────────────────────────────────────────────────
    synthetic = generate_synthetic_training_data(n_normal=600, n_anomaly=100)

    if real_samples:
        real_matrix = np.array(real_samples, dtype=np.float64)
        X = np.vstack([synthetic, real_matrix])
        logger.info(f"Training on {len(synthetic)} synthetic + {len(real_samples)} real samples.")
    else:
        X = synthetic
        logger.info(f"Training on {len(synthetic)} synthetic samples (no real data yet).")

    # ── Train ────────────────────────────────────────────────────────────────
    metrics = model_manager.train(X)

    return TrainResponse(
        status="success",
        samples_used=len(X),
        model_version=model_manager.version,
        metrics=metrics,
    )
