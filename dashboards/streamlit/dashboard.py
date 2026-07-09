import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus

PASSWORD = quote_plus("Anurag@2601")

engine = create_engine(
    f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/postgres"
)

@st.cache_data(ttl=300)
def load_dashboard_metrics():
    return pd.read_sql(
        """
        SELECT *
        FROM fraud.fraud_dashboard_metrics
        """,
        engine
    )

st.set_page_config(
    page_title="Fraud Intelligence Platform",
    layout="wide"
)

st.title("Fraud Intelligence Platform")

df = load_dashboard_metrics()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Transactions",
    int(df["total_transactions"].iloc[0])
)

col2.metric(
    "Fraud Transactions",
    int(df["fraud_transactions"].iloc[0])
)

col3.metric(
    "Average Risk Score",
    round(df["avg_risk_score"].iloc[0], 2)
)