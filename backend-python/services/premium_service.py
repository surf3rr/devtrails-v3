"""
Premium Service - Parametric Micro-Insurance
Plans: Basic ₹29/week (₹500 cap), Standard ₹49/week (₹1000 cap), Pro ₹79/week (₹1500 cap)
Dynamic pricing based on zone risk, weather history, AQI
"""

PLANS = {
    "basic":    {"weekly_premium": 29, "weekly_cap": 500,  "label": "Basic"},
    "standard": {"weekly_premium": 49, "weekly_cap": 1000, "label": "Standard"},
    "pro":      {"weekly_premium": 79, "weekly_cap": 1500, "label": "Pro"},
}

# Zone-based dynamic pricing adjustments (₹/week)
ZONE_ADJUSTMENTS = {
    "bellandur":    +12,  # High flood risk
    "btm_layout":   +10,  # High waterlogging
    "koramangala":  +5,   # Moderate rain risk
    "indiranagar":  +3,
    "hsr_layout":   0,    # Baseline zone
    "jayanagar":    -5,   # Low risk, dry zone
    "whitefield":   +8,   # AQI risk
    "hebbal":       +6,   # Flood prone
}

# Platform riders (Swiggy/Zomato = outdoor, higher risk)
PLATFORM_ADJUSTMENTS = {
    "swiggy":   +3,
    "zomato":   +3,
    "zepto":    +5,   # High frequency, more exposure
    "blinkit":  +5,
    "amazon":   +2,
    "flipkart": +2,
    "ola":      +2,
    "uber":     +2,
    "dunzo":    +4,
}

def calculate_premium(
    plan: str = "standard",
    zone: str = "hsr_layout",
    platform: str = "swiggy",
    aqi_risk: float = 0.0,       # 0–1 multiplier for historical AQI
    disruption_frequency: float = 0.0  # historical disruptions per month
) -> dict:
    """
    Dynamic premium calculation for parametric micro-insurance.
    Returns full breakdown of pricing components.
    """
    plan = plan.lower()
    if plan not in PLANS:
        plan = "standard"

    base = PLANS[plan]
    base_premium = base["weekly_premium"]
    weekly_cap = base["weekly_cap"]

    # Zone adjustment
    zone_adj = ZONE_ADJUSTMENTS.get(zone.lower().replace(" ", "_"), 0)

    # Platform adjustment
    platform_adj = PLATFORM_ADJUSTMENTS.get(platform.lower(), 0)

    # AQI load (e.g. 0.3 = add ₹3 for medium AQI exposure)
    aqi_load = round(aqi_risk * 10)

    # Disruption load (historical frequency penalty)
    freq_load = round(disruption_frequency * 2)

    dynamic_adjustment = zone_adj + platform_adj + aqi_load + freq_load
    final_premium = base_premium + dynamic_adjustment

    # Enforce non-negative
    final_premium = max(final_premium, 10)

    return {
        "plan": base["label"],
        "weekly_premium": final_premium,
        "base_premium": base_premium,
        "weekly_cap": weekly_cap,
        "adjustments": {
            "zone": zone_adj,
            "platform": platform_adj,
            "aqi_load": aqi_load,
            "disruption_load": freq_load,
            "total": dynamic_adjustment,
        },
        "coverage": {
            "heavy_rain":      f"₹300–₹{min(500, weekly_cap)} per event",
            "aqi_alert":       f"₹200–₹{min(400, weekly_cap)} per event",
            "zone_shutdown":   f"₹500–₹{min(800, weekly_cap)} per event",
            "flood_alert":     f"₹600–₹{min(weekly_cap, weekly_cap)} per event",
            "platform_outage": f"₹300–₹{min(500, weekly_cap)} per event",
        }
    }


def get_all_plans() -> list:
    """Return all available plan tiers for display."""
    return [
        {
            "id": k,
            "label": v["label"],
            "weekly_premium": v["weekly_premium"],
            "weekly_cap": v["weekly_cap"],
            "triggers": 5 if k == "pro" else (4 if k == "standard" else 3),
            "features": _plan_features(k),
        }
        for k, v in PLANS.items()
    ]


def _plan_features(plan: str) -> list:
    base = [
        "Heavy rain trigger (>50mm)",
        "AQI alert trigger (>300)",
        "Flood alert trigger",
    ]
    if plan in ("standard", "pro"):
        base.append("Zone shutdown trigger")
    if plan == "pro":
        base.append("Platform outage trigger")
        base.append("Priority claim processing")
    return base
