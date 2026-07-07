"""
Location Generator
Reads city reference data and creates the Location Master table.
"""

from pathlib import Path
import logging
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

INPUT_FILE = REFERENCE_DIR / "indian_cities.csv"
OUTPUT_FILE = MASTER_DIR / "locations.csv"


class LocationGenerator:

    def __init__(self):
        self.df = None

    def load_reference_data(self):
        logger.info("Loading reference city dataset...")

        self.df = pd.read_csv(INPUT_FILE)

        logger.info(f"Loaded {len(self.df)} cities.")

    def validate(self):

        required_columns = [
            "city",
            "state",
            "region",
            "tier",
            "latitude",
            "longitude"
        ]

        missing = [
            col for col in required_columns
            if col not in self.df.columns
        ]

        if missing:
            raise ValueError(f"Missing columns: {missing}")

        logger.info("Validation successful.")

    def generate_location_ids(self):

        self.df.insert(
            0,
            "location_id",
            [f"LOC{i:06d}" for i in range(1, len(self.df)+1)]
        )

    def add_metadata(self):

        self.df["country"] = "India"
        self.df["timezone"] = "Asia/Kolkata"

    def save(self):

        self.df.to_csv(OUTPUT_FILE, index=False)

        logger.info(f"Saved to {OUTPUT_FILE}")

    def generate(self):

        self.load_reference_data()
        self.validate()
        self.generate_location_ids()
        self.add_metadata()
        self.save()

        logger.info("Location Master Generated Successfully.")

        return self.df


if __name__ == "__main__":

    generator = LocationGenerator()

    df = generator.generate()

    print(df.head())