from pyspark.sql import SparkSession


def create_spark_session(app_name: str = "FraudStreaming") -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .config("spark.hadoop.io.native.lib.available", "false")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
        # Windows Hadoop compatibility
        .config("spark.hadoop.io.native.lib.available", "false")
        .config("spark.sql.warehouse.dir", "warehouse")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark