from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import razorpay
import hmac, hashlib, time

from services import premium_service, trigger_service, claims_service
from db.database import get_firestore_client

router = APIRouter()

# ─── Razorpay Client ──────────────────────────────────────────────────────────
RZP_KEY_ID = 'rzp_test_SZTRH39KNoZTLr'
RZP_KEY_SECRET = 'cBcDe0W3URwyZe1c925luque'
rzp_client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

class PremiumCalculateRequest(BaseModel):
    plan: str = "standard"
    zone: str = "hsr_layout"
    platform: str = "swiggy"
    aqi_risk: float = 0.0
    disruption_frequency: float = 0.0

class ClaimSubmitRequest(BaseModel):
    userId: str = 'Worker'
    platform: str = 'Unknown'
    lat: float
    lon: float
    upiId: str = 'test@tx'

# ─── Premium ──────────────────────────────────────────────────────────────────
@router.post("/premium/calculate")
async def calculate_premium(req: PremiumCalculateRequest):
    try:
        result = premium_service.calculate_premium(**req.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─── Events ───────────────────────────────────────────────────────────────────
@router.get("/events/check")
async def check_event(lat: float = 12.9716, lon: float = 77.5946):
    try:
        result = await trigger_service.check_weather_event(lat, lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Claims ───────────────────────────────────────────────────────────────────
@router.post("/claims/submit")
async def submit_claim(req: ClaimSubmitRequest, request: Request):
    try:
        ip = request.client.host
        user_agent = request.headers.get('user-agent', '')

        payload = req.model_dump()
        payload['ip'] = ip
        payload['userAgent'] = user_agent

        result = await claims_service.submit_claim(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# IMPORTANT: /claims/all MUST come BEFORE /claims/{user_id}
@router.get("/claims/all")
async def get_all_claims():
    """Fetch all claims from Firestore for the admin portal."""
    try:
        claims = await claims_service.get_all_claims()
        return {"claims": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/{user_id}")
async def get_user_claims(user_id: str):
    try:
        claims = await claims_service.get_claims(user_id)
        return {"claims": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Plans ────────────────────────────────────────────────────────────────────
@router.get("/plans")
async def get_plans():
    try:
        plans = premium_service.get_all_plans()
        return {"plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Zones ────────────────────────────────────────────────────────────────────
@router.get("/zones")
async def get_zones():
    """Fetch all zone risk data from Firestore."""
    try:
        db = get_firestore_client()
        docs = db.collection("zones").stream()
        zones = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            zones.append(data)
        return {"zones": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Analytics ────────────────────────────────────────────────────────────────
@router.get("/analytics/weekly")
async def get_weekly_analytics():
    """Fetch weekly analytics summary from Firestore."""
    try:
        db = get_firestore_client()
        doc = db.collection("analytics").document("weekly_summary").get()
        if doc.exists:
            return doc.to_dict()
        return {"days": [], "total_claims": 0, "total_fraud": 0, "total_payouts": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Workers ──────────────────────────────────────────────────────────────────
@router.get("/workers")
async def get_workers():
    """Fetch all registered workers from Firestore."""
    try:
        db = get_firestore_client()
        docs = db.collection("workers").stream()
        workers = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            workers.append(data)
        return {"workers": workers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Razorpay Payments ────────────────────────────────────────────────────────
class CreateOrderRequest(BaseModel):
    planId: str
    planLabel: str
    amount: int  # in rupees
    userId: str = 'Worker'

@router.post("/payment/create-order")
async def create_razorpay_order(req: CreateOrderRequest):
    """Create a Razorpay order for plan subscription."""
    try:
        order_data = {
            "amount": req.amount * 100,  # Razorpay expects amount in paise
            "currency": "INR",
            "receipt": f"plan_{req.planId}_{int(time.time())}",
            "notes": {
                "plan": req.planId,
                "planLabel": req.planLabel,
                "userId": req.userId
            }
        }
        order = rzp_client.order.create(data=order_data)
        return {
            "orderId": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "keyId": RZP_KEY_ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    planId: str
    userId: str = 'Worker'
    amount: int = 0

@router.post("/payment/verify")
async def verify_razorpay_payment(req: VerifyPaymentRequest):
    """Verify Razorpay payment signature and activate the plan."""
    try:
        # Verify signature
        params = {
            'razorpay_order_id': req.razorpay_order_id,
            'razorpay_payment_id': req.razorpay_payment_id,
            'razorpay_signature': req.razorpay_signature
        }
        rzp_client.utility.verify_payment_signature(params)

        # Store payment record in Firestore
        db = get_firestore_client()
        db.collection("payments").add({
            "orderId": req.razorpay_order_id,
            "paymentId": req.razorpay_payment_id,
            "planId": req.planId,
            "userId": req.userId,
            "amount": req.amount,
            "status": "paid",
            "created_at": int(time.time() * 1000)
        })

        return {"status": "success", "message": f"Payment verified. {req.planId} plan activated!"}
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment signature verification failed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
