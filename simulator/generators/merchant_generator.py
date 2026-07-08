"""
merchant_generator.py
------------------------------------------------------------
Enterprise Merchant Generator
Version: 1.0 (Frozen)
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
from datetime import datetime, timedelta
import logging
import random

import numpy as np
import pandas as pd

# ---------------- Logging ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------- Paths ---------------- #

BASE_DIR = Path(__file__).resolve().parent.parent

REFERENCE_DIR = BASE_DIR / "data" / "reference"
MASTER_DIR = BASE_DIR / "data" / "master"

MASTER_DIR.mkdir(parents=True, exist_ok=True)

CITY_FILE = REFERENCE_DIR / "indian_cities.csv"
MERCHANT_CATEGORY_FILE = REFERENCE_DIR / "merchant_categories.csv"

MERCHANT_OUTPUT = MASTER_DIR / "merchants.csv"

random.seed(42)
np.random.seed(42)


class MerchantGenerator:
    """
    Enterprise merchant generator.
    """

    def __init__(self):
        self.cities = None
        self.categories = None
        self.merchants = []

    def load_reference_data(self):
        """Load reference datasets."""

        logger.info("Loading reference datasets...")

        self.cities = pd.read_csv(CITY_FILE)
        self.categories = pd.read_csv(MERCHANT_CATEGORY_FILE)

        logger.info(
            "Loaded %d cities and %d merchant categories.",
            len(self.cities),
            len(self.categories)
        )

    @staticmethod
    def generate_merchant_id(index: int) -> str:
        return f"MER{index:06d}"

    @staticmethod
    def generate_acceptance_flag(probability: float = 0.95) -> bool:
        return random.random() < probability

    @staticmethod
    def generate_onboarding_date() -> str:
        start = datetime(2015, 1, 1)
        end = datetime.today()

        delta_days = (end - start).days
        days_offset = random.randint(0, delta_days)

        return str((start + timedelta(days=days_offset)).date())

    def generate_city(self) -> dict:
        row = self.cities.sample(1).iloc[0]
        return row.to_dict()

    def generate_category(self) -> dict:
        row = self.categories.sample(1).iloc[0]
        return row.to_dict()

    def generate_merchant_name(
        self,
        base_name: str,
        city: str
    ) -> str:
        suffix = random.choice(
            [
                "Store",
                "Retail",
                "Mart",
                "Center",
                "Outlet",
                "Services",
                "Hub",
                "Point"
            ]
        )

        return f"{base_name} {city} {suffix}"

    def generate_merchant(self, index: int) -> dict:
        city_data = self.generate_city()
        category_data = self.generate_category()

        return {
            "merchant_id":
                self.generate_merchant_id(index),

            "merchant_name":
                self.generate_merchant_name(
                    category_data["merchant_name"],
                    city_data["city"]
                ),

            "merchant_category":
                category_data["merchant_category"],

            "mcc_code":
                category_data["mcc_code"],

            "channel":
                category_data["channel"],

            "avg_transaction":
                category_data["avg_transaction"],

            "risk_level":
                category_data["risk_level"],

            "fraud_weight":
                category_data["fraud_weight"],

            "settlement_type":
                category_data["settlement_type"],

            "city":
                city_data["city"],

            "state":
                city_data["state"],

            "latitude":
                city_data["latitude"],

            "longitude":
                city_data["longitude"],

            "accepts_upi":
                self.generate_acceptance_flag(0.98),

            "accepts_card":
                self.generate_acceptance_flag(0.92),

            "accepts_net_banking":
                self.generate_acceptance_flag(0.85),

            "merchant_since":
                self.generate_onboarding_date(),

            "is_active":
                random.random() < 0.98
        }

    def generate(
        self,
        count: int = 5000
    ):
        """
        Generate merchants.
        """

        self.load_reference_data()

        logger.info(
            "Generating %d merchants...",
            count
        )

        for i in range(1, count + 1):
            self.merchants.append(
                self.generate_merchant(i)
            )

        df = pd.DataFrame(self.merchants)

        df.to_csv(
            MERCHANT_OUTPUT,
            index=False
        )

        logger.info(
            "Generated %d merchants.",
            len(df)
        )

        logger.info(
            "Saved merchant dataset to %s",
            MERCHANT_OUTPUT
        )


if __name__ == "__main__":
    generator = MerchantGenerator()
    generator.generate()

    logger.info(
        "Merchant generation completed successfully."
    )
