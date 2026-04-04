"""
Parametric Trigger Engine
5 trigger types based on external conditions → automatic payout
Persona: Urban Swiggy delivery partner earning ₹800–₹1200/day (≈₹100/hr)
"""

import random
from datetime import datetime

# Trigger definitions with thresholds and payout ranges
TRIGGERS = {
    "heavy_rain": {
        "name": "Heavy Rain",
        "description": "Rainfall > 50mm in 3 hours",
        "threshold": 50.0,    # mm in 3 hours
        "unit": "mm/3hr",
        "icon": "🌧",
        "base_hours_lost": 4,
        "payout_min": 300,
        "payout_max": 500,
    },
    "aqi_alert": {
        "name": "Pollution Alert",
        "description": "AQI > 300 — outdoor work unsafe",
        "threshold": 300,     # AQI index
        "unit": "AQI",
        "icon": "🌫",
        "base_hours_lost": 3,
        "payout_min": 200,
        "payout_max": 400,
    },
    "zone_shutdown": {
        "name": "Zone Shutdown / Curfew",
        "description": "Government curfew or zone restriction signal",
        "threshold": 1,       # binary: 0/1
        "unit": "signal",
        "icon": "🚫",
        "base_hours_lost": 6,
        "payout_min": 500,
        "payout_max": 800,
    },
    "flood_alert": {
        "name": "Flood / Waterlogging Alert",
        "description": "Waterlogging alert in delivery zone",
        "threshold": 1,       # binary: 0/1
        "unit": "alert",
        "icon": "🌊",
        "base_hours_lost": 5,
        "payout_min": 600,
        "payout_max": 900,
    },
    "platform_outage": {
        "name": "Platform Outage",
        "description": "Swiggy/Zomato API downtime > 60 minutes",
        "threshold": 60,      # minutes
        "unit": "minutes",
        "icon": "📉",
        "base_hours_lost": 2,
        "payout_min": 300,
        "payout_max": 500,
    },
}


def calculate_payout(
    trigger_id: str,
    daily_income: float,
    hours_lost: float,
    weekly_cap: float,
    total_week_payouts: float = 0.0,
    severity_multiplier: float = 1.0
) -> dict:
    """
    Core payout formula:
    Payout = Min(hourly_rate × hours_lost × severity, remaining_cap)

    Args:
        trigger_id: Which trigger activated
        daily_income: Worker's daily earnings (₹)
        hours_lost: Estimated hours work was disrupted
        weekly_cap: Plan weekly maximum payout (₹)
        total_week_payouts: Payouts already received this week by the user
        severity_multiplier: 1.0 = normal, >1 = more severe event
    """
    hourly_rate = daily_income / 8  # 8-hour working day
    gross_loss = hourly_rate * hours_lost * severity_multiplier
    remaining_cap = max(0.0, weekly_cap - total_week_payouts)
    payout = min(round(gross_loss), int(remaining_cap))

    trigger = TRIGGERS.get(trigger_id, {})

    return {
        "trigger_id": trigger_id,
        "trigger_name": trigger.get("name", trigger_id),
        "hourly_rate": round(hourly_rate, 2),
        "hours_lost": hours_lost,
        "gross_income_loss": round(gross_loss, 2),
        "weekly_cap": weekly_cap,
        "remaining_cap": remaining_cap,
        "total_week_payouts": total_week_payouts,
        "payout_amount": payout,
        "payout_capped": gross_loss > remaining_cap,
        "formula": f"Min(₹{round(hourly_rate)}/hr × {hours_lost}hrs, ₹{int(remaining_cap)} remaining cap) = ₹{payout}",
    }


def check_weather_trigger(
    rainfall_mm: float,
    aqi: int,
    zone: str = "HSR Layout",
    flood_alert: bool = False,
    zone_shutdown: bool = False,
    platform_outage_mins: int = 0,
) -> dict:
    """
    Check all parametric conditions and return which triggers activated.
    In production, this uses OpenWeatherMap + AQI APIs.
    For demo/hackathon, values can be simulated.
    """
    activated = []
    timestamp = datetime.utcnow().isoformat()

    # 🌧 Heavy Rain
    if rainfall_mm > TRIGGERS["heavy_rain"]["threshold"]:
        severity = min(rainfall_mm / 50.0, 3.0)
        hours = min(TRIGGERS["heavy_rain"]["base_hours_lost"] * severity, 8)
        activated.append({
            "trigger_id": "heavy_rain",
            "trigger_name": "Heavy Rain",
            "icon": "🌧",
            "value": rainfall_mm,
            "threshold": 50,
            "unit": "mm/3hr",
            "hours_lost": round(hours, 1),
            "severity": round(severity, 2),
        })

    # 🌫 AQI Alert
    if aqi > TRIGGERS["aqi_alert"]["threshold"]:
        severity = min(aqi / 300.0, 2.0)
        hours = TRIGGERS["aqi_alert"]["base_hours_lost"] * severity
        activated.append({
            "trigger_id": "aqi_alert",
            "trigger_name": "AQI Alert",
            "icon": "🌫",
            "value": aqi,
            "threshold": 300,
            "unit": "AQI",
            "hours_lost": round(hours, 1),
            "severity": round(severity, 2),
        })

    # 🌊 Flood Alert
    if flood_alert:
        activated.append({
            "trigger_id": "flood_alert",
            "trigger_name": "Flood Alert",
            "icon": "🌊",
            "value": 1,
            "threshold": 1,
            "unit": "alert",
            "hours_lost": TRIGGERS["flood_alert"]["base_hours_lost"],
            "severity": 1.5,
        })

    # 🚫 Zone Shutdown
    if zone_shutdown:
        activated.append({
            "trigger_id": "zone_shutdown",
            "trigger_name": "Zone Shutdown",
            "icon": "🚫",
            "value": 1,
            "threshold": 1,
            "unit": "signal",
            "hours_lost": TRIGGERS["zone_shutdown"]["base_hours_lost"],
            "severity": 2.0,
        })

    # 📉 Platform Outage
    if platform_outage_mins > TRIGGERS["platform_outage"]["threshold"]:
        hours = platform_outage_mins / 60.0
        activated.append({
            "trigger_id": "platform_outage",
            "trigger_name": "Platform Outage",
            "icon": "📉",
            "value": platform_outage_mins,
            "threshold": 60,
            "unit": "minutes",
            "hours_lost": round(hours, 1),
            "severity": 1.0,
        })

    return {
        "timestamp": timestamp,
        "zone": zone,
        "conditions": {
            "rainfall_mm": rainfall_mm,
            "aqi": aqi,
            "flood_alert": flood_alert,
            "zone_shutdown": zone_shutdown,
            "platform_outage_mins": platform_outage_mins,
        },
        "triggers_activated": activated,
        "any_triggered": len(activated) > 0,
        "trigger_count": len(activated),
    }


def simulate_heavy_rain(zone: str = "Bellandur") -> dict:
    """Demo simulation — generates a random heavy rain event."""
    rainfall = round(random.uniform(55, 120), 1)
    aqi = random.randint(80, 200)
    return check_weather_trigger(
        rainfall_mm=rainfall,
        aqi=aqi,
        zone=zone,
        flood_alert=rainfall > 80
    )
