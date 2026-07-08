"""
transaction_engine.py
------------------------------------------------------------
Enterprise Transaction Engine
Version: 1.0
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
from datetime import datetime
import json
import random
import logging
import uuid

import pandas as pd
import numpy as np

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Random Seed
# ------------------------------------------------------------

random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_DIR = BASE_DIR / "data" / "master"
PROFILE_DIR = BASE_DIR / "data" / "profiles"
STREAM_DIR = BASE_DIR / "data" / "stream"

STREAM_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMERS_FILE = MASTER_DIR / "customers.csv"
DEVICES_FILE = MASTER_DIR / "devices.csv"
MERCHANTS_FILE = MASTER_DIR / "merchants.csv"

CUSTOMER_PROFILE_FILE = PROFILE_DIR / "customer_profiles.json"
CUSTOMER_BEHAVIOUR_FILE = PROFILE_DIR / "customer_behaviour.json"

OUTPUT_FILE = STREAM_DIR / "transactions.csv"


class TransactionEngine:

    def __init__(self):

        self.customers = None
        self.devices = None
        self.merchants = None
        self.customer_profiles = None
        self.customer_behaviour = None

    def load_data(self):

        logger.info("Loading datasets...")

        self.customers = pd.read_csv(CUSTOMERS_FILE)
        self.devices = pd.read_csv(DEVICES_FILE)
        self.merchants = pd.read_csv(MERCHANTS_FILE)

        with open(
            CUSTOMER_PROFILE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            self.customer_profiles = json.load(file)

        with open(
            CUSTOMER_BEHAVIOUR_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            self.customer_behaviour = json.load(file)

        logger.info(
            "Loaded %d customers | %d devices | %d merchants",
            len(self.customers),
            len(self.devices),
            len(self.merchants)
        )

    @staticmethod
    def generate_transaction_id():

        return f"TXN{uuid.uuid4().hex[:12].upper()}"

    def generate_transaction(self):

        customer = self.customers.sample(1).iloc[0]

        customer_id = customer["customer_id"]

        behaviour = self.customer_behaviour.get(
            customer_id,
            {}
        )

        customer_devices = self.devices[
            self.devices["customer_id"] == customer_id
        ]

        device = customer_devices.sample(
            1
        ).iloc[0]

        merchant = self.merchants.sample(
            1
        ).iloc[0]

        avg_amount = behaviour.get(
            "avg_transaction_amount",
            1000
        )

        amount = round(
            np.random.normal(
                avg_amount,
                avg_amount * 0.30
            ),
            2
        )

        amount = max(
            amount,
            10
        )

        transaction = {

            "transaction_id":
                self.generate_transaction_id(),

            "timestamp":
                datetime.now().isoformat(),

            "customer_id":
                customer_id,

            "device_id":
                device["device_id"],

            "merchant_id":
                merchant["merchant_id"],

            "merchant_category":
                merchant["merchant_category"],

            "transaction_type":
                random.choice(
                    [
                        "UPI",
                        "CARD",
                        "NET_BANKING",
                        "ATM"
                    ]
                ),

            "amount":
                amount,

            "city":
                customer["city"],

            "state":
                customer["state"],

            "bank":
                customer["bank_name"],

            "status":
                random.choices(
                    [
                        "SUCCESS",
                        "FAILED"
                    ],
                    weights=[98, 2]
                )[0]
        }

        return transaction

    def generate_batch(
        self,
        batch_size=1000
    ):

        transactions = []

        for _ in range(batch_size):

            transactions.append(
                self.generate_transaction()
            )

        df = pd.DataFrame(
            transactions
        )

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

        logger.info(
            "Generated %d transactions.",
            batch_size
        )


if __name__ == "__main__":

    engine = TransactionEngine()

    engine.load_data()

    engine.generate_batch(
        batch_size=10000
    )

    logger.info(
        "Transaction generation completed."
    )
