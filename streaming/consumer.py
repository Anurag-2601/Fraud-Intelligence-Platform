"""
consumer.py
------------------------------------------------------------
Enterprise Fraud Transaction Consumer
------------------------------------------------------------
"""

import json
import logging
from pathlib import Path

import pandas as pd
from kafka import KafkaConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

BOOTSTRAP_SERVERS = ["localhost:9092"]
TOPIC_NAME = "fraud-transactions"

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = BASE_DIR / "warehouse" / "bronze"
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = BRONZE_DIR / "transactions_bronze.csv"


class FraudConsumer:

    def __init__(self):

        self.consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(
                m.decode("utf-8")
            ),
            consumer_timeout_ms=1000
        )

    def save_transaction(self, transaction):

        df = pd.DataFrame([transaction])

        if OUTPUT_FILE.exists():
            df.to_csv(
                OUTPUT_FILE,
                mode="a",
                index=False,
                header=False
            )
        else:
            df.to_csv(
                OUTPUT_FILE,
                index=False
            )

    def run(self):

        logger.info(
            "Listening to Kafka topic '%s'",
            TOPIC_NAME
        )

        try:
            for message in self.consumer:

                transaction = message.value

                self.save_transaction(
                    transaction
                )

                logger.info(
                    "Consumed %s | Fraud=%s | Score=%s",
                    transaction["transaction_id"],
                    transaction["fraud_type"],
                    transaction["risk_score"]
                )

        except KeyboardInterrupt:
            logger.info(
                "Stopping consumer..."
            )

        finally:
            self.consumer.close()


if __name__ == "__main__":

    consumer = FraudConsumer()
    consumer.run()