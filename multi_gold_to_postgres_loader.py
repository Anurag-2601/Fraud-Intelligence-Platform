import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine , text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

DATABASE_URL = (
    "postgresql+psycopg2://postgres:"
    "Anurag%402601@localhost:5432/fraud_intelligence"
)

engine = create_engine(DATABASE_URL)

GOLD_TABLE_MAPPING = {
    "customer_risk_metrics": "customer_risk_metrics",
    "merchant_risk_metrics": "merchant_risk_metrics",
    "fraud_metrics": "fraud_metrics",
    "fraud_dashboard_metrics": "fraud_dashboard_metrics"
}


def load_gold_table(folder_name: str, table_name: str) -> None:
    path = Path("warehouse/gold") / folder_name

    logger.info("Reading %s", path)

    df = pd.read_parquet(path)

    logger.info(
        "Loaded %s rows from %s",
        len(df),
        folder_name
    )

    df.to_sql(
        name=table_name,
        schema="fraud",
        con=engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    logger.info(
        "Inserted %s rows into fraud.%s",
        len(df),
        table_name
    )


def main() -> None:
    for folder, table in GOLD_TABLE_MAPPING.items():
        try:
            load_gold_table(folder, table)
        except Exception as exc:
            logger.exception(
                "Failed loading %s: %s",
                folder,
                exc
            )


if __name__ == "__main__":
    main()