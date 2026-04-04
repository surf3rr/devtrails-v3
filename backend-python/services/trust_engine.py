import time

def evaluate_trust_score(claim_data: dict) -> dict:
    """
    Python translation of the trust_engine logic.
    """
    import math
    
    def get_distance_km(lat1, lon1, lat2, lon2):
        if not lat1 or not lon1 or not lat2 or not lon2: return 999
        R = 6371
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) * math.sin(dLon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    location_score = 1.0
    behavioral_score = 1.0
    device_score = 1.0

    # 1. Location Integrity
    event_lat, event_lon = 12.9716, 77.5946
    claim_lat = claim_data.get('lat')
    claim_lon = claim_data.get('lon')

    if claim_lat and claim_lon:
        distance = get_distance_km(event_lat, event_lon, float(claim_lat), float(claim_lon))
        if distance > 50:
            location_score = max(0.0, 1.0 - (distance / 500.0))
    else:
        location_score = 0.3

    # 2. Behavioral Signals (Velocity)
    ip_claims_count = claim_data.get('recent_ip_claims', 0)
    if ip_claims_count > 3:
        behavioral_score = 0.1
    elif ip_claims_count > 1:
        behavioral_score = 0.6

    # 3. Device Signals
    user_agent = claim_data.get('user_agent', '').lower()
    if not user_agent or 'bot' in user_agent or 'curl' in user_agent:
        device_score = 0.2
    else:
        device_score = 0.95

    trust_score = (0.5 * location_score) + (0.3 * behavioral_score) + (0.2 * device_score)

    decision = 'flagged'
    if trust_score > 0.8:
        decision = 'instant_payout'
    elif 0.5 <= trust_score <= 0.8:
        decision = 'verification_required'

    return {
        "trustScore": round(trust_score, 2),
        "decision": decision,
        "factors": {
            "location_score": round(location_score, 2),
            "behavioral_score": round(behavioral_score, 2),
            "device_score": round(device_score, 2)
        }
    }
