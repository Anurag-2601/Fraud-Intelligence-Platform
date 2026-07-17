import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

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

DB_USER = "postgres"
DB_PASSWORD = "Anurag%402601"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "fraud_intelligence"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "live_mode" not in st.session_state:
    st.session_state.live_mode = True

if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 5000

# ==========================================================
# AUTO REFRESH
# ==========================================================

if st.session_state.live_mode:
    st_autorefresh(
        interval=st.session_state.refresh_interval,
        key="fraud_refresh"
    )

# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data(ttl=5)
def load_data():
    query = """
        SELECT *
        FROM fraud.fact_transactions
        ORDER BY transaction_time DESC
    """
    return pd.read_sql(query, engine)

df = load_data()

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
        [5000, 10000, 30000, 60000],
        format_func=lambda x: f"{x//1000} sec"
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

transaction_types = st.sidebar.multiselect(
    "Transaction Type",
    sorted(df["transaction_type"].dropna().unique())
)

banks = st.sidebar.multiselect(
    "Bank",
    sorted(df["bank"].dropna().unique())
)

states = st.sidebar.multiselect(
    "State",
    sorted(df["state"].dropna().unique())
)

merchant_categories = st.sidebar.multiselect(
    "Merchant Category",
    sorted(df["merchant_category"].dropna().unique())
)

risk_range = st.sidebar.slider(
    "Risk Score",
    int(df["risk_score"].min()),
    int(df["risk_score"].max()),
    (
        int(df["risk_score"].min()),
        int(df["risk_score"].max())
    )
)

amount_range = st.sidebar.slider(
    "Transaction Amount",
    int(df["transaction_amount"].min()),
    int(df["transaction_amount"].max()),
    (
        int(df["transaction_amount"].min()),
        int(df["transaction_amount"].max())
    )
)

customer_search = st.sidebar.text_input(
    "Customer ID"
)

merchant_search = st.sidebar.text_input(
    "Merchant ID"
)

show_only_fraud = st.sidebar.checkbox(
    "Show Fraud Transactions Only"
)

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if transaction_types:
    filtered_df = filtered_df[
        filtered_df["transaction_type"].isin(transaction_types)
    ]

if banks:
    filtered_df = filtered_df[
        filtered_df["bank"].isin(banks)
    ]

if states:
    filtered_df = filtered_df[
        filtered_df["state"].isin(states)
    ]

if merchant_categories:
    filtered_df = filtered_df[
        filtered_df["merchant_category"].isin(
            merchant_categories
        )
    ]

filtered_df = filtered_df[
    (filtered_df["risk_score"] >= risk_range[0]) &
    (filtered_df["risk_score"] <= risk_range[1])
]

filtered_df = filtered_df[
    (filtered_df["transaction_amount"] >= amount_range[0]) &
    (filtered_df["transaction_amount"] <= amount_range[1])
]

if customer_search:
    filtered_df = filtered_df[
        filtered_df["customer_id"]
        .astype(str)
        .str.contains(customer_search, case=False)
    ]

if merchant_search:
    filtered_df = filtered_df[
        filtered_df["merchant_id"]
        .astype(str)
        .str.contains(merchant_search, case=False)
    ]

if show_only_fraud:
    filtered_df = filtered_df[
        filtered_df["fraud_flag"] == True
    ]

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

total_transactions = len(filtered_df)

total_amount = filtered_df[
    "transaction_amount"
].sum()

average_risk = filtered_df[
    "risk_score"
].mean()

high_risk_transactions = len(
    filtered_df[
        filtered_df["risk_score"] >= 80
    ]
)

fraud_transactions = filtered_df[
    "fraud_flag"
].sum()

fraud_rate = (
    fraud_transactions /
    total_transactions * 100
) if total_transactions > 0 else 0

unique_customers = filtered_df[
    "customer_id"
].nunique()

unique_merchants = filtered_df[
    "merchant_id"
].nunique()

# ==========================================================
# KPI ROW 1
# ==========================================================

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Transactions",
    f"{total_transactions:,}"
)

k2.metric(
    "Total Amount",
    f"₹ {total_amount:,.2f}"
)

k3.metric(
    "Average Risk Score",
    f"{average_risk:.2f}"
)

k4.metric(
    "High Risk Transactions",
    f"{high_risk_transactions:,}"
)

# ==========================================================
# KPI ROW 2
# ==========================================================

k5, k6, k7, k8 = st.columns(4)

k5.metric(
    "Fraud Transactions",
    f"{fraud_transactions:,}"
)

k6.metric(
    "Fraud Rate",
    f"{fraud_rate:.2f}%"
)

k7.metric(
    "Unique Customers",
    f"{unique_customers:,}"
)

k8.metric(
    "Unique Merchants",
    f"{unique_merchants:,}"
)

st.markdown("---")

# ==========================================================
# RISK CATEGORY
# ==========================================================

filtered_df["risk_category"] = pd.cut(
    filtered_df["risk_score"],
    bins=[0, 30, 60, 80, 100],
    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk",
        "Critical Risk"
    ]
)

risk_dist = (
    filtered_df["risk_category"]
    .value_counts()
    .reset_index()
)

risk_dist.columns = [
    "Risk Category",
    "Transactions"
]

chart1, chart2 = st.columns(2)

with chart1:
    fig = px.bar(
        risk_dist,
        x="Risk Category",
        y="Transactions",
        text="Transactions",
        title="Fraud Risk Categories"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart2:
    fig = px.pie(
        filtered_df,
        names="transaction_type",
        title="Transaction Type Distribution"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# SECOND ROW OF CHARTS
# ==========================================================

chart3, chart4 = st.columns(2)

with chart3:
    bank_df = (
        filtered_df.groupby("bank")
        ["fraud_flag"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        bank_df,
        x="bank",
        y="fraud_flag",
        title="Fraud by Bank"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart4:
    state_df = (
        filtered_df.groupby("state")
        ["fraud_flag"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        state_df,
        x="state",
        y="fraud_flag",
        title="Fraud by State"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# THIRD ROW OF CHARTS
# ==========================================================

chart5, chart6 = st.columns(2)

with chart5:
    merchant_df = (
        filtered_df.groupby(
            "merchant_category"
        )["fraud_flag"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        merchant_df,
        x="merchant_category",
        y="fraud_flag",
        title="Fraud by Merchant Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart6:
    filtered_df["fraud_probability_band"] = pd.cut(
    filtered_df["fraud_probability"],
    bins=[0, 0.25, 0.50, 0.75, 1.00],
    labels=[
        "Low (0-25%)",
        "Medium (25-50%)",
        "High (50-75%)",
        "Critical (75-100%)"
    ],
    include_lowest=True
)

probability_df = (
    filtered_df["fraud_probability_band"]
    .value_counts()
    .reset_index()
)

probability_df.columns = [
    "Fraud Probability",
    "Transactions"
]

fig = px.bar(
    probability_df,
    x="Fraud Probability",
    y="Transactions",
    text="Transactions",
    title="Fraud Probability Categories"
)

fig.update_layout(
    xaxis_title="Fraud Probability Category",
    yaxis_title="Transaction Count"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
# ==========================================================
# TRANSACTION TABLE
# ==========================================================

st.subheader("Latest Transactions")

rows = st.selectbox(
    "Rows to Display",
    [20, 50, 100, 250, 500],
    index=0
)

st.dataframe(
    filtered_df.head(rows),
    use_container_width=True,
    height=650
)

st.markdown("---")

st.caption(
    "Enterprise Fraud Intelligence Platform | "
    "Kafka | Spark | PostgreSQL | Streamlit"
)