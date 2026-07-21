"""
Bronze Layer
Reads transactions from Kafka and stores raw data as Parquet.
"""

import os
import time

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
)

# -------------------------------------------------------
# Create folders
# -------------------------------------------------------

os.makedirs("warehouse/bronze", exist_ok=True)
os.makedirs("warehouse/checkpoints", exist_ok=True)

BRONZE_PATH = "warehouse/bronze/transactions"
CHECKPOINT_PATH = "warehouse/checkpoints/bronze"

# -------------------------------------------------------
# Spark Session
# -------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("FraudBronzeLayer")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# -------------------------------------------------------
# Transaction Schema
# -------------------------------------------------------

transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("device_id", StringType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("bank", StringType(), True),
    StructField("status", StringType(), True),
    StructField("is_fraud", IntegerType(), True),
    StructField("fraud_type", StringType(), True),
    StructField("risk_score", IntegerType(), True),
])

# -------------------------------------------------------
# Read Kafka
# -------------------------------------------------------

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "fraud-transactions")
    .option("startingOffsets", "earliest")
    .load()
)

# -------------------------------------------------------
# Parse JSON
# -------------------------------------------------------

parsed_df = (
    kafka_df
    .select(
        from_json(
            col("value").cast("string"),
            transaction_schema,
        ).alias("data")
    )
    .select("data.*")
)

print("\nParsed Schema:\n")
parsed_df.printSchema()

# -------------------------------------------------------
# Write Bronze
# -------------------------------------------------------

query = (
    parsed_df.writeStream
    .format("parquet")
    .outputMode("append")
    .option("path", BRONZE_PATH)
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime="5 seconds")
    .start()
)

print("\nBronze streaming started...\n")
print("Output Path      :", BRONZE_PATH)
print("Checkpoint Path :", CHECKPOINT_PATH)

# -------------------------------------------------------
# Monitor
# -------------------------------------------------------

while query.isActive:

    print("\n" + "=" * 80)

    print("STATUS")
    print(query.status)

    print("\nEXCEPTION")
    print(query.exception())

    print("\nLAST PROGRESS")
    print(query.lastProgress)

    print("=" * 80)

    time.sleep(5)

print("\nStreaming stopped.")