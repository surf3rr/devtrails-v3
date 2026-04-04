"""
Firestore Seed Script — Populates all collections with realistic initial data.
Run once: python db/seed_firestore.py
"""

import os
import sys
import glob
import time
import firebase_admin
from firebase_admin import credentials, firestore

# ─── Initialize Firebase ──────────────────────────────────────────────────────
def init_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_files = glob.glob(os.path.join(os.path.dirname(__file__), '..', '*firebase-adminsdk*.json'))
        if cred_files:
            cred = credentials.Certificate(cred_files[0])
            firebase_admin.initialize_app(cred)
            print(f"Firebase initialized with: {cred_files[0]}")
        else:
            firebase_admin.initialize_app()
            print("Firebase initialized with default credentials.")
    return firestore.client()


def seed_workers(db):
    print("\n[SEED] Creating workers collection...")
    workers = [
        {"name": "Rahul K.", "platform": "Zomato", "zone": "hsr_layout", "plan": "standard", "upiId": "rahul@okicici", "created_at": int(time.time() * 1000)},
        {"name": "Priya S.", "platform": "Swiggy", "zone": "koramangala", "plan": "pro", "upiId": "priya@oksbi", "created_at": int(time.time() * 1000)},
        {"name": "Amit D.", "platform": "Uber", "zone": "bellandur", "plan": "basic", "upiId": "amit@paytm", "created_at": int(time.time() * 1000)},
        {"name": "Meera R.", "platform": "Zepto", "zone": "bellandur", "plan": "standard", "upiId": "meera@okaxis", "created_at": int(time.time() * 1000)},
        {"name": "Kiran T.", "platform": "Blinkit", "zone": "indiranagar", "plan": "pro", "upiId": "kiran@okhdfc", "created_at": int(time.time() * 1000)},
        {"name": "Suresh M.", "platform": "Zomato", "zone": "btm_layout", "plan": "basic", "upiId": "suresh@oksbi", "created_at": int(time.time() * 1000)},
        {"name": "Divya N.", "platform": "Swiggy", "zone": "jayanagar", "plan": "standard", "upiId": "divya@okicici", "created_at": int(time.time() * 1000)},
    ]
    for w in workers:
        db.collection("workers").document(w["name"].lower().replace(" ", "_").replace(".", "")).set(w)
        print(f"  ✓ Worker: {w['name']} ({w['platform']})")


def seed_claims(db):
    print("\n[SEED] Creating claims collection...")
    now = int(time.time() * 1000)
    day_ms = 86400 * 1000
    claims = [
        {"userId": "Rahul K.", "platform": "Zomato", "event": "Rainfall > 45mm", "zone": "HSR Layout",
         "location": {"lat": 12.9116, "lon": 77.6389}, "ip": "103.21.58.12",
         "trustScore": 0.91, "status": "approved_paid", "amount": 2000,
         "factors": {"location_score": 0.95, "behavioral_score": 1.0, "device_score": 0.95},
         "created_at": now - 2 * day_ms},

        {"userId": "Priya S.", "platform": "Swiggy", "event": "AQI > 320", "zone": "Koramangala",
         "location": {"lat": 12.9352, "lon": 77.6245}, "ip": "49.37.142.88",
         "trustScore": 0.87, "status": "approved_paid", "amount": 2000,
         "factors": {"location_score": 0.90, "behavioral_score": 0.85, "device_score": 0.95},
         "created_at": now - 2 * day_ms},

        {"userId": "Amit D.", "platform": "Uber", "event": "Manual Claim", "zone": "Unknown",
         "location": {"lat": 28.7041, "lon": 77.1025}, "ip": "192.168.1.45",
         "trustScore": 0.22, "status": "flagged", "amount": 0,
         "factors": {"location_score": 0.30, "behavioral_score": 0.10, "device_score": 0.20},
         "created_at": now - 3 * day_ms},

        {"userId": "Meera R.", "platform": "Zepto", "event": "Flood Alert", "zone": "Bellandur",
         "location": {"lat": 12.9249, "lon": 77.6763}, "ip": "117.200.51.33",
         "trustScore": 0.61, "status": "verification_required", "amount": 2000,
         "factors": {"location_score": 0.70, "behavioral_score": 0.55, "device_score": 0.80},
         "created_at": now - 4 * day_ms},

        {"userId": "Kiran T.", "platform": "Blinkit", "event": "Rainfall > 30mm", "zone": "Indiranagar",
         "location": {"lat": 12.9784, "lon": 77.6408}, "ip": "103.87.140.22",
         "trustScore": 0.89, "status": "approved_paid", "amount": 2000,
         "factors": {"location_score": 0.92, "behavioral_score": 0.90, "device_score": 0.95},
         "created_at": now - 5 * day_ms},

        {"userId": "Suresh M.", "platform": "Zomato", "event": "Manual Claim", "zone": "Unknown",
         "location": {"lat": 28.6139, "lon": 77.2090}, "ip": "192.168.1.45",
         "trustScore": 0.18, "status": "flagged", "amount": 0,
         "factors": {"location_score": 0.20, "behavioral_score": 0.10, "device_score": 0.20},
         "created_at": now - 6 * day_ms},

        {"userId": "Divya N.", "platform": "Swiggy", "event": "Rainfall > 25mm", "zone": "Jayanagar",
         "location": {"lat": 12.9299, "lon": 77.5838}, "ip": "103.55.88.14",
         "trustScore": 0.93, "status": "approved_paid", "amount": 2000,
         "factors": {"location_score": 0.98, "behavioral_score": 0.90, "device_score": 0.95},
         "created_at": now - 7 * day_ms},
    ]
    for c in claims:
        db.collection("claims").add(c)
        print(f"  ✓ Claim: {c['userId']} — {c['event']} [{c['status']}]")


def seed_payouts(db):
    print("\n[SEED] Creating payouts collection...")
    now = int(time.time() * 1000)
    day_ms = 86400 * 1000
    payouts = [
        {"claimId": "seed_001", "userId": "Rahul K.", "amount": 2000, "upiId": "rahul@okicici", "status": "processed", "created_at": now - 2 * day_ms},
        {"claimId": "seed_002", "userId": "Priya S.", "amount": 2000, "upiId": "priya@oksbi", "status": "processed", "created_at": now - 2 * day_ms},
        {"claimId": "seed_005", "userId": "Kiran T.", "amount": 2000, "upiId": "kiran@okhdfc", "status": "processed", "created_at": now - 5 * day_ms},
        {"claimId": "seed_007", "userId": "Divya N.", "amount": 2000, "upiId": "divya@okicici", "status": "processed", "created_at": now - 7 * day_ms},
    ]
    for p in payouts:
        db.collection("payouts").add(p)
        print(f"  ✓ Payout: ₹{p['amount']} → {p['userId']}")


def seed_zones(db):
    print("\n[SEED] Creating zones collection...")
    zones = [
        {"name": "Bellandur", "city": "Bangalore", "risk": "HIGH", "premiumAdj": 12, "floodProb": 0.82, "aqiAvg": 245, "trend": "up", "workers": 340, "weekClaims": 32},
        {"name": "BTM Layout", "city": "Bangalore", "risk": "HIGH", "premiumAdj": 10, "floodProb": 0.74, "aqiAvg": 210, "trend": "up", "workers": 520, "weekClaims": 28},
        {"name": "Indiranagar", "city": "Bangalore", "risk": "MEDIUM", "premiumAdj": 3, "floodProb": 0.41, "aqiAvg": 175, "trend": "stable", "workers": 410, "weekClaims": 11},
        {"name": "Koramangala", "city": "Bangalore", "risk": "MEDIUM", "premiumAdj": 5, "floodProb": 0.35, "aqiAvg": 160, "trend": "down", "workers": 680, "weekClaims": 9},
        {"name": "HSR Layout", "city": "Bangalore", "risk": "LOW", "premiumAdj": 0, "floodProb": 0.18, "aqiAvg": 130, "trend": "stable", "workers": 290, "weekClaims": 4},
        {"name": "Jayanagar", "city": "Bangalore", "risk": "LOW", "premiumAdj": -5, "floodProb": 0.12, "aqiAvg": 110, "trend": "down", "workers": 210, "weekClaims": 2},
    ]
    for z in zones:
        doc_id = z["name"].lower().replace(" ", "_")
        db.collection("zones").document(doc_id).set(z)
        print(f"  ✓ Zone: {z['name']} [{z['risk']}]")


def seed_analytics(db):
    print("\n[SEED] Creating analytics collection...")
    weekly = {
        "days": [
            {"day": "Mon", "claims": 12, "fraud": 1, "payouts": 22000},
            {"day": "Tue", "claims": 19, "fraud": 2, "payouts": 36000},
            {"day": "Wed", "claims": 7,  "fraud": 0, "payouts": 12000},
            {"day": "Thu", "claims": 84, "fraud": 5, "payouts": 158000},
            {"day": "Fri", "claims": 14, "fraud": 1, "payouts": 26000},
            {"day": "Sat", "claims": 5,  "fraud": 0, "payouts": 10000},
            {"day": "Sun", "claims": 8,  "fraud": 0, "payouts": 16000},
        ],
        "total_claims": 149,
        "total_fraud": 9,
        "total_payouts": 280000,
        "active_policies": 12450,
        "loss_ratio": 0.68,
        "approval_rate": 0.78,
        "fraud_savings": 18000,
        "avg_payout_time_sec": 1.2,
        "updated_at": int(time.time() * 1000),
    }
    db.collection("analytics").document("weekly_summary").set(weekly)
    print("  ✓ Weekly analytics summary")


def main():
    print("=" * 60)
    print("  ParamedicGuard — Firestore Seed Script")
    print("=" * 60)

    db = init_firebase()

    seed_workers(db)
    seed_claims(db)
    seed_payouts(db)
    seed_zones(db)
    seed_analytics(db)

    print("\n" + "=" * 60)
    print("  ✅ All collections seeded successfully!")
    print("  Check: https://console.firebase.google.com/project/dev-v2-ab30b/firestore")
    print("=" * 60)


if __name__ == "__main__":
    main()
