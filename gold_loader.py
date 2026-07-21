import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
    f"?sslmode=require&channel_binding=require"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ============================================================
# Gold Table Mapping
# ============================================================

GOLD_TABLE_MAPPING = {
    "customer_risk_metrics": "customer_risk_metrics",
    "merchant_risk_metrics": "merchant_risk_metrics",
    "fraud_metrics": "fraud_metrics",
    "fraud_dashboard_metrics": "fraud_dashboard_metrics",
}

# ============================================================
# Load One Table
# ============================================================


def load_gold_table(folder_name: str, table_name: str) -> None:
    """Read Parquet and load into PostgreSQL."""

    path = Path("warehouse") / "gold" / folder_name

    logger.info("=" * 70)
    logger.info("Loading table: %s", table_name)
    logger.info("Reading folder: %s", path)

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")

    df = pd.read_parquet(path)

    logger.info("Rows    : %d", len(df))
    logger.info("Columns : %s", list(df.columns))
    logger.info("Dtypes:\n%s", df.dtypes)

    # Append latest Gold rows into the target table.
    with engine.begin() as conn:
        df.to_sql(
            name=table_name,
            schema="fraud",
            con=conn,
            if_exists="append",
            index=False,
        )

    logger.info("Successfully loaded %d rows into fraud.%s", len(df), table_name)


# ============================================================
# Main
# ============================================================


def main() -> None:

    logger.info("=" * 70)
    logger.info("Starting Gold Layer Loader")
    logger.info("=" * 70)

    for folder, table in GOLD_TABLE_MAPPING.items():

        try:
            load_gold_table(folder, table)

        except Exception:
            logger.exception("FAILED LOADING %s", table)

    logger.info("=" * 70)
    logger.info("Gold Layer Loading Completed")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()