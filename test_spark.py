from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pathlib import Path

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BRONZE_PATH = str(
    PROJECT_ROOT /
    "warehouse" /
    "bronze" /
    "transactions"
)

kafka_df = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "localhost:9092"
    )
    .option(
        "subscribe",
        "fraud-transactions"
    )
    .option(
        "startingOffsets",
        "latest"
    )
    .load()
)

bronze_df = (
    kafka_df
    .selectExpr(
        "CAST(value AS STRING) AS transaction_json",
        "timestamp AS kafka_timestamp",
        "partition",
        "offset"
    )
)

query = (
    bronze_df.writeStream
    .format("parquet")
    .option(
        "path",
        BRONZE_PATH
    )
    .option(
        "checkpointLocation",
        BRONZE_PATH + "_checkpoint"
    )
    .outputMode("append")
    .start()
)

query.awaitTermination()