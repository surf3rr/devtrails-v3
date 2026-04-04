"""
History API — GET /fraud-history/{user_id}
             GET /explain/{claim_id}
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.schemas import FraudHistoryResponse, ClaimHistoryItem
from app.db.database import AsyncSession, get_db, get_claims_by_user, get_claim_by_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/fraud-history/{user_id}", response_model=FraudHistoryResponse)
async def get_fraud_history(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve the full fraud check history for a specific gig worker.
    Includes per-claim scores, decisions, and aggregate statistics.
    """
    records = await get_claims_by_user(db, user_id=user_id)

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No fraud history found for user '{user_id}'.",
        )

    flagged = [r for r in records if r.is_flagged]
    avg_score = round(sum(r.fraud_score for r in records) / len(records), 4)

    claims = [
        ClaimHistoryItem(
            claim_id=r.claim_id,
            timestamp=r.timestamp,
            disruption_type=r.disruption_type,
            claimed_loss_amount=r.claimed_loss_amount,
            fraud_score=r.fraud_score,
            decision=r.decision,
            reasons=json.loads(r.reasons_json or "[]"),
            processed_at=r.processed_at,
        )
        for r in records
    ]

    return FraudHistoryResponse(
        user_id=user_id,
        total_claims=len(records),
        flagged_claims=len(flagged),
        average_fraud_score=avg_score,
        claims=claims,
    )


@router.get("/explain/{claim_id}")
async def explain_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a human-readable explanation of exactly why a claim
    received its fraud score and decision.

    Great for auditing, transparency, and hackathon demos.
    """
    record = await get_claim_by_id(db, claim_id=claim_id)

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Claim '{claim_id}' not found.",
        )

    reasons = json.loads(record.reasons_json or "[]")
    flags   = json.loads(record.rule_flags_json or "[]")

    # ── Build human-readable explanations for each flag ───────────────────
    flag_explanations = {
        "no_weather_event_found":      "No verified weather event matched this disruption type and timestamp.",
        "gps_outside_disruption_zone": "Worker's GPS location was outside the expected disruption zone.",
        "future_event_timestamp":      "The claim timestamp was set in the future — likely manipulated.",
        "claim_before_event":          "The claim was filed before the disruption event started.",
        "claim_filed_too_late":        "The claim was filed too long after the event ended.",
        "duplicate_claim_detected":    "This user already filed a claim for the same disruption event.",
        "no_prior_activity":           "Worker has no recorded activity before the disruption (possible ghost account).",
        "insufficient_prior_activity": "Worker had very little activity history before the event.",
        "weather_event_not_verified":  "The disruption type could not be verified against weather records.",
        "weather_type_mismatch":       "The claimed disruption type does not match the recorded weather event.",
        "excessive_claimed_loss":      "The claimed loss amount is disproportionately high for this event severity.",
        "syndicate_burst_detected":    "Multiple claims were detected from the same area in a short time window — possible coordinated fraud.",
    }

    reason_explanations = {
        "location_verified":      "Worker's GPS is within the verified disruption zone.",
        "valid_claim_timing":     "Claim was filed within the valid time window after the event.",
        "no_duplicate_found":     "No duplicate claims found for this user and event.",
        "activity_verified":      "Worker has sufficient activity history before the disruption.",
        "valid_weather_event":    "Disruption type is confirmed by verified weather records.",
        "reasonable_loss_amount": "Claimed loss amount is proportionate to the event severity.",
        "no_syndicate_detected":  "No coordinated fraud pattern detected in this area.",
        "time_check_skipped":     "Time check was skipped because no matching event was found.",
    }

    # ── Risk level label ──────────────────────────────────────────────────
    score = record.fraud_score
    if score <= 0.35:
        risk_level = "LOW"
        risk_summary = "This claim appears legitimate. All or most checks passed."
    elif score <= 0.65:
        risk_level = "MEDIUM"
        risk_summary = "This claim has some suspicious signals. Manual review recommended."
    else:
        risk_level = "HIGH"
        risk_summary = "This claim has multiple fraud indicators. Likely fraudulent."

    # ── Score breakdown ───────────────────────────────────────────────────
    rule_score  = round(score / 0.65, 4) if score > 0 else 0  # approximate
    ml_score    = record.ml_anomaly_score or 0.0

    return {
        "claim_id":        record.claim_id,
        "user_id":         record.user_id,
        "decision":        record.decision,
        "fraud_score":     score,
        "risk_level":      risk_level,
        "risk_summary":    risk_summary,
        "processed_at":    record.processed_at,

        "score_breakdown": {
            "rule_engine_weight": "65%",
            "ml_engine_weight":   "35%",
            "ml_anomaly_score":   round(ml_score, 4),
            "final_score":        score,
        },

        "passed_checks": [
            {
                "check": r,
                "explanation": reason_explanations.get(r, r)
            }
            for r in reasons
        ],

        "failed_checks": [
            {
                "check": f,
                "explanation": flag_explanations.get(f, f),
                "severity": _flag_severity(f),
            }
            for f in flags
        ],

        "claim_details": {
            "disruption_type":     record.disruption_type,
            "claimed_loss_amount": record.claimed_loss_amount,
            "gps_lat":             record.gps_lat,
            "gps_lon":             record.gps_lon,
            "event_timestamp":     record.timestamp,
        },
    }


def _flag_severity(flag: str) -> str:
    """Return severity level for each flag type."""
    high = {
        "future_event_timestamp",
        "claim_before_event",
        "no_weather_event_found",
        "syndicate_burst_detected",
        "duplicate_claim_detected",
    }
    medium = {
        "gps_outside_disruption_zone",
        "weather_event_not_verified",
        "weather_type_mismatch",
        "excessive_claimed_loss",
        "no_prior_activity",
    }
    if flag in high:
        return "HIGH"
    elif flag in medium:
        return "MEDIUM"
    return "LOW"