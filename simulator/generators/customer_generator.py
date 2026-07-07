"""
customer_generator.py
------------------------------------------------------------
Enterprise Customer Generator
Version: 1.0 (Frozen)
Author: Pallela Anurag
------------------------------------------------------------
"""

from pathlib import Path
from datetime import datetime, timedelta
import logging
import random
import json

import numpy as np
import pandas as pd
from faker import Faker

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
PROFILE_DIR = BASE_DIR / "data" / "profiles"

MASTER_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

LOCATIONS_FILE = REFERENCE_DIR / "indian_cities.csv"
OCCUPATIONS_FILE = REFERENCE_DIR / "occupations.csv"
BANK_BRANCH_FILE = REFERENCE_DIR / "bank_branches.csv"

CUSTOMER_OUTPUT = MASTER_DIR / "customers.csv"
PROFILE_OUTPUT = PROFILE_DIR / "customer_profiles.json"

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)


class CustomerGenerator:

    def __init__(self):
        self.locations = None
        self.occupations = None
        self.bank_branches = None
        self.customers = []

    def load_reference_data(self):
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

    @staticmethod
    def generate_customer_id(index):
        return f"CUST{index:06d}"

    @staticmethod
    def generate_account_number():
        return "".join(random.choices("0123456789", k=12))

    @staticmethod
    def generate_credit_score():
        return random.randint(300, 900)

    @staticmethod
    def generate_age():
        return random.randint(18, 75)

    @staticmethod
    def generate_account_open_date():
        start = datetime(2010, 1, 1)
        end = datetime.today()
        return (start + timedelta(days=random.randint(0, (end - start).days))).date()

    @staticmethod
    def generate_gender():
        return random.choice(["Male", "Female"])

    def generate_name(self, gender):
        return fake.name_male() if gender == "Male" else fake.name_female()

    @staticmethod
    def generate_phone():
        return f"+91{random.randint(6000000000,9999999999)}"

    def generate_email(self, name):
        username = name.lower().replace(" ", ".").replace("'", "")
        return f"{username}@{random.choice(['gmail.com','outlook.com','yahoo.com'])}"

    def generate_location(self):
        row = self.locations.sample(1).iloc[0]
        return row.to_dict()

    def generate_branch(self, city):
        branches = self.bank_branches[self.bank_branches["city"] == city]
        if branches.empty:
            branches = self.bank_branches
        row = branches.sample(1).iloc[0]
        return {
            "bank_name": row["bank_name"],
            "branch_name": row["branch_name"],
            "ifsc_code": f"{row['ifsc_prefix']}0001234"
        }

    def generate_occupation(self):
        row = self.occupations.sample(1).iloc[0]
        return row.to_dict()

    @staticmethod
    def generate_income(segment):
        ranges = {
            "Student": (0, 300000),
            "Salaried": (400000, 1800000),
            "Freelancer": (500000, 2500000),
            "Business": (1200000, 8000000),
            "Senior Citizen": (200000, 900000)
        }
        low, high = ranges.get(segment, (300000, 800000))
        return random.randint(low, high)

    @staticmethod
    def generate_budget(income):
        return round((income / 12) * random.uniform(0.3, 0.6), 2)

    @staticmethod
    def generate_clv(income):
        return round(income * random.uniform(2.5, 8), 2)

    def generate_customer(self, idx):
        gender = self.generate_gender()
        name = self.generate_name(gender)
        location = self.generate_location()
        occupation = self.generate_occupation()

        income = self.generate_income(occupation["segment"])
        branch = self.generate_branch(location["city"])

        return {
            "customer_id": self.generate_customer_id(idx),
            "account_number": self.generate_account_number(),
            "ifsc_code": branch["ifsc_code"],
            "bank_name": branch["bank_name"],
            "branch_name": branch["branch_name"],
            "full_name": name,
            "gender": gender,
            "age": self.generate_age(),
            "phone": self.generate_phone(),
            "email": self.generate_email(name),
            "occupation": occupation["occupation"],
            "customer_segment": occupation["segment"],
            "annual_income": income,
            "monthly_budget": self.generate_budget(income),
            "credit_score": self.generate_credit_score(),
            "customer_lifetime_value": self.generate_clv(income),
            "city": location["city"],
            "state": location["state"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "account_open_date": str(self.generate_account_open_date()),
            "preferred_payment": random.choice(
                ["UPI", "Debit Card", "Credit Card", "Net Banking"]
            ),
            "salary_day": random.choice([1, 5, 10, 25]),
            "risk_profile": random.choice(["Low", "Medium", "High"]),
            "is_active": True
        }

    def generate(self, count=10000):
        self.load_reference_data()

        for i in range(1, count + 1):
            self.customers.append(self.generate_customer(i))

        df = pd.DataFrame(self.customers)
        df.to_csv(CUSTOMER_OUTPUT, index=False)

        profiles = {}

        for customer in self.customers:
            profiles[customer["customer_id"]] = {
                "salary_day": customer["salary_day"],
                "preferred_payment": customer["preferred_payment"],
                "risk_profile": customer["risk_profile"],
                "preferred_transaction_hours": sorted(
                    random.sample(range(6, 23), 3)
                ),
                "shopping_preference": random.choice(
                    ["ONLINE", "OFFLINE", "BOTH"]
                ),
                "travel_frequency": random.choice(
                    ["LOW", "MEDIUM", "HIGH"]
                ),
                "device_count": random.randint(1, 4),
                "home_city": customer["city"],
                "home_state": customer["state"]
            }

        logger.info("Writing customer_profiles.json...")
        print(repr(PROFILE_OUTPUT))
        with open(PROFILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=4)

            
            
        logger.info("Generated %d customers.", len(df))
        logger.info("Saved: %s", CUSTOMER_OUTPUT)
        logger.info("Saved: %s", PROFILE_OUTPUT)


if __name__ == "__main__":
    generator = CustomerGenerator()
    generator.generate()
    logger.info("Customer generation completed successfully.")
