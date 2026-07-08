"""
fraud_scenarios.py
------------------------------------------------------------
Enterprise Fraud Scenario Engine
Version: 1.0
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
import logging
import random

import numpy as np
import pandas as pd

# ----------------------------------------------------------
# Logging
# ----------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

random.seed(42)
np.random.seed(42)

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

STREAM_DIR = BASE_DIR / "data" / "stream"

TRANSACTION_FILE = STREAM_DIR / "transactions.csv"
OUTPUT_FILE = STREAM_DIR / "transactions_enriched.csv"


class FraudScenarioEngine:

    def __init__(self):
        self.transactions = None

    def load_transactions(self):
        logger.info("Loading transactions...")

        self.transactions = pd.read_csv(
            TRANSACTION_FILE
        )

        logger.info(
            "Loaded %d transactions.",
            len(self.transactions)
        )

    @staticmethod
    def assign_fraud(transaction):

        fraud_probability = random.random()

        if transaction["amount"] > 50000:
            return (
                1,
                "HIGH_VALUE",
                random.randint(85, 98)
            )

        if fraud_probability < 0.01:
            return (
                1,
                "VELOCITY",
                random.randint(88, 99)
            )

        if fraud_probability < 0.02:
            return (
                1,
                "NEW_DEVICE",
                random.randint(80, 94)
            )

        if fraud_probability < 0.03:
            return (
                1,
                "IMPOSSIBLE_TRAVEL",
                random.randint(92, 99)
            )

        if fraud_probability < 0.05:
            return (
                1,
                "HIGH_RISK_MERCHANT",
                random.randint(75, 90)
            )

        return (
            0,
            "NONE",
            random.randint(5, 25)
        )

    @staticmethod
    def alert_priority(score):

        if score >= 95:
            return "CRITICAL"

        if score >= 85:
            return "HIGH"

        if score >= 70:
            return "MEDIUM"

        return "LOW"

    def enrich_transactions(self):

        logger.info(
            "Injecting fraud scenarios..."
        )

        fraud_flags = []
        fraud_types = []
        risk_scores = []
        priorities = []

        for _, txn in self.transactions.iterrows():

            is_fraud, fraud_type, score = (
                self.assign_fraud(txn)
            )

            fraud_flags.append(is_fraud)
            fraud_types.append(fraud_type)
            risk_scores.append(score)
            priorities.append(
                self.alert_priority(score)
            )

        self.transactions["is_fraud"] = fraud_flags
        self.transactions["fraud_type"] = fraud_types
        self.transactions["risk_score"] = risk_scores
        self.transactions["alert_priority"] = priorities

        fraud_rate = (
            self.transactions["is_fraud"]
            .mean()
            * 100
        )

        logger.info(
            "Fraud rate: %.2f%%",
            fraud_rate
        )

    def save(self):

        self.transactions.to_csv(
            OUTPUT_FILE,
            index=False
        )

        logger.info(
            "Saved enriched transactions to %s",
            OUTPUT_FILE
        )

    def run(self):

        self.load_transactions()
        self.enrich_transactions()
        self.save()


if __name__ == "__main__":

    engine = FraudScenarioEngine()

    engine.run()

    logger.info(
        "Fraud scenario generation completed."
    )