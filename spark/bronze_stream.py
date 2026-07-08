from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import *

# -----------------------------------------
# Spark Session
# -----------------------------------------

spark = (
    SparkSession.builder
    .appName("FraudBronzeLayer")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# -----------------------------------------
# Transaction Schema
# -----------------------------------------

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
    StructField("risk_score", IntegerType(), True)
])

# -----------------------------------------
# Read Kafka Stream
# -----------------------------------------

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "fraud-transactions")
    .option("startingOffsets", "latest")
    .load()
)

# -----------------------------------------
# Parse JSON Message
# -----------------------------------------

parsed_df = (
    kafka_df
    .select(
        from_json(
            col("value").cast("string"),
            transaction_schema
        ).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    )
    .select(
        "data.*",
        "kafka_timestamp"
    )
)

# -----------------------------------------
# Write Bronze Layer
# -----------------------------------------

query = (
    parsed_df.writeStream
    .format("parquet")
    .outputMode("append")
    .option(
        "path",
        "warehouse/bronze/transactions"
    )
    .option(
        "checkpointLocation",
        "warehouse/checkpoints/bronze"
    )
    .start()
)

print("Bronze streaming started...")

query.awaitTermination()