"""
Database layer — async SQLAlchemy with SQLite (swap DATABASE_URL for PostgreSQL).
"""

import json
import logging
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, Boolean,
    select, func
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Engine & Session ─────────────────────────────────────────────────────────

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # SQLite only
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── ORM Base ─────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ─── Models ───────────────────────────────────────────────────────────────────

class ClaimRecord(Base):
    """Persisted fraud check result for every claim submitted."""
    __tablename__ = "claim_records"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True, nullable=False)

    # Input fields
    timestamp = Column(DateTime, nullable=False)
    gps_lat = Column(Float, nullable=False)
    gps_lon = Column(Float, nullable=False)
    disruption_type = Column(String(50), nullable=False)
    claimed_loss_amount = Column(Float, nullable=False)

    # Output fields
    fraud_score = Column(Float, nullable=False)
    decision = Column(String(20), nullable=False)
    reasons_json = Column(Text, default="[]")
    rule_flags_json = Column(Text, default="[]")
    ml_anomaly_score = Column(Float, nullable=True)

    # Metadata
    processed_at = Column(DateTime, default=datetime.utcnow)
    is_flagged = Column(Boolean, default=False)

    @property
    def reasons(self):
        return json.loads(self.reasons_json or "[]")

    @property
    def rule_flags(self):
        return json.loads(self.rule_flags_json or "[]")


class WorkerActivity(Base):
    """Tracks worker activity to validate pre-disruption activity."""
    __tablename__ = "worker_activity"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True, nullable=False)
    activity_date = Column(DateTime, nullable=False)
    gps_lat = Column(Float)
    gps_lon = Column(Float)
    activity_type = Column(String(50), default="delivery")


# ─── Init ─────────────────────────────────────────────────────────────────────

async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables initialized.")


# ─── Session Dependency ───────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ─── Repository Helpers ───────────────────────────────────────────────────────

async def save_claim(session: AsyncSession, record: ClaimRecord):
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_claims_by_user(session: AsyncSession, user_id: str):
    result = await session.execute(
        select(ClaimRecord)
        .where(ClaimRecord.user_id == user_id)
        .order_by(ClaimRecord.processed_at.desc())
    )
    return result.scalars().all()


async def get_recent_claims(
    session: AsyncSession,
    user_id: str,
    disruption_type: str,
    since_timestamp,
):
    """Fetch claims by user for same disruption type within time window."""
    result = await session.execute(
        select(ClaimRecord).where(
            ClaimRecord.user_id == user_id,
            ClaimRecord.disruption_type == disruption_type,
            ClaimRecord.timestamp >= since_timestamp,
        )
    )
    return result.scalars().all()


async def get_worker_activity_days(
    session: AsyncSession,
    user_id: str,
    since_timestamp,
):
    """Count distinct active days for a worker before the disruption."""
    result = await session.execute(
        select(func.count(WorkerActivity.id)).where(
            WorkerActivity.user_id == user_id,
            WorkerActivity.activity_date <= since_timestamp,
        )
    )
    return result.scalar() or 0


async def seed_worker_activity(
    session: AsyncSession,
    user_id: str,
    num_days: int = 10,
):
    """Insert fake historical activity for a worker (for testing)."""
    from datetime import timedelta
    now = datetime.utcnow()
    for i in range(num_days):
        activity = WorkerActivity(
            user_id=user_id,
            activity_date=now - timedelta(days=i + 1),
            gps_lat=28.6139,
            gps_lon=77.2090,
            activity_type="delivery",
        )
        session.add(activity)
    await session.commit()


async def get_area_claim_count(
    session: AsyncSession,
    lat: float,
    lon: float,
    disruption_type: str,
    radius_deg: float = 0.5,
    since_minutes: int = 60,
) -> int:
    """
    Count claims from a geographic area within a recent time window.
    Used for syndicate/burst fraud detection.
    radius_deg=0.5 is roughly 50km grid bucket.
    """
    from datetime import timedelta
    from sqlalchemy import and_

    since = datetime.utcnow() - timedelta(minutes=since_minutes)

    lat_min = round(lat - radius_deg, 2)
    lat_max = round(lat + radius_deg, 2)
    lon_min = round(lon - radius_deg, 2)
    lon_max = round(lon + radius_deg, 2)

    result = await session.execute(
        select(func.count(ClaimRecord.id)).where(
            and_(
                ClaimRecord.disruption_type == disruption_type,
                ClaimRecord.gps_lat >= lat_min,
                ClaimRecord.gps_lat <= lat_max,
                ClaimRecord.gps_lon >= lon_min,
                ClaimRecord.gps_lon <= lon_max,
                ClaimRecord.processed_at >= since,
            )
        )
    )
    return result.scalar() or 0

async def get_claim_by_id(session: AsyncSession, claim_id: str):
    """Fetch a single claim record by claim_id."""
    result = await session.execute(
        select(ClaimRecord).where(ClaimRecord.claim_id == claim_id)
    )
    return result.scalar_one_or_none()