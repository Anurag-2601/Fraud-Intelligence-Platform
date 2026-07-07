"""
Simulator Configuration
-----------------------
Central configuration for the Fraud Intelligence Platform.
"""

from pathlib import Path

# ==============================================================================
# PROJECT PATHS
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

# ==============================================================================
# RANDOMNESS
# ==============================================================================

RANDOM_SEED = 42

# ==============================================================================
# MASTER DATA COUNTS
# ==============================================================================

CUSTOMER_COUNT = 10_000
MERCHANT_COUNT = 500
CITY_COUNT = 100
ATM_COUNT = 300
BRANCH_COUNT = 150

# ==============================================================================
# OUTPUT FILES
# ==============================================================================

CUSTOMERS_FILE = DATA_DIR / "customers.csv"
CUSTOMER_PROFILE_FILE = DATA_DIR / "customer_profiles.json"

MERCHANT_FILE = DATA_DIR / "merchants.csv"
DEVICE_FILE = DATA_DIR / "devices.csv"
LOCATION_FILE = DATA_DIR / "locations.csv"
ATM_FILE = DATA_DIR / "atms.csv"
BRANCH_FILE = DATA_DIR / "branches.csv"

# ==============================================================================
# CUSTOMER SEGMENTS
# ==============================================================================

CUSTOMER_SEGMENTS = {
    "Salaried": 45,
    "Student": 20,
    "Business": 15,
    "Freelancer": 10,
    "Senior Citizen": 10,
}

# ==============================================================================
# ACCOUNT TYPES
# ==============================================================================

ACCOUNT_TYPES = [
    "Savings",
    "Current",
]

# ==============================================================================
# PAYMENT METHODS
# ==============================================================================

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
]

# ==============================================================================
# RISK PROFILE
# ==============================================================================

RISK_PROFILES = [
    "Low",
    "Medium",
    "High",
]
