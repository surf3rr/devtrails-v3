import time
from db.database import get_firestore_client
from services.trust_engine import evaluate_trust_score
from services.payments_service import process_upi_payout

async def submit_claim(payload: dict) -> dict:
    user_id = payload.get('userId')
    platform = payload.get('platform', 'Unknown')
    lat = payload.get('lat')
    lon = payload.get('lon')
    ip = payload.get('ip')
    user_agent = payload.get('userAgent')
    upi_id = payload.get('upiId')

    # 1. Evaluate trust parameters
    claim_evaluation_data = {
        'lat': lat,
        'lon': lon,
        'ip': ip,
        'user_agent': user_agent,
        'recent_ip_claims': 0
    }
    evaluation = evaluate_trust_score(claim_evaluation_data)

    # 2. Determine event type based on trust decision
    if evaluation["decision"] == "flagged":
        event = "Manual Claim"
        zone = "Unknown"
    else:
        event = "Parametric Trigger"
        zone = "HSR Layout"

    # 3. Create claim record with full data
    db = get_firestore_client()
    claim_data = {
        "userId": user_id,
        "platform": platform,
        "event": event,
        "zone": zone,
        "location": {"lat": lat, "lon": lon},
        "ip": ip,
        "upiId": upi_id,
        "trustScore": evaluation["trustScore"],
        "status": evaluation["decision"],
        "amount": 0.0,
        "factors": evaluation["factors"],
        "created_at": int(time.time() * 1000)
    }

    _, doc_ref = db.collection("claims").add(claim_data)
    claim_id = doc_ref.id

    # 4. Automated action based on decision
    payment_result = None
    if evaluation["decision"] == 'instant_payout':
        total_week_payouts = 0
        try:
            week_ago = int((time.time() - 7 * 86400) * 1000)
            past_claims = db.collection("claims").where("userId", "==", user_id).where("created_at", ">", week_ago).where("status", "==", "approved_paid").stream()
            total_week_payouts = sum([doc.to_dict().get("amount", 0) for doc in past_claims])
        except Exception as e:
            print(f"[WARN] Compound Firestore query failed (composite index may be needed): {e}")
            total_week_payouts = 0
        
        from services.trigger_service import calculate_payout
        payout_info = calculate_payout("heavy_rain", 1000.0, 4, 1500, total_week_payouts)
        payout_amount = payout_info["payout_amount"]
        
        if payout_amount > 0:
            payment_result = await process_upi_payout(claim_id, payout_amount, upi_id)
            # Also record the payout
            db.collection("payouts").add({
                "claimId": claim_id,
                "userId": user_id,
                "amount": payout_amount,
                "upiId": upi_id,
                "status": "processed",
                "created_at": int(time.time() * 1000)
            })
        else:
            evaluation["decision"] = "cap_reached"

    return {
        "claimId": claim_id,
        "trustScore": evaluation["trustScore"],
        "decision": evaluation["decision"],
        "factors": evaluation["factors"],
        "paymentResult": payment_result
    }

async def get_claims(user_id: str) -> list:
    db = get_firestore_client()
    docs = db.collection("claims").where("userId", "==", user_id).stream()
    claims = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        claims.append(data)
    return claims

async def get_all_claims() -> list:
    """Fetch all claims from Firestore (for admin portal)."""
    db = get_firestore_client()
    docs = db.collection("claims").stream()
    claims = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        claims.append(data)
    return claims
