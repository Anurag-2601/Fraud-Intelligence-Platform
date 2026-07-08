"""
stream_generator.py
------------------------------------------------------------
Enterprise Live Transaction Stream Generator
------------------------------------------------------------
"""

import time
import logging
from pathlib import Path

import pandas as pd

from transaction_engine import TransactionEngine
from fraud_scenarios import FraudScenarioEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

STREAM_DIR = BASE_DIR / "data" / "stream"
STREAM_DIR.mkdir(parents=True, exist_ok=True)

LIVE_FILE = STREAM_DIR / "live_transactions.csv"


class StreamGenerator:

    def __init__(self):
        self.transaction_engine = TransactionEngine()

        self.transaction_engine.load_data()

    def generate_live_transaction(self):

        transaction = (
            self.transaction_engine
            .generate_transaction()
        )

        fraud_flag, fraud_type, risk_score = (
            FraudScenarioEngine.assign_fraud(
                transaction
            )
        )

        transaction["is_fraud"] = fraud_flag
        transaction["fraud_type"] = fraud_type
        transaction["risk_score"] = risk_score

        return transaction

    def append_transaction(
        self,
        transaction
    ):

        df = pd.DataFrame(
            [transaction]
        )

        if LIVE_FILE.exists():

            df.to_csv(
                LIVE_FILE,
                mode="a",
                header=False,
                index=False
            )

        else:

            df.to_csv(
                LIVE_FILE,
                index=False
            )

    def run(
        self,
        interval_seconds=1
    ):

        logger.info(
            "Starting live transaction stream..."
        )

        while True:

            transaction = (
                self.generate_live_transaction()
            )

            self.append_transaction(
                transaction
            )

            logger.info(
                "Generated transaction %s | Fraud=%s | Score=%s",
                transaction["transaction_id"],
                transaction["is_fraud"],
                transaction["risk_score"]
            )

            time.sleep(
                interval_seconds
            )


if __name__ == "__main__":

    stream = StreamGenerator()

    stream.run(
        interval_seconds=1
    )
