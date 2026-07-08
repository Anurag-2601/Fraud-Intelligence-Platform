from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    hour,
    to_timestamp,
    to_date
)
from pathlib import Path

spark = (
    SparkSession.builder
    .appName("FraudSilverLayer")
    .getOrCreate()
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BRONZE_PATH = str(
    PROJECT_ROOT /
    "warehouse" /
    "bronze" /
    "transactions"
)

SILVER_PATH = str(
    PROJECT_ROOT /
    "warehouse" /
    "silver" /
    "transactions_silver"
)

BRONZE_PATH = "warehouse/bronze/transactions_bronze.csv"

df = spark.read.csv(
    BRONZE_PATH,
    header=True,
    inferSchema=True
)

silver_df = (
    df
    .withColumn(
        "event_timestamp",
        to_timestamp(
            col("timestamp")
        )
    )
    .withColumn(
        "transaction_date",
        to_date(
            col("event_timestamp")
        )
    )
    .withColumn(
        "transaction_hour",
        hour(
            col("event_timestamp")
        )
    )
    .withColumn(
        "amount_bucket",
        when(
            col("amount") < 1000,
            "SMALL"
        )
        .when(
            col("amount") < 10000,
            "MEDIUM"
        )
        .otherwise(
            "LARGE"
        )
    )
    .withColumn(
        "is_high_risk",
        when(
            col("risk_score") >= 80,
            1
        ).otherwise(
            0
        )
    )
)

(
    silver_df.write
    .mode("overwrite")
    .parquet(SILVER_PATH)
)

print(
    f"Silver layer written to {SILVER_PATH}"
)

spark.stop()