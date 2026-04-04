"""
Fraud Detector — orchestrates the full detection pipeline.

Pipeline:
  1. Fetch weather event data
  2. Query recent claims for duplicate check
  3. Query worker activity history
  4. Run deterministic rules engine
  5. Compute ML anomaly score
  6. Blend scores with weighted average
  7. Apply decision thresholds (APPROVE / REVIEW / REJECT)
  8. Persist result + log flagged claims
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Tuple, List

from sqlalchemy.ext.asyncio import AsyncSession

from fraud_engine.core.config import settings
from fraud_engine.core.schemas import ClaimRequest, FraudCheckResponse, Decision
from fraud_engine.db.database import (
    ClaimRecord,
    get_recent_claims,
    get_worker_activity_days,
    get_area_claim_count,
    save_claim,
)
from fraud_engine.ml.model_manager import ModelManager
from fraud_engine.rules.rules_engine import RulesEngine
from fraud_engine.services.weather_service import WeatherService, _haversine

import json

logger = logging.getLogger(__name__)

# Weights for blending rule score vs ML score
RULE_WEIGHT = 0.65
ML_WEIGHT = 0.35


class FraudDetector:
    """
    Top-level fraud detection pipeline.
    Combines deterministic rules and ML-based anomaly detection.
    """

    def __init__(self, model_manager: ModelManager):
        self.rules = RulesEngine()
        self.weather = WeatherService()
        self.ml = model_manager

    async def check_claim(
        self,
        request: ClaimRequest,
        db: AsyncSession,
    ) -> FraudCheckResponse:
        """
        Full fraud check pipeline. Returns a structured FraudCheckResponse.
        """
        claim_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        logger.info(f"[{claim_id}] Processing claim for user={request.user_id}")

        # ── Step 1: Weather event lookup ─────────────────────────────────────
        weather_event = self.weather.find_matching_event(
            disruption_type=request.disruption_type.value,
            claim_timestamp=request.timestamp,
            claim_lat=request.gps_location.lat,
            claim_lon=request.gps_location.lon,
        )

        # ── Step 2: Duplicate check ──────────────────────────────────────────
        window_start = request.timestamp - timedelta(minutes=settings.DUPLICATE_WINDOW_MINUTES)
        recent_claims = await get_recent_claims(
            db,
            user_id=request.user_id,
            disruption_type=request.disruption_type.value,
            since_timestamp=window_start,
        )

        # ── Step 3: Worker activity ──────────────────────────────────────────
        active_days = await get_worker_activity_days(
            db,
            user_id=request.user_id,
            since_timestamp=request.timestamp,
        )

        # ── Step 3b: Syndicate detection ─────────────────────────────────────
        recent_area_claims = await get_area_claim_count(
            db,
            lat=request.gps_location.lat,
            lon=request.gps_location.lon,
            disruption_type=request.disruption_type.value,
            radius_deg=0.5,
            since_minutes=60,
        )

        # ── Step 4: Rules engine ─────────────────────────────────────────────
        rule_score, reasons, rule_flags = self.rules.evaluate(
            request=request,
            weather_event=weather_event,
            recent_claims=recent_claims,
            active_days=active_days,
            submission_time=now,
            recent_area_claims=recent_area_claims,
        )

        # ── Step 5: ML anomaly score ─────────────────────────────────────────
        location_deviation_km = (
            _haversine(
                request.gps_location.lat, request.gps_location.lon,
                weather_event.centroid_lat, weather_event.centroid_lon,
            )
            if weather_event else 999.0
        )

        claim_ts = request.timestamp
        if claim_ts.tzinfo is None:
            claim_ts = claim_ts.replace(tzinfo=timezone.utc)
        hours_after = max((now - claim_ts).total_seconds() / 3600, 0)

        ml_score = self.ml.score(
            claim_frequency_30d=len(recent_claims),
            location_deviation_km=location_deviation_km,
            hours_after_event=hours_after,
            claimed_loss_amount=request.claimed_loss_amount,
            disruption_type=request.disruption_type.value,
        )

        # ── Step 6: Blend scores ─────────────────────────────────────────────
        fraud_score = round(RULE_WEIGHT * rule_score + ML_WEIGHT * ml_score, 4)
        fraud_score = max(0.0, min(1.0, fraud_score))

        # ── Step 7: Decision ─────────────────────────────────────────────────
        decision = _make_decision(fraud_score)

        # ── Step 8: Persist + log ────────────────────────────────────────────
        is_flagged = decision != Decision.APPROVE
        record = ClaimRecord(
            claim_id=claim_id,
            user_id=request.user_id,
            timestamp=request.timestamp,
            gps_lat=request.gps_location.lat,
            gps_lon=request.gps_location.lon,
            disruption_type=request.disruption_type.value,
            claimed_loss_amount=request.claimed_loss_amount,
            fraud_score=fraud_score,
            decision=decision.value,
            reasons_json=json.dumps(reasons),
            rule_flags_json=json.dumps(rule_flags),
            ml_anomaly_score=ml_score,
            processed_at=now,
            is_flagged=is_flagged,
        )
        await save_claim(db, record)

        if is_flagged:
            logger.warning(
                f"🚨 FLAGGED [{claim_id}] user={request.user_id} "
                f"score={fraud_score:.3f} decision={decision.value} flags={rule_flags}"
            )
        else:
            logger.info(
                f"✅ APPROVED [{claim_id}] user={request.user_id} score={fraud_score:.3f}"
            )

        return FraudCheckResponse(
            claim_id=claim_id,
            user_id=request.user_id,
            fraud_score=fraud_score,
            decision=decision,
            reasons=reasons,
            rule_flags=rule_flags,
            ml_anomaly_score=ml_score,
            processed_at=now,
        )


# ─── Decision Logic ───────────────────────────────────────────────────────────

def _make_decision(fraud_score: float) -> Decision:
    """
    Apply threshold rules to convert a fraud score into a decision.
      0.00–0.35 → APPROVE
      0.35–0.65 → REVIEW
      0.65–1.00 → REJECT
    """
    if fraud_score <= settings.RISK_APPROVE_THRESHOLD:
        return Decision.APPROVE
    elif fraud_score <= settings.RISK_REVIEW_THRESHOLD:
        return Decision.REVIEW
    else:
        return Decision.REJECT
