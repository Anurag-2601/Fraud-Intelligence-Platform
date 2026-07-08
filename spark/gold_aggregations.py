from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    count,
    sum,
    col,
    round as spark_round
)

spark = (
    SparkSession.builder
    .appName("FraudGoldLayer")
    .getOrCreate()
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SILVER_PATH = str(
    PROJECT_ROOT /
    "warehouse" /
    "silver" /
    "transactions_silver"
)

GOLD_PATH = (
    PROJECT_ROOT /
    "warehouse" /
    "gold"
)

silver_df = spark.read.parquet(
    SILVER_PATH
)

# ---------------------------
# Customer Metrics
# ---------------------------

customer_metrics = (
    silver_df
    .groupBy("customer_id")
    .agg(
        count("*").alias(
            "total_transactions"
        ),

        sum("is_fraud").alias(
            "fraud_transactions"
        ),

        spark_round(
            avg("risk_score"),
            2
        ).alias(
            "avg_risk_score"
        )
    )
    .withColumn(
        "fraud_rate",
        spark_round(
            (
                col("fraud_transactions")
                /
                col("total_transactions")
            ) * 100,
            2
        )
    )
)

customer_metrics.write.mode(
    "overwrite"
).parquet(
    str(
        GOLD_PATH /
        "customer_risk_metrics"
    )
)

# ---------------------------
# Merchant Metrics
# ---------------------------

merchant_metrics = (
    silver_df
    .groupBy(
        "merchant_id"
    )
    .agg(
        count("*").alias(
            "total_transactions"
        ),

        sum("is_fraud").alias(
            "fraud_transactions"
        ),

        spark_round(
            avg("risk_score"),
            2
        ).alias(
            "avg_risk_score"
        )
    )
)

merchant_metrics.write.mode(
    "overwrite"
).parquet(
    str(
        GOLD_PATH /
        "merchant_risk_metrics"
    )
)

# ---------------------------
# Dashboard Metrics
# ---------------------------

dashboard_metrics = (
    silver_df
    .agg(
        count("*").alias(
            "total_transactions"
        ),

        sum("is_fraud").alias(
            "fraud_transactions"
        ),

        spark_round(
            avg("risk_score"),
            2
        ).alias(
            "avg_risk_score"
        )
    )
)

dashboard_metrics.write.mode(
    "overwrite"
).parquet(
    str(
        GOLD_PATH /
        "fraud_dashboard_metrics"
    )
)

print("\nGold layer generated successfully.\n")

spark.stop()