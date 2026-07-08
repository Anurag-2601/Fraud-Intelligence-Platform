"""
device_generator.py
------------------------------------------------------------
Enterprise Device Generator
Version: 1.0
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
from datetime import datetime, timedelta
import logging
import random

import pandas as pd
import numpy as np

# ---------------- Logging ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------- Paths ---------------- #

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_DIR = BASE_DIR / "data" / "master"
REFERENCE_DIR = BASE_DIR / "data" / "reference"

CUSTOMERS_FILE = MASTER_DIR / "customers.csv"
DEVICE_REFERENCE_FILE = REFERENCE_DIR / "device_types.csv"

OUTPUT_FILE = MASTER_DIR / "devices.csv"

random.seed(42)
np.random.seed(42)


class DeviceGenerator:
    """Generates customer device inventory."""

    def __init__(self):
        self.customers = None
        self.device_reference = None
        self.devices = []

    def load_data(self):
        logger.info("Loading customers and device reference data...")

        self.customers = pd.read_csv(CUSTOMERS_FILE)
        self.device_reference = pd.read_csv(DEVICE_REFERENCE_FILE)

        logger.info(
            "Loaded %d customers and %d device types.",
            len(self.customers),
            len(self.device_reference)
        )

    @staticmethod
    def generate_device_id(index: int) -> str:
        return f"DEV{index:08d}"

    @staticmethod
    def random_date(start_year: int = 2020) -> str:
        start = datetime(start_year, 1, 1)
        end = datetime.today()

        days = (end - start).days
        offset = random.randint(0, days)

        return str((start + timedelta(days=offset)).date())

    def devices_per_customer(self, segment: str) -> int:
        mapping = {
            "Student": random.randint(1, 2),
            "Salaried": random.randint(2, 3),
            "Business": random.randint(3, 5),
            "Senior Citizen": 1
        }

        return mapping.get(segment, random.randint(1, 2))

    def generate(self):
        self.load_data()

        device_counter = 1

        logger.info("Generating customer devices...")

        for _, customer in self.customers.iterrows():

            num_devices = self.devices_per_customer(
                customer.get(
                    "customer_segment",
                    "Salaried"
                )
            )

            for _ in range(num_devices):

                device = (
                    self.device_reference
                    .sample(1)
                    .iloc[0]
                )

                first_seen = self.random_date()

                self.devices.append({
                    "device_id":
                        self.generate_device_id(
                            device_counter
                        ),

                    "customer_id":
                        customer["customer_id"],

                    "device_type":
                        device["device_type"],

                    "os_family":
                        device["os_family"],

                    "manufacturer":
                        device["manufacturer"],

                    "risk_weight":
                        device["risk_weight"],

                    "is_mobile":
                        device["is_mobile"],

                    "is_rooted":
                        random.random() < 0.03,

                    "is_emulator":
                        random.random() < 0.01,

                    "is_trusted":
                        random.random() < 0.94,

                    "first_seen_date":
                        first_seen,

                    "last_seen_date":
                        first_seen
                })

                device_counter += 1

        df = pd.DataFrame(self.devices)

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        logger.info(
            "Generated %d devices.",
            len(df)
        )

        logger.info(
            "Saved device inventory to %s",
            OUTPUT_FILE
        )


if __name__ == "__main__":
    generator = DeviceGenerator()
    generator.generate()

    logger.info(
        "Device generation completed successfully."
    )
