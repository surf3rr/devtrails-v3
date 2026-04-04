"""
ML Engine — Isolation Forest anomaly detection for fraud scoring.

Features used:
  - claim_frequency_30d      : How many claims in last 30 days
  - location_deviation_km    : Distance from disruption centroid
  - hours_after_event        : How soon after event the claim was filed
  - claimed_loss_normalized  : Loss amount normalized 0–1
  - disruption_type_encoded  : One-hot encoded disruption type

The ML score is combined with the rule-based score in a weighted blend.
"""

import json
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "isolation_forest.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
META_PATH = MODEL_DIR / "model_meta.json"

DISRUPTION_TYPES = ["rain", "flood", "pollution", "curfew", "earthquake", "storm", "heatwave", "strike"]


# ─── Feature Engineering ──────────────────────────────────────────────────────

def build_feature_vector(
    claim_frequency_30d: int,
    location_deviation_km: float,
    hours_after_event: float,
    claimed_loss_amount: float,
    disruption_type: str,
) -> np.ndarray:
    """Convert raw inputs into a fixed-length numeric feature vector."""
    # Encode disruption type as one-hot
    disruption_encoded = [1 if disruption_type == t else 0 for t in DISRUPTION_TYPES]

    # Normalize loss to 0–1 range (assume max $10,000)
    loss_normalized = min(claimed_loss_amount / 10_000, 1.0)

    # Normalize hours (assume 72h max window)
    hours_normalized = min(hours_after_event / 72, 1.0)

    features = [
        claim_frequency_30d,
        location_deviation_km,
        hours_normalized,
        loss_normalized,
    ] + disruption_encoded

    return np.array(features, dtype=np.float64)


def generate_synthetic_training_data(n_normal: int = 800, n_anomaly: int = 100) -> np.ndarray:
    """
    Generate synthetic training data for initial model training.
    Normal claims cluster in realistic ranges; anomalies deviate significantly.
    """
    rng = np.random.default_rng(seed=42)

    # ── Normal claims ────────────────────────────────────────────────────────
    normal = []
    for _ in range(n_normal):
        dtype_idx = rng.integers(0, len(DISRUPTION_TYPES))
        dtype_oh = [1 if i == dtype_idx else 0 for i in range(len(DISRUPTION_TYPES))]
        row = [
            rng.integers(0, 3),           # claim_frequency: 0–2 (normal)
            rng.uniform(0, 30),            # location_deviation: 0–30km
            rng.uniform(0, 0.5),           # hours_normalized: 0–36h
            rng.uniform(0.01, 0.3),        # loss_normalized: $100–$3000
        ] + dtype_oh
        normal.append(row)

    # ── Anomalous claims ─────────────────────────────────────────────────────
    anomalies = []
    for _ in range(n_anomaly):
        dtype_idx = rng.integers(0, len(DISRUPTION_TYPES))
        dtype_oh = [1 if i == dtype_idx else 0 for i in range(len(DISRUPTION_TYPES))]
        row = [
            rng.integers(8, 20),           # claim_frequency: way too high
            rng.uniform(80, 200),          # location_deviation: very far from event
            rng.uniform(0.9, 1.0),         # hours_normalized: filed just before deadline
            rng.uniform(0.85, 1.0),        # loss_normalized: unusually high
        ] + dtype_oh
        anomalies.append(row)

    return np.array(normal + anomalies, dtype=np.float64)


# ─── Model Manager ────────────────────────────────────────────────────────────

class ModelManager:
    """
    Manages the lifecycle of the Isolation Forest model:
    loading, training, scoring, and persistence.
    """

    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.version: str = "untrained"
        MODEL_DIR.mkdir(exist_ok=True)

    def load_or_train(self):
        """Load existing model from disk, or train a fresh one."""
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            logger.info("📦 Loading existing ML model from disk...")
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                self.scaler = pickle.load(f)
            if META_PATH.exists():
                meta = json.loads(META_PATH.read_text())
                self.version = meta.get("version", "loaded")
            logger.info(f"✅ Model loaded (version={self.version})")
        else:
            logger.info("🏋️ No saved model found — training on synthetic data...")
            self.train(generate_synthetic_training_data())

    def train(self, X: np.ndarray, contamination: float = 0.1) -> Dict:
        """
        Train (or retrain) the Isolation Forest model.
        Returns training metrics.
        """
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)

        # Score all training samples (for metrics)
        scores = -self.model.score_samples(X_scaled)  # Higher = more anomalous
        predictions = self.model.predict(X_scaled)    # -1 = anomaly, 1 = normal
        n_anomalies = int((predictions == -1).sum())

        self.version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Persist to disk
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(SCALER_PATH, "wb") as f:
            pickle.dump(self.scaler, f)
        META_PATH.write_text(json.dumps({
            "version": self.version,
            "samples": len(X),
            "n_anomalies_detected": n_anomalies,
            "contamination": contamination,
            "trained_at": datetime.utcnow().isoformat(),
        }, indent=2))

        metrics = {
            "samples_trained": len(X),
            "anomalies_detected_in_training": n_anomalies,
            "anomaly_rate": round(n_anomalies / len(X), 3),
            "mean_anomaly_score": float(np.mean(scores)),
        }
        logger.info(f"✅ Model trained: {metrics}")
        return metrics

    def score(
        self,
        claim_frequency_30d: int,
        location_deviation_km: float,
        hours_after_event: float,
        claimed_loss_amount: float,
        disruption_type: str,
    ) -> float:
        """
        Compute anomaly score for a single claim.
        Returns a value in [0, 1] where higher = more anomalous.
        """
        if self.model is None or self.scaler is None:
            logger.warning("ML model not loaded — returning neutral score 0.5")
            return 0.5

        features = build_feature_vector(
            claim_frequency_30d,
            location_deviation_km,
            hours_after_event,
            claimed_loss_amount,
            disruption_type,
        ).reshape(1, -1)

        features_scaled = self.scaler.transform(features)

        # score_samples returns negative values; more negative = more anomalous
        raw_score = float(-self.model.score_samples(features_scaled)[0])

        # Normalize to 0–1 using a calibrated sigmoid
        normalized = _sigmoid_normalize(raw_score)

        logger.debug(f"ML raw_score={raw_score:.4f} → normalized={normalized:.4f}")
        return round(normalized, 4)

    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None


# ─── Sigmoid Normalization ────────────────────────────────────────────────────

def _sigmoid_normalize(raw: float, center: float = 0.5, steepness: float = 6.0) -> float:
    """
    Map raw Isolation Forest score (roughly 0.3–0.8) to [0, 1].
    Scores above center are increasingly anomalous.
    """
    import math
    return 1 / (1 + math.exp(-steepness * (raw - center)))
