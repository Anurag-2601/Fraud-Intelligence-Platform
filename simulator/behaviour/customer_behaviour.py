"""
customer_behaviour.py
------------------------------------------------------------
Enterprise Customer Behaviour Generator
Version: 1.1
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
import json
import random
import logging

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_DIR = BASE_DIR / "data" / "master"
PROFILE_DIR = BASE_DIR / "data" / "profiles"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMERS_FILE = MASTER_DIR / "customers.csv"
DEVICES_FILE = MASTER_DIR / "devices.csv"
MERCHANTS_FILE = MASTER_DIR / "merchants.csv"

CUSTOMER_PROFILE_FILE = PROFILE_DIR / "customer_profiles.json"
OUTPUT_FILE = PROFILE_DIR / "customer_behaviour.json"


class CustomerBehaviourGenerator:

    def __init__(self):
        self.customers = None
        self.devices = None
        self.merchants = None
        self.customer_profiles = {}
        self.behaviour_profiles = {}

    def load_data(self):
        logger.info("Loading master datasets...")

        self.customers = pd.read_csv(CUSTOMERS_FILE)
        self.devices = pd.read_csv(DEVICES_FILE)
        self.merchants = pd.read_csv(MERCHANTS_FILE)

        with open(
            CUSTOMER_PROFILE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            raw_profiles = json.load(file)

        # Handle both dictionary and list formats
        if isinstance(raw_profiles, dict):
            self.customer_profiles = raw_profiles

        elif isinstance(raw_profiles, list):
            logger.warning(
                "Detected legacy customer_profiles.json format."
            )

            for profile in raw_profiles:
                customer_id = profile.get("customer_id")

                if customer_id:
                    self.customer_profiles[customer_id] = profile

        logger.info(
            "Loaded %d customers | %d devices | %d merchants | %d profiles",
            len(self.customers),
            len(self.devices),
            len(self.merchants),
            len(self.customer_profiles)
        )

    @staticmethod
    def transaction_volume(segment):
        mapping = {
            "Student": random.randint(2, 6),
            "Salaried": random.randint(4, 10),
            "Business": random.randint(10, 25),
            "Senior Citizen": random.randint(1, 4)
        }

        return mapping.get(segment, random.randint(3, 8))

    @staticmethod
    def amount_profile(income):
        monthly_income = income / 12

        return round(
            monthly_income * random.uniform(0.02, 0.08),
            2
        )

    def build_profile(self, customer):
        customer_id = customer["customer_id"]

        profile = self.customer_profiles.get(customer_id)

        if profile is None:
            logger.warning(
                "Skipping missing customer profile: %s",
                customer_id
            )
            return

        preferred_hours = profile.get(
            "preferred_transaction_hours",
            sorted(random.sample(range(6, 23), 3))
        )

        risk_profile = profile.get(
            "risk_profile",
            "Medium"
        )

        self.behaviour_profiles[customer_id] = {

            "avg_daily_transactions":
                self.transaction_volume(
                    customer.get(
                        "customer_segment",
                        "Salaried"
                    )
                ),

            "avg_transaction_amount":
                self.amount_profile(
                    customer.get(
                        "annual_income",
                        500000
                    )
                ),

            "preferred_channels":
                [
                    profile.get(
                        "preferred_payment",
                        "UPI"
                    )
                ],

            "preferred_transaction_hours":
                preferred_hours,

            "weekend_activity_multiplier":
                round(random.uniform(1.1, 1.8), 2),

            "salary_spike_multiplier":
                round(random.uniform(1.5, 3.5), 2),

            "cash_usage_ratio":
                round(random.uniform(0.05, 0.60), 2),

            "online_ratio":
                round(random.uniform(0.20, 0.90), 2),

            "travel_probability":
                round(random.uniform(0.01, 0.10), 3),

            "night_transaction_probability":
                round(
                    random.uniform(
                        0.05,
                        0.20
                    ) if str(risk_profile).lower() == "high"
                    else random.uniform(
                        0.01,
                        0.05
                    ),
                    3
                ),

            "device_count":
                profile.get(
                    "device_count",
                    1
                ),

            "home_city":
                profile.get(
                    "home_city",
                    customer.get("city")
                ),

            "risk_profile":
                risk_profile
        }

    def generate(self):
        self.load_data()

        logger.info(
            "Generating customer behaviour profiles..."
        )

        for _, customer in self.customers.iterrows():
            self.build_profile(customer)

        logger.info(
            "Generated %d behaviour profiles.",
            len(self.behaviour_profiles)
        )

        logger.info(
            "Writing file to %s",
            OUTPUT_FILE
        )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.behaviour_profiles,
                file,
                indent=4
            )

        logger.info(
            "customer_behaviour.json created successfully."
        )


if __name__ == "__main__":
    generator = CustomerBehaviourGenerator()
    generator.generate()

    logger.info(
        "Customer behaviour generation completed."
    )