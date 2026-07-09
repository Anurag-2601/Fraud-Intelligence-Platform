"""
gold_to_postgres_loader.py

Production-grade loader for moving Gold Layer parquet data
into PostgreSQL warehouse tables.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Final
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

LOG_FORMAT: Final = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
)

logger = logging.getLogger("gold_to_postgres_loader")


class GoldToPostgresLoader:
    """Load Gold layer parquet data into PostgreSQL."""

    def __init__(
        self,
        parquet_path: str,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        target_table: str = "warehouse/gold/merchant_risk_metrics",
    ) -> None:
        self.parquet_path = parquet_path
        self.target_table = target_table

        # Encode special characters in password
        encoded_password = quote_plus(db_password)

        connection_string = (
            f"postgresql+psycopg2://{db_user}:{encoded_password}"
            f"@{db_host}:{db_port}/{db_name}"
        )

        self.engine: Engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

    def read_gold_layer(self) -> pd.DataFrame:
        logger.info("Reading Gold parquet: %s", self.parquet_path)

        dataframe = pd.read_parquet(self.parquet_path)

        logger.info("Loaded %s rows", len(dataframe))
        return dataframe

    def remove_duplicates(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        before = len(dataframe)

        dataframe = dataframe.drop_duplicates()

        logger.info(
            "Removed %s duplicate records",
            before - len(dataframe),
        )

        return dataframe

    def insert_dataframe(
        self,
        dataframe: pd.DataFrame,
        chunksize: int = 10000,
    ) -> None:
        logger.info("Loading dataframe into PostgreSQL")

        dataframe.to_sql(
            name="merchant_risk_metrics",
            schema="fraud",
            con=self.engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize,
        )

        logger.info(
            "Inserted %s rows into warehouse",
            len(dataframe),
        )

    def health_check(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("PostgreSQL connection successful")

    def run(self) -> None:
        start_time = time.time()

        self.health_check()

        dataframe = self.read_gold_layer()
        dataframe = self.remove_duplicates(dataframe)

        self.insert_dataframe(dataframe)

        elapsed = round(time.time() - start_time, 2)

        logger.info(
            "Warehouse load completed in %s seconds",
            elapsed,
        )


def main() -> None:
    loader = GoldToPostgresLoader(
        parquet_path=os.getenv(
            "GOLD_PARQUET_PATH",
            "warehouse/gold/merchant_risk_metrics",
        ),
        db_host=os.getenv("POSTGRES_HOST", "localhost"),
        db_port=int(os.getenv("POSTGRES_PORT", "5432")),

        # Your database is postgres unless you created another one
        db_name=os.getenv(
            "POSTGRES_DB",
            "postgres",
        ),

        db_user=os.getenv(
            "POSTGRES_USER",
            "postgres",
        ),

        # Your actual password
        db_password=os.getenv(
            "POSTGRES_PASSWORD",
            "Anurag@2601",
        ),
    )

    loader.run()


if __name__ == "__main__":
    main()