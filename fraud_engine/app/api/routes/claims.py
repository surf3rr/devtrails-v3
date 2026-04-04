"""
Claims API — POST /check-claim
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.schemas import ClaimRequest, FraudCheckResponse
from app.db.database import AsyncSession, get_db, seed_worker_activity
from app.services.fraud_detector import FraudDetector
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/check-claim", response_model=FraudCheckResponse)
async def check_claim(
    payload: ClaimRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a parametric insurance claim for fraud analysis.

    Returns a fraud score (0–1) and a decision:
    - **APPROVE**: Low fraud risk
    - **REVIEW**: Moderate risk — human review required
    - **REJECT**: High fraud risk — claim denied
    """
    model_manager = request.app.state.model_manager
    detector = FraudDetector(model_manager=model_manager)

    try:
        result = await detector.check_claim(request=payload, db=db)
        return result
    except Exception as e:
        logger.error(f"Error processing claim: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fraud check failed: {str(e)}")


@router.get("/debug/events")
async def debug_events():
    """
    DEBUG ONLY — shows all active mock weather events with their
    time windows and locations. Use this to build valid test payloads.
    """
    weather = WeatherService()
    events = weather.get_all_events()
    now = datetime.now(timezone.utc)

    result = []
    for e in events:
        result.append({
            "event_type": e.event_type,
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "centroid_lat": e.centroid_lat,
            "centroid_lon": e.centroid_lon,
            "radius_km": e.radius_km,
            "severity": e.severity,
            "is_active_now": e.start_time <= now <= e.end_time,
            "sample_payload": {
                "user_id": "test_user_001",
                "timestamp": now.isoformat(),
                "gps_location": {
                    "lat": e.centroid_lat,
                    "lon": e.centroid_lon
                },
                "disruption_type": e.event_type,
                "claimed_loss_amount": 500.0
            }
        })

    return {
        "current_time_utc": now.isoformat(),
        "total_events": len(result),
        "events": result
    }


@router.post("/debug/seed-activity/{user_id}")
async def seed_activity(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    DEBUG ONLY — seeds fake worker activity for a user so the
    worker_activity rule passes during testing.
    """
    await seed_worker_activity(session=db, user_id=user_id, num_days=10)
    return {
        "status": "seeded",
        "user_id": user_id,
        "days_added": 10,
        "message": f"Worker '{user_id}' now has 10 days of activity history."
    }