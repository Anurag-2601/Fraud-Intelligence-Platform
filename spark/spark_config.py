from pyspark.sql import SparkSession


def create_spark_session(app_name: str = "FraudStreaming") -> SparkSession:
    """
    Create Spark session configured for Kafka integration.
    """

    spark = (
        SparkSession.builder
        .appName(app_name)
        .config(
            "spark.sql.shuffle.partitions",
            "4"
        )
        .config(
            "spark.streaming.stopGracefullyOnShutdown",
            "true"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark