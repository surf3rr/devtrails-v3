"""
Weather Service — mock data provider simulating a real weather/event API.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class WeatherEvent:
    event_type: str
    start_time: datetime
    end_time: datetime
    centroid_lat: float
    centroid_lon: float
    radius_km: float
    severity: float
    verified: bool = True


def _make_event(event_type, days_ago_start, duration_hours, lat, lon, radius_km, severity):
    """Helper to create events relative to today so they always match."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days_ago_start)
    end = start + timedelta(hours=duration_hours)
    return WeatherEvent(
        event_type=event_type,
        start_time=start,
        end_time=end,
        centroid_lat=lat,
        centroid_lon=lon,
        radius_km=radius_km,
        severity=severity,
    )


def _get_mock_events():
    """Always generates events relative to current time."""
    return [
        _make_event("rain",       days_ago_start=2,  duration_hours=12, lat=12.9716, lon=77.5946, radius_km=30, severity=0.7),   # Bangalore
        _make_event("flood",      days_ago_start=5,  duration_hours=36, lat=19.0760, lon=72.8777, radius_km=25, severity=0.9),   # Mumbai
        _make_event("pollution",  days_ago_start=3,  duration_hours=96, lat=28.6139, lon=77.2090, radius_km=50, severity=0.85),  # Delhi
        _make_event("curfew",     days_ago_start=1,  duration_hours=12, lat=17.3850, lon=78.4867, radius_km=20, severity=1.0),   # Hyderabad
        _make_event("storm",      days_ago_start=4,  duration_hours=36, lat=13.0827, lon=80.2707, radius_km=40, severity=0.8),   # Chennai
        _make_event("heatwave",   days_ago_start=7,  duration_hours=240,lat=21.1458, lon=79.0882, radius_km=60, severity=0.75),  # Nagpur
        _make_event("strike",     days_ago_start=1,  duration_hours=16, lat=22.5726, lon=88.3639, radius_km=35, severity=0.6),   # Kolkata
        _make_event("earthquake", days_ago_start=6,  duration_hours=2,  lat=23.0225, lon=72.5714, radius_km=45, severity=0.95), # Ahmedabad
    ]


class WeatherService:

    def find_matching_event(
        self,
        disruption_type: str,
        claim_timestamp: datetime,
        claim_lat: float,
        claim_lon: float,
    ) -> Optional[WeatherEvent]:

        if claim_timestamp.tzinfo is None:
            claim_timestamp = claim_timestamp.replace(tzinfo=timezone.utc)

        MOCK_EVENTS = _get_mock_events()

        candidates = [
            e for e in MOCK_EVENTS
            if e.event_type == disruption_type
            and e.start_time <= claim_timestamp <= e.end_time
        ]

        if not candidates:
            logger.warning(
                f"No weather event found for type='{disruption_type}' "
                f"at timestamp={claim_timestamp.isoformat()}"
            )
            return None

        def distance_to(event: WeatherEvent) -> float:
            return _haversine(claim_lat, claim_lon, event.centroid_lat, event.centroid_lon)

        return min(candidates, key=distance_to)

    def get_all_events(self) -> list:
        return _get_mock_events()


def _haversine(lat1, lon1, lat2, lon2) -> float:
    import math
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
