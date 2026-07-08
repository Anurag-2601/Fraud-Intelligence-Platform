"""
producer.py
------------------------------------------------------------
Enterprise Fraud Transaction Kafka Producer
------------------------------------------------------------
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import logging
import time
from pathlib import Path

from kafka import KafkaProducer

# Import your existing engine
from simulator.engine.transaction_engine import TransactionEngine
from simulator.engine.fraud_scenarios import FraudScenarioEngine

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Kafka Configuration
# ------------------------------------------------------------

BOOTSTRAP_SERVERS = ["localhost:9092"]
TOPIC_NAME = "fraud-transactions"

# ------------------------------------------------------------
# Producer
# ------------------------------------------------------------


class FraudTransactionProducer:

    def __init__(self):

        logger.info("Initializing Kafka producer...")

        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5
        )

        self.transaction_engine = TransactionEngine()
        self.transaction_engine.load_data()

        logger.info("Kafka producer initialized.")

    def generate_enriched_transaction(self):

        transaction = (
            self.transaction_engine
            .generate_transaction()
        )

        is_fraud, fraud_type, risk_score = (
            FraudScenarioEngine.assign_fraud(
                transaction
            )
        )

        transaction["is_fraud"] = is_fraud
        transaction["fraud_type"] = fraud_type
        transaction["risk_score"] = risk_score

        return transaction

    def publish_transaction(self, transaction):

        future = self.producer.send(
            TOPIC_NAME,
            value=transaction
        )

        metadata = future.get(timeout=10)

        logger.info(
            "Published %s -> partition=%s offset=%s fraud=%s score=%s",
            transaction["transaction_id"],
            metadata.partition,
            metadata.offset,
            transaction["fraud_type"],
            transaction["risk_score"]
        )

    def run(self, interval_seconds=1):

        logger.info(
            "Starting transaction stream to Kafka topic '%s'",
            TOPIC_NAME
        )

        try:
            while True:

                transaction = (
                    self.generate_enriched_transaction()
                )

                self.publish_transaction(
                    transaction
                )

                time.sleep(
                    interval_seconds
                )

        except KeyboardInterrupt:

            logger.info(
                "Stopping Kafka producer..."
            )

        finally:

            self.producer.flush()
            self.producer.close()

            logger.info(
                "Kafka producer closed successfully."
            )


if __name__ == "__main__":

    producer = FraudTransactionProducer()

    producer.run(
        interval_seconds=1
    )