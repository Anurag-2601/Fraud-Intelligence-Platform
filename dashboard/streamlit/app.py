import os
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Enterprise Fraud Intelligence Platform",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================
# Reads from Streamlit Cloud's Secrets manager (st.secrets) when
# deployed. Falls back to a local .env file for local development.
#
# Streamlit Cloud setup: App settings -> Secrets -> paste:
#   DB_USER = "neondb_owner"
#   DB_PASSWORD = "..."
#   DB_HOST = "ep-....neon.tech"
#   DB_PORT = "5432"
#   DB_NAME = "neondb"
#
# Local setup: create a .env file with the same keys (no quotes needed).


from dotenv import load_dotenv


def get_db_credential(key: str) -> str:
    # First try Streamlit Secrets (works on Streamlit Cloud)
    try:
        return st.secrets[key]
    except Exception:
        pass

    # Fallback to local .env (works locally)
    load_dotenv()
    return os.getenv(key)


DB_USER = get_db_credential("DB_USER")
DB_PASSWORD = get_db_credential("DB_PASSWORD")
DB_HOST = get_db_credential("DB_HOST")
DB_PORT = get_db_credential("DB_PORT")
DB_NAME = get_db_credential("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?sslmode=require"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=1800)

# ==========================================================
# RISK BUCKET DEFINITION (shared by KPI + chart so they always agree)
# 0-30   Low Risk
# 30-60  Medium Risk
# 60-80  High Risk
# 80-100 Critical Risk
# "High Risk Transactions" KPI = High + Critical combined (risk_score >= 60)
# ==========================================================

HIGH_RISK_THRESHOLD = 60

# ==========================================================
# SESSION STATE
# ==========================================================

if "live_mode" not in st.session_state:
    st.session_state.live_mode = True

if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 30000  # ms

# ==========================================================
# AUTO REFRESH
# ==========================================================

if st.session_state.live_mode:
    st_autorefresh(
        interval=st.session_state.refresh_interval,
        key="fraud_refresh"
    )

# ==========================================================
# DIMENSION VALUES FOR FILTER DROPDOWNS
# Cached longer (5 min) since these barely change day to day.
# Pulled from fact_transactions directly since bank/state/merchant
# category/transaction_type live there; small DISTINCT queries are
# cheap even on a large fact table.
# ==========================================================

@st.cache_data(ttl=300)
def load_filter_options():
    banks = pd.read_sql(
        "SELECT DISTINCT bank FROM fraud.fact_transactions "
        "WHERE bank IS NOT NULL ORDER BY bank", engine
    )["bank"].tolist()

    states = pd.read_sql(
        "SELECT DISTINCT state FROM fraud.fact_transactions "
        "WHERE state IS NOT NULL ORDER BY state", engine
    )["state"].tolist()

    categories = pd.read_sql(
        "SELECT DISTINCT merchant_category FROM fraud.fact_transactions "
        "WHERE merchant_category IS NOT NULL ORDER BY merchant_category", engine
    )["merchant_category"].tolist()

    txn_types = pd.read_sql(
        "SELECT DISTINCT transaction_type FROM fraud.fact_transactions "
        "WHERE transaction_type IS NOT NULL ORDER BY transaction_type", engine
    )["transaction_type"].tolist()

    bounds = pd.read_sql(
        "SELECT MIN(risk_score) AS min_risk, MAX(risk_score) AS max_risk, "
        "MIN(amount) AS min_amt, MAX(amount) AS max_amt "
        "FROM fraud.fact_transactions", engine
    ).iloc[0]

    return banks, states, categories, txn_types, bounds


banks_opts, states_opts, category_opts, txn_type_opts, bounds = load_filter_options()

# ==========================================================
# HEADER
# ==========================================================

st.title("🛡️ Enterprise Fraud Intelligence Platform")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.live_mode:
        st.success("🟢 LIVE FEED RUNNING")
    else:
        st.error("🔴 LIVE FEED PAUSED")

with status_col2:
    st.info(
        f"Last Updated\n"
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

with status_col3:
    interval = st.selectbox(
        "Refresh Interval",
        [10000, 30000, 60000, 120000],
        index=1,
        format_func=lambda x: f"{x // 1000} sec"
    )
    st.session_state.refresh_interval = interval

button1, button2, button3 = st.columns(3)

with button1:
    if st.button("⏸ Pause Live Feed"):
        st.session_state.live_mode = False
        st.rerun()

with button2:
    if st.button("▶ Resume Live Feed"):
        st.session_state.live_mode = True
        st.rerun()

with button3:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.title("Dashboard Filters")

if st.sidebar.button("🧹 Clear Filters"):
    for k in [
        "filter_txn_types", "filter_banks", "filter_states",
        "filter_categories", "filter_risk_range", "filter_amount_range",
        "filter_customer_search", "filter_merchant_search",
    ]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

txn_types = st.sidebar.multiselect("Transaction Type", txn_type_opts, key="filter_txn_types")
banks = st.sidebar.multiselect("Bank", banks_opts, key="filter_banks")
states = st.sidebar.multiselect("State", states_opts, key="filter_states")
categories = st.sidebar.multiselect("Merchant Category", category_opts, key="filter_categories")

risk_min = int(bounds["min_risk"]) if bounds["min_risk"] is not None else 0
risk_max = int(bounds["max_risk"]) if bounds["max_risk"] is not None else 100
risk_range = st.sidebar.slider(
    "Risk Score", risk_min, risk_max, (risk_min, risk_max), key="filter_risk_range"
)

amt_min = float(bounds["min_amt"]) if bounds["min_amt"] is not None else 0.0
amt_max = float(bounds["max_amt"]) if bounds["max_amt"] is not None else 100000.0
amount_range = st.sidebar.slider(
    "Transaction Amount", amt_min, amt_max, (amt_min, amt_max), key="filter_amount_range"
)

customer_search = st.sidebar.text_input("Customer ID contains", key="filter_customer_search")
merchant_search = st.sidebar.text_input("Merchant ID contains", key="filter_merchant_search")

# ==========================================================
# BUILD A SHARED SQL WHERE CLAUSE FROM THE FILTERS ABOVE
# Every chart/KPI below re-uses this so they can never disagree
# with each other. Parameterized to avoid SQL injection.
# ==========================================================

where_clauses = ["risk_score BETWEEN :risk_lo AND :risk_hi",
                  "amount BETWEEN :amt_lo AND :amt_hi"]
params = {
    "risk_lo": risk_range[0], "risk_hi": risk_range[1],
    "amt_lo": amount_range[0], "amt_hi": amount_range[1],
}

if txn_types:
    where_clauses.append("transaction_type = ANY(:txn_types)")
    params["txn_types"] = txn_types
if banks:
    where_clauses.append("bank = ANY(:banks)")
    params["banks"] = banks
if states:
    where_clauses.append("state = ANY(:states)")
    params["states"] = states
if categories:
    where_clauses.append("merchant_category = ANY(:categories)")
    params["categories"] = categories
if customer_search:
    where_clauses.append("customer_id::text ILIKE :customer_search")
    params["customer_search"] = f"%{customer_search}%"
if merchant_search:
    where_clauses.append("merchant_id::text ILIKE :merchant_search")
    params["merchant_search"] = f"%{merchant_search}%"

WHERE_SQL = " AND ".join(where_clauses)

# ==========================================================
# KPI QUERY — single aggregate pass over fact_transactions
# ==========================================================

@st.cache_data(ttl=30)
def load_kpis(where_sql: str, params: dict) -> dict:
    query = text(f"""
        SELECT
            COUNT(*) AS total_transactions,
            COALESCE(SUM(is_fraud::int), 0) AS fraud_transactions,
            COALESCE(AVG(risk_score), 0) AS avg_risk_score,
            COUNT(*) FILTER (WHERE risk_score >= {HIGH_RISK_THRESHOLD}) AS high_risk_transactions,
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(DISTINCT merchant_id) AS unique_merchants,
            COUNT(DISTINCT bank) AS banks_tracked,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM fraud.fact_transactions
        WHERE {where_sql}
    """)
    with engine.connect() as conn:
        row = conn.execute(query, params).mappings().first()
    return dict(row)


kpis = load_kpis(WHERE_SQL, params)

total_transactions = int(kpis["total_transactions"])
fraud_transactions = int(kpis["fraud_transactions"])
average_risk = float(kpis["avg_risk_score"])
high_risk_transactions = int(kpis["high_risk_transactions"])
unique_customers = int(kpis["unique_customers"])
unique_merchants = int(kpis["unique_merchants"])
banks_tracked = int(kpis["banks_tracked"])
total_amount = float(kpis["total_amount"])

fraud_rate = (fraud_transactions / total_transactions * 100) if total_transactions else 0

# ==========================================================
# KPI ROW 1
# ==========================================================

k1, k2, k3, k4 = st.columns(4)
k1.metric("Transactions", f"{total_transactions:,}")
k2.metric("Total Amount", f"₹{total_amount:,.2f}")
k3.metric("Average Risk Score", f"{average_risk:.2f}")
k4.metric("High Risk Transactions", f"{high_risk_transactions:,}")

# ==========================================================
# KPI ROW 2
# ==========================================================

k5, k6, k7, k8 = st.columns(4)
k5.metric("Fraud Transactions", f"{fraud_transactions:,}")
k6.metric("Fraud Rate", f"{fraud_rate:.2f}%" if total_transactions else "N/A")
k7.metric("Unique Customers", f"{unique_customers:,}")
k8.metric("Unique Merchants", f"{unique_merchants:,}")

st.markdown("---")

# ==========================================================
# CHART QUERIES — each does its own GROUP BY in Postgres,
# reusing the same WHERE_SQL / params so every chart reflects
# exactly the same filtered slice as the KPIs above.
# ==========================================================

@st.cache_data(ttl=30)
def load_risk_category_dist(where_sql: str, params: dict) -> pd.DataFrame:
    query = text(f"""
        SELECT
            CASE
                WHEN risk_score < 30 THEN 'Low Risk'
                WHEN risk_score < 60 THEN 'Medium Risk'
                WHEN risk_score < 80 THEN 'High Risk'
                ELSE 'Critical Risk'
            END AS risk_category,
            COUNT(*) AS transactions
        FROM fraud.fact_transactions
        WHERE {where_sql}
        GROUP BY 1
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=30)
def load_txn_type_dist(where_sql: str, params: dict) -> pd.DataFrame:
    query = text(f"""
        SELECT transaction_type, COUNT(*) AS transactions
        FROM fraud.fact_transactions
        WHERE {where_sql}
        GROUP BY transaction_type
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=30)
def load_fraud_by_bank(where_sql: str, params: dict) -> pd.DataFrame:
    query = text(f"""
        SELECT bank, COALESCE(SUM(is_fraud::int), 0) AS fraud_transactions
        FROM fraud.fact_transactions
        WHERE {where_sql}
        GROUP BY bank
        ORDER BY fraud_transactions DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=30)
def load_fraud_by_state(where_sql: str, params: dict) -> pd.DataFrame:
    query = text(f"""
        SELECT state, COALESCE(SUM(is_fraud::int), 0) AS fraud_transactions
        FROM fraud.fact_transactions
        WHERE {where_sql}
        GROUP BY state
        ORDER BY fraud_transactions DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


@st.cache_data(ttl=30)
def load_fraud_by_category(where_sql: str, params: dict) -> pd.DataFrame:
    query = text(f"""
        SELECT merchant_category, COALESCE(SUM(is_fraud::int), 0) AS fraud_flag
        FROM fraud.fact_transactions
        WHERE {where_sql}
        GROUP BY merchant_category
        ORDER BY merchant_category
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)


risk_dist_df = load_risk_category_dist(WHERE_SQL, params)
txn_type_df = load_txn_type_dist(WHERE_SQL, params)
bank_agg = load_fraud_by_bank(WHERE_SQL, params)
state_agg = load_fraud_by_state(WHERE_SQL, params)
category_agg = load_fraud_by_category(WHERE_SQL, params)

# ==========================================================
# ROW: Fraud Risk Categories + Transaction Type Distribution
# ==========================================================

chart1, chart2 = st.columns(2)

with chart1:
    fig = px.bar(
        risk_dist_df, x="risk_category", y="transactions",
        text="transactions", title="Fraud Risk Categories",
        category_orders={"risk_category": ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]}
    )
    fig.update_layout(xaxis_title="Risk Category", yaxis_title="Transactions")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    fig = px.pie(
        txn_type_df, names="transaction_type", values="transactions",
        title="Transaction Type Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# ROW: Fraud by Bank + Fraud by State
# ==========================================================

chart3, chart4 = st.columns(2)

with chart3:
    fig = px.bar(
        bank_agg, x="bank", y="fraud_transactions",
        title="Fraud by Bank"
    )
    st.plotly_chart(fig, use_container_width=True)

with chart4:
    fig = px.bar(
        state_agg, x="state", y="fraud_transactions",
        title="Fraud by State"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# ROW: Fraud by Merchant Category (full width, matches screenshot)
# ==========================================================

fig = px.bar(
    category_agg, x="merchant_category", y="fraud_flag",
    title="Fraud by Merchant Category"
)
fig.update_layout(xaxis_title="merchant_category")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# TOP RISKY CUSTOMERS / MERCHANTS
# Sourced from the pre-aggregated Gold tables (small, safe to load
# in full) since they don't carry bank/state/category/type columns
# to filter against fact_transactions-level filters. Only the
# customer/merchant ID search boxes apply here.
# ==========================================================

@st.cache_data(ttl=30)
def load_customer_metrics() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM fraud.customer_risk_metrics", engine)


@st.cache_data(ttl=30)
def load_merchant_metrics() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM fraud.merchant_risk_metrics", engine)


customer_df = load_customer_metrics()
merchant_df = load_merchant_metrics()

filtered_customer_df = customer_df.copy()
if customer_search:
    filtered_customer_df = filtered_customer_df[
        filtered_customer_df["customer_id"].astype(str).str.contains(customer_search, case=False)
    ]

filtered_merchant_df = merchant_df.copy()
if merchant_search:
    filtered_merchant_df = filtered_merchant_df[
        filtered_merchant_df["merchant_id"].astype(str).str.contains(merchant_search, case=False)
    ]

st.subheader("Top Risky Customers")
st.dataframe(
    filtered_customer_df.sort_values("fraud_rate", ascending=False).head(50),
    use_container_width=True,
    height=400
)

st.subheader("Top Risky Merchants")
st.dataframe(
    filtered_merchant_df.sort_values("avg_risk_score", ascending=False).head(50),
    use_container_width=True,
    height=400
)

st.markdown("---")

st.caption(
    "Enterprise Fraud Intelligence Platform | "
    "Kafka | Spark | PostgreSQL | Streamlit"
)