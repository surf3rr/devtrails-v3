"""
Core configuration — loads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./fraud_engine.db"

    # ML
    MODEL_PATH: str = "models/isolation_forest.pkl"
    ML_CONTAMINATION: float = 0.1       # Expected fraction of anomalies
    ML_N_ESTIMATORS: int = 100

    # Fraud thresholds
    RISK_APPROVE_THRESHOLD: float = 0.35
    RISK_REVIEW_THRESHOLD: float = 0.65  # Above this → REJECT

    # GPS
    MAX_LOCATION_DEVIATION_KM: float = 50.0   # Max km from disruption zone centroid

    # Timing
    MAX_CLAIM_HOURS_AFTER_EVENT: float = 48.0  # Claims filed >48h after event are suspicious
    MIN_CLAIM_HOURS_AFTER_EVENT: float = 0.0   # Claims filed before event are invalid

    # Duplicate window (minutes)
    DUPLICATE_WINDOW_MINUTES: int = 60

    # Activity
    MIN_ACTIVE_DAYS_BEFORE_CLAIM: int = 3     # Worker must have been active ≥3 days

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
