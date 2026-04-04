"""
Pydantic schemas — request/response contracts for the Fraud Detection API.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ────────────────────────────────────────────────────────────────────

class DisruptionType(str, Enum):
    RAIN = "rain"
    FLOOD = "flood"
    POLLUTION = "pollution"
    CURFEW = "curfew"
    EARTHQUAKE = "earthquake"
    STORM = "storm"
    HEATWAVE = "heatwave"
    STRIKE = "strike"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


# ─── Request ──────────────────────────────────────────────────────────────────

class GPSLocation(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class ClaimRequest(BaseModel):
    user_id: str = Field(..., description="Unique gig worker identifier")
    timestamp: datetime = Field(..., description="When the disruption occurred")
    gps_location: GPSLocation = Field(..., description="Worker's reported GPS location")
    disruption_type: DisruptionType = Field(..., description="Type of disruption event")
    claimed_loss_amount: float = Field(..., gt=0, description="Claimed monetary loss (USD)")

    @field_validator("claimed_loss_amount")
    @classmethod
    def validate_loss(cls, v):
        if v > 10_000:
            raise ValueError("Claimed loss exceeds maximum allowed (10,000 USD)")
        return round(v, 2)


# ─── Response ─────────────────────────────────────────────────────────────────

class FraudCheckResponse(BaseModel):
    claim_id: str
    user_id: str
    fraud_score: float = Field(..., ge=0, le=1, description="0 = clean, 1 = highly fraudulent")
    decision: Decision
    reasons: List[str] = Field(default_factory=list)
    rule_flags: List[str] = Field(default_factory=list)
    ml_anomaly_score: Optional[float] = None
    processed_at: datetime


class ClaimHistoryItem(BaseModel):
    claim_id: str
    timestamp: datetime
    disruption_type: str
    claimed_loss_amount: float
    fraud_score: float
    decision: str
    reasons: List[str]
    processed_at: datetime


class FraudHistoryResponse(BaseModel):
    user_id: str
    total_claims: int
    flagged_claims: int
    average_fraud_score: float
    claims: List[ClaimHistoryItem]


class TrainResponse(BaseModel):
    status: str
    samples_used: int
    model_version: str
    metrics: dict
