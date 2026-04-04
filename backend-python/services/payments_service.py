import asyncio
import random
import time
from db.database import get_firestore_client

async def process_upi_payout(claim_id: str, amount: float, upi_id: str) -> dict:
    print(f"[PAYMENTS] Initiating Razorpay UPI payout of ₹{amount} to {upi_id}...")

    # Simulate network delay
    await asyncio.sleep(1.5)

    response = {
        "payout_id": f"pout_{random.randint(1000, 9999)}",
        "status": "processed",
        "mode": "UPI",
        "amount": amount,
        "fund_account_id": "fa_mocked123"
    }

    # Update claim status
    db = get_firestore_client()
    try:
        db.collection("claims").document(claim_id).update({
            "status": "approved_paid",
            "amount": amount,
            "updated_at": int(time.time() * 1000)
        })
        print(f"[PAYMENTS] Claim {claim_id} marked as PAID.")
    except Exception as e:
        print(f"Error updating claim status: {e}")

    return response
