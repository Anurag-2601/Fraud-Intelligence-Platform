"""
customer_generator.py
-----------------------------------------
Generates the Customer Master Dataset
for the Fraud Intelligence Platform.
"""

from pathlib import Path
import random
import logging
from datetime import datetime, timedelta
import json

import numpy as np
import pandas as pd
from faker import Faker

print("=" * 50)
print("Customer Generator Started")
print("=" * 50)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

REFERENCE_DIR = BASE_DIR / "data" / "reference"
MASTER_DIR = BASE_DIR / "data" / "master"
PROFILE_DIR = BASE_DIR / "data" / "profiles"

MASTER_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMER_OUTPUT = MASTER_DIR / "customers.csv"
PROFILE_OUTPUT = PROFILE_DIR / "customer_profiles.json"

LOCATIONS_FILE = MASTER_DIR / "locations.csv"
OCCUPATIONS_FILE = REFERENCE_DIR / "occupations.csv"
BANK_BRANCH_FILE = REFERENCE_DIR / "bank_branches.csv"

fake = Faker("en_IN")

random.seed(42)
np.random.seed(42)

# ==========================================================
# Customer Generator
# ==========================================================

class CustomerGenerator:
    """
    Generates realistic synthetic banking customers.
    """

    def __init__(self):

        logger.info("Initializing Customer Generator...")

        self.locations = None
        self.occupations = None
        self.bank_branches = None

        self.customers = []
        self.customer_profiles = []

    # ------------------------------------------------------

    def load_reference_data(self):
        """
        Load all reference datasets.
        """

        logger.info("Loading reference datasets...")

        self.locations = pd.read_csv(LOCATIONS_FILE)

        self.occupations = pd.read_csv(OCCUPATIONS_FILE)

        self.bank_branches = pd.read_csv(BANK_BRANCH_FILE)

        logger.info(
            "Loaded %d locations | %d occupations | %d branches",
            len(self.locations),
            len(self.occupations),
            len(self.bank_branches)
        )

    # ------------------------------------------------------

    @staticmethod
    def generate_customer_id(index: int) -> str:

        return f"CUST{index:06d}"

    # ------------------------------------------------------

    @staticmethod
    def generate_account_number() -> str:

        return "".join(
            random.choices("0123456789", k=12)
        )

    # ------------------------------------------------------

    @staticmethod
    def generate_credit_score() -> int:

        return random.randint(300, 900)

    # ------------------------------------------------------

    @staticmethod
    def generate_age() -> int:

        return random.randint(18, 75)

    # ------------------------------------------------------

    @staticmethod
    def generate_account_open_date():

        start = datetime(2010, 1, 1)

        end = datetime.today()

        delta = (end - start).days

        return (
            start +
            timedelta(days=random.randint(0, delta))
        ).date()

    # ------------------------------------------------------

    @staticmethod
    def generate_customer_segment(income: int):

        if income < 300000:
            return "Student"

        elif income < 1200000:
            return "Salaried"

        elif income < 2500000:
            return "Freelancer"

        else:
            return "Business"

    # ------------------------------------------------------

    @staticmethod
    def generate_monthly_budget(income: int):

        return round(
            (income / 12) * random.uniform(0.30, 0.60),
            2
        )

    # ------------------------------------------------------

    @staticmethod
    def generate_clv(income: int):

        return round(
            income * random.uniform(2.5, 8),
            2
        )
        
        
if __name__ == "__main__":

    generator = CustomerGenerator()

    generator.load_reference_data()

    print(generator.locations.head())

    print(generator.occupations.head())

    print(generator.bank_branches.head())