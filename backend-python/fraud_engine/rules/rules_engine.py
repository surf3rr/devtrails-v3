"""
Rules Engine — deterministic fraud checks.
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fraud_engine.core.config import settings
from fraud_engine.core.schemas import ClaimRequest
from fraud_engine.services.weather_service import WeatherEvent

logger = logging.getLogger(__name__)


@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    reason_code: str
    weight: float
    detail: str = ""


# ─── Individual Rules ─────────────────────────────────────────────────────────

def check_gps_location(
    request: ClaimRequest,
    weather_event: Optional[WeatherEvent],
) -> RuleResult:
    if weather_event is None:
        return RuleResult(
            rule_name="gps_location",
            passed=False,
            reason_code="no_weather_event_found",
            weight=0.9,
            detail="No verified disruption event found for this type/time.",
        )

    distance_km = _haversine(
        request.gps_location.lat, request.gps_location.lon,
        weather_event.centroid_lat, weather_event.centroid_lon,
    )

    max_km = weather_event.radius_km + settings.MAX_LOCATION_DEVIATION_KM
    passed = distance_km <= max_km

    return RuleResult(
        rule_name="gps_location",
        passed=passed,
        reason_code="location_verified" if passed else "gps_outside_disruption_zone",
        weight=0.85,
        detail=f"Worker is {distance_km:.1f} km from event centroid (limit: {max_km:.1f} km).",
    )


def check_time_anomaly(
    request: ClaimRequest,
    weather_event: Optional[WeatherEvent],
    submission_time: Optional[datetime] = None,
) -> RuleResult:
    now = submission_time or datetime.now(timezone.utc)

    claim_ts = request.timestamp
    if claim_ts.tzinfo is None:
        claim_ts = claim_ts.replace(tzinfo=timezone.utc)

    if claim_ts > now:
        return RuleResult(
            rule_name="time_anomaly",
            passed=False,
            reason_code="future_event_timestamp",
            weight=0.95,
            detail="Claim timestamp is set in the future.",
        )

    if weather_event is None:
        return RuleResult(
            rule_name="time_anomaly",
            passed=True,
            reason_code="time_check_skipped",
            weight=0.0,
            detail="No event found; time check skipped.",
        )

    event_end = weather_event.end_time
    hours_after_event = (now - event_end).total_seconds() / 3600

    if claim_ts < weather_event.start_time:
        return RuleResult(
            rule_name="time_anomaly",
            passed=False,
            reason_code="claim_before_event",
            weight=1.0,
            detail="Claim timestamp precedes the disruption event start.",
        )

    if hours_after_event > settings.MAX_CLAIM_HOURS_AFTER_EVENT:
        return RuleResult(
            rule_name="time_anomaly",
            passed=False,
            reason_code="claim_filed_too_late",
            weight=0.6,
            detail=f"Claim filed {hours_after_event:.1f}h after event (max: {settings.MAX_CLAIM_HOURS_AFTER_EVENT}h).",
        )

    return RuleResult(
        rule_name="time_anomaly",
        passed=True,
        reason_code="valid_claim_timing",
        weight=0.0,
        detail=f"Claim filed {hours_after_event:.1f}h after event end (within window).",
    )


def check_duplicate_claim(
    request: ClaimRequest,
    recent_claims: List,
) -> RuleResult:
    existing = [c for c in recent_claims if c.claim_id is not None]

    if existing:
        return RuleResult(
            rule_name="duplicate_claim",
            passed=False,
            reason_code="duplicate_claim_detected",
            weight=0.9,
            detail=f"Found {len(existing)} existing claim(s) for this user/event.",
        )

    return RuleResult(
        rule_name="duplicate_claim",
        passed=True,
        reason_code="no_duplicate_found",
        weight=0.0,
        detail="No duplicate claims detected.",
    )


def check_worker_activity(
    request: ClaimRequest,
    active_days: int,
) -> RuleResult:
    min_days = settings.MIN_ACTIVE_DAYS_BEFORE_CLAIM

    if active_days == 0:
        return RuleResult(
            rule_name="worker_activity",
            passed=False,
            reason_code="no_prior_activity",
            weight=0.8,
            detail="Worker has no recorded activity before the disruption event.",
        )

    if active_days < min_days:
        return RuleResult(
            rule_name="worker_activity",
            passed=False,
            reason_code="insufficient_prior_activity",
            weight=0.5,
            detail=f"Worker only active {active_days} day(s) before event (min: {min_days}).",
        )

    return RuleResult(
        rule_name="worker_activity",
        passed=True,
        reason_code="activity_verified",
        weight=0.0,
        detail=f"Worker has {active_days} active day(s) on record.",
    )


def check_weather_match(
    request: ClaimRequest,
    weather_event: Optional[WeatherEvent],
) -> RuleResult:
    if weather_event is None:
        return RuleResult(
            rule_name="weather_match",
            passed=False,
            reason_code="weather_event_not_verified",
            weight=0.75,
            detail="Could not verify disruption against weather database.",
        )

    if weather_event.event_type != request.disruption_type.value:
        return RuleResult(
            rule_name="weather_match",
            passed=False,
            reason_code="weather_type_mismatch",
            weight=0.85,
            detail=(
                f"Claimed '{request.disruption_type.value}' but "
                f"only '{weather_event.event_type}' recorded at that time."
            ),
        )

    return RuleResult(
        rule_name="weather_match",
        passed=True,
        reason_code="valid_weather_event",
        weight=0.0,
        detail=f"Weather event '{weather_event.event_type}' confirmed (severity: {weather_event.severity}).",
    )


def check_loss_amount(
    request: ClaimRequest,
    weather_event: Optional[WeatherEvent],
) -> RuleResult:
    amount = request.claimed_loss_amount
    severity = weather_event.severity if weather_event else 0.5
    expected_max = 500 + (severity * 2000)

    if amount > expected_max * 2:
        return RuleResult(
            rule_name="loss_amount",
            passed=False,
            reason_code="excessive_claimed_loss",
            weight=0.65,
            detail=f"Claimed ${amount:.2f} far exceeds expected max (${expected_max:.2f}) for severity {severity:.2f}.",
        )

    return RuleResult(
        rule_name="loss_amount",
        passed=True,
        reason_code="reasonable_loss_amount",
        weight=0.0,
        detail=f"Claimed ${amount:.2f} within expected range for severity {severity:.2f}.",
    )


def check_syndicate_burst(
    request: ClaimRequest,
    recent_area_claims: int,
    burst_threshold: int = 5,
) -> RuleResult:
    if recent_area_claims >= burst_threshold:
        return RuleResult(
            rule_name="syndicate_burst",
            passed=False,
            reason_code="syndicate_burst_detected",
            weight=0.85,
            detail=(
                f"Detected {recent_area_claims} claims from same area "
                f"in short window (threshold: {burst_threshold})."
            ),
        )

    return RuleResult(
        rule_name="syndicate_burst",
        passed=True,
        reason_code="no_syndicate_detected",
        weight=0.0,
        detail=f"Only {recent_area_claims} claims from this area — within normal range.",
    )


# ─── Rules Engine ─────────────────────────────────────────────────────────────

class RulesEngine:

    def evaluate(
        self,
        request: ClaimRequest,
        weather_event: Optional[WeatherEvent],
        recent_claims: List,
        active_days: int,
        submission_time: Optional[datetime] = None,
        recent_area_claims: int = 0,
    ) -> Tuple[float, List[str], List[str]]:

        results: List[RuleResult] = [
            check_gps_location(request, weather_event),
            check_time_anomaly(request, weather_event, submission_time),
            check_duplicate_claim(request, recent_claims),
            check_worker_activity(request, active_days),
            check_weather_match(request, weather_event),
            check_loss_amount(request, weather_event),
            check_syndicate_burst(request, recent_area_claims),
        ]

        reasons = []
        flags = []
        weighted_risk = 0.0

        for r in results:
            logger.debug(f"Rule [{r.rule_name}] -> {'PASS' if r.passed else 'FAIL'} | {r.reason_code}")
            if r.passed:
                reasons.append(r.reason_code)
            else:
                flags.append(r.reason_code)
                weighted_risk += r.weight

        max_possible = sum(r.weight for r in results)
        rule_score = min(weighted_risk / max_possible, 1.0) if max_possible > 0 else 0.0

        logger.info(
            f"Rules evaluation: score={rule_score:.3f} | "
            f"flags={flags} | reasons={reasons}"
        )
        return rule_score, reasons, flags


# ─── Haversine ────────────────────────────────────────────────────────────────

def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
