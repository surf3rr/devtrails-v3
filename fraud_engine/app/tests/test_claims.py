"""
Test suite — integration tests for the Fraud Detection Engine.
Run with: python app/tests/test_claims.py (requires server running on :8000)
"""

import json
import sys
from datetime import datetime, timezone, timedelta

import requests

BASE_URL = "http://127.0.0.1:8000/api"

# ─── Helpers ──────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ts(days_ago: float) -> str:
    """Return an ISO timestamp N days ago (always within event windows)."""
    t = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return t.isoformat()

def print_result(name: str, response: dict, expected_decision: str = None):
    score    = response.get("fraud_score", 0)
    decision = response.get("decision", "?")
    reasons  = response.get("reasons", [])
    flags    = response.get("rule_flags", [])

    color = GREEN if decision == "APPROVE" else (YELLOW if decision == "REVIEW" else RED)
    match = ""
    if expected_decision:
        match = (
            f" {GREEN}PASS{RESET}"
            if decision == expected_decision
            else f" {RED}FAIL (expected {expected_decision}){RESET}"
        )

    print(f"\n{BOLD}{CYAN}-- {name} --{RESET}")
    print(f"  Score:    {color}{score:.3f}{RESET}")
    print(f"  Decision: {color}{BOLD}{decision}{RESET}{match}")
    if reasons:
        print(f"  Reasons:  {GREEN}{', '.join(reasons)}{RESET}")
    if flags:
        print(f"  Flags:    {RED}{', '.join(flags)}{RESET}")

def post_claim(payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/check-claim", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def seed_user(user_id: str):
    """Seed activity for a user so worker_activity rule passes."""
    requests.post(f"{BASE_URL}/debug/seed-activity/{user_id}", timeout=10)

# ─── Test Cases ───────────────────────────────────────────────────────────────

def test_clean_pollution_claim():
    """Legitimate claim — Nagpur heatwave, seeded worker, reasonable loss."""
    uid = f"test_clean_{datetime.now().microsecond}"
    seed_user(uid)
    result = post_claim({
        "user_id": uid,
        "timestamp": ts(3),
        "gps_location": {"lat": 21.1458, "lon": 79.0882},
        "disruption_type": "heatwave",
        "claimed_loss_amount": 200.00,
    })
    print_result("Clean Legitimate Claim (APPROVE)", result, expected_decision="APPROVE")
    return result


def test_clean_heatwave_claim():
    """Legitimate claim — Nagpur heatwave, different user."""
    uid = f"test_heatwave_{datetime.now().microsecond}"
    seed_user(uid)
    result = post_claim({
        "user_id": uid,
        "timestamp": ts(3),
        "gps_location": {"lat": 21.1458, "lon": 79.0882},
        "disruption_type": "heatwave",
        "claimed_loss_amount": 300.00,
    })
    print_result("Clean Heatwave Claim (APPROVE)", result, expected_decision="APPROVE")
    return result


def test_gps_far_from_zone():
    """Worker GPS is far from the disruption zone — London claiming Delhi pollution."""
    result = post_claim({
        "user_id": "test_gps_bad_001",
        "timestamp": ts(1.5),
        "gps_location": {"lat": 51.5074, "lon": -0.1278},  # London
        "disruption_type": "pollution",
        "claimed_loss_amount": 200.00,
    })
    print_result("GPS Far From Zone (REJECT)", result, expected_decision="REJECT")
    return result


def test_wrong_disruption_type():
    """Claiming earthquake when only pollution is on record for Delhi."""
    result = post_claim({
        "user_id": "test_wrong_type_001",
        "timestamp": ts(1.5),
        "gps_location": {"lat": 28.6139, "lon": 77.2090},
        "disruption_type": "earthquake",
        "claimed_loss_amount": 500.00,
    })
    print_result("Wrong Disruption Type (REJECT)", result, expected_decision="REJECT")
    return result


def test_excessive_loss():
    """Claimed amount is disproportionately high for the event severity."""
    seed_user("test_excess_001")
    result = post_claim({
        "user_id": "test_excess_001",
        "timestamp": ts(1.5),
        "gps_location": {"lat": 28.6139, "lon": 77.2090},
        "disruption_type": "pollution",
        "claimed_loss_amount": 9500.00,
    })
    print_result("Excessive Loss Amount (REVIEW or REJECT)", result)
    return result


def test_no_worker_activity():
    """Brand new user with no activity history — ghost account."""
    result = post_claim({
        "user_id": f"ghost_user_{datetime.now().microsecond}",  # unique each run
        "timestamp": ts(1.5),
        "gps_location": {"lat": 28.6139, "lon": 77.2090},
        "disruption_type": "pollution",
        "claimed_loss_amount": 200.00,
    })
    print_result("No Prior Activity (REVIEW)", result, expected_decision="REVIEW")
    return result


def test_future_timestamp():
    """Claim timestamp set in the future."""
    result = post_claim({
        "user_id": "test_future_001",
        "timestamp": ts(-2),   # negative = 2 days in the future
        "gps_location": {"lat": 28.6139, "lon": 77.2090},
        "disruption_type": "pollution",
        "claimed_loss_amount": 200.00,
    })
    print_result("Future Timestamp (REJECT)", result, expected_decision="REJECT")
    return result


def test_history(user_id: str = "test_clean_001"):
    """Retrieve fraud history for a user."""
    r = requests.get(f"{BASE_URL}/fraud-history/{user_id}", timeout=10)
    if r.status_code == 404:
        print(f"\n{YELLOW}No history found for {user_id}{RESET}")
        return
    r.raise_for_status()
    data = r.json()
    print(f"\n{BOLD}{CYAN}-- Fraud History: {user_id} --{RESET}")
    print(f"  Total Claims:  {data['total_claims']}")
    print(f"  Flagged:       {data['flagged_claims']}")
    print(f"  Avg Score:     {data['average_fraud_score']:.3f}")


def test_train_model():
    """Trigger model retraining."""
    r = requests.post(f"{BASE_URL}/train-model", timeout=30)
    r.raise_for_status()
    data = r.json()
    print(f"\n{BOLD}{CYAN}-- Model Training --{RESET}")
    print(f"  Status:   {GREEN}{data['status']}{RESET}")
    print(f"  Samples:  {data['samples_used']}")
    print(f"  Version:  {data['model_version']}")


# ─── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Fraud Detection Engine - Integration Tests{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    try:
        health = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"\n{GREEN}Server is running{RESET}")
    except Exception:
        print(f"\n{RED}Server not running. Start with: uvicorn main:app --reload{RESET}")
        sys.exit(1)

    test_clean_pollution_claim()
    test_clean_heatwave_claim()
    test_gps_far_from_zone()
    test_wrong_disruption_type()
    test_excessive_loss()
    test_no_worker_activity()
    test_future_timestamp()
    test_train_model()
    test_history("test_user_002")

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{GREEN}{BOLD}All tests complete.{RESET}\n")