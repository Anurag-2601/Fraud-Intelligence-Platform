import pandas as pd


# Bronze Layer
bronze_df = pd.read_parquet(
    "warehouse/bronze/transactions"
)

bronze_df.to_csv(
    "warehouse/bronze/transactions_bronze.csv",
    index=False
)


# Silver Layer
silver_df = pd.read_parquet(
    "warehouse/silver/transactions_silver"
)

silver_df.to_csv(
    "warehouse/silver/transactions_silver.csv",
    index=False
)


# Gold Layer - Customer Metrics
customer_gold_df = pd.read_parquet(
    "warehouse/gold/customer_risk_metrics"
)

customer_gold_df.to_csv(
    "warehouse/gold/customer_risk_metrics.csv",
    index=False
)


# Gold Layer - Merchant Metrics
merchant_gold_df = pd.read_parquet(
    "warehouse/gold/merchant_risk_metrics"
)

merchant_gold_df.to_csv(
    "warehouse/gold/merchant_risk_metrics.csv",
    index=False
)


# Gold Layer - Fraud Metrics
fraud_metrics_df = pd.read_parquet(
    "warehouse/gold/fraud_metrics"
)

fraud_metrics_df.to_csv(
    "warehouse/gold/fraud_metrics.csv",
    index=False
)


# Gold Layer - Dashboard Metrics
dashboard_df = pd.read_parquet(
    "warehouse/gold/fraud_dashboard_metrics"
)

dashboard_df.to_csv(
    "warehouse/gold/fraud_dashboard_metrics.csv",
    index=False
)


print("Bronze, Silver and Gold layers exported successfully.")