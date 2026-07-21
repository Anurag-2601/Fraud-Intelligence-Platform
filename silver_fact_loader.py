"""
============================================================
Silver -> Neon Fact Transactions Loader
============================================================

Reads:
    warehouse/silver/transactions_silver

Loads into:
    fraud.fact_transactions

Author: Pallela Anurag
============================================================
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ==========================================================
# Environment
# ==========================================================

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

SILVER_PATH = (
    BASE_DIR
    / "warehouse"
    / "silver"
    / "transactions_silver"
)

TABLE_NAME = "fact_transactions"

SCHEMA_NAME = "fraud"

# ==========================================================
# Loader
# ==========================================================


def load_fact_transactions() -> None:
    """
    Loads Silver transactions into Neon.
    """

    if not SILVER_PATH.exists():
        logger.error("Silver folder not found:")
        logger.error(SILVER_PATH)
        return

    logger.info("Reading Silver parquet...")

    df = pd.read_parquet(SILVER_PATH)

    logger.info("Rows read: %d", len(df))

    if df.empty:
        logger.warning("No rows found.")
        return

    logger.info("Replacing fact_transactions table...")

    df.to_sql(
        TABLE_NAME,
        engine,
        schema=SCHEMA_NAME,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=5000,
    )

    with engine.begin() as conn:
        count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM fraud.fact_transactions
                """
            )
        ).scalar()

    logger.info("Loaded %s rows into fraud.fact_transactions", count)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":
    load_fact_transactions()
