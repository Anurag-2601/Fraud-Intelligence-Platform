# Fraud Intelligence Platform
### Real-Time Fraud Analytics & Behavioral Anomaly Detection System

An enterprise-style end-to-end fraud intelligence platform designed to simulate, process, analyze, and visualize financial transactions in real time using modern data engineering technologies.

The platform leverages Apache Kafka, Apache Spark Structured Streaming, PostgreSQL, and Streamlit to build a production-style fraud monitoring solution capable of detecting suspicious financial activity through rule-based risk scoring and behavioral anomaly detection.

---

## Project Highlights

- Real-time transaction simulation engine
- Fraud scenario injection framework
- Kafka-based event streaming architecture
- Spark Structured Streaming pipeline
- Medallion Architecture implementation (Bronze → Silver → Gold)
- Rule-based fraud detection engine
- Customer and merchant risk scoring
- PostgreSQL analytical warehouse
- Interactive Streamlit dashboard
- Production-style ETL orchestration

---

## Architecture

```text
Transaction Simulator
        ↓
Fraud Scenario Engine
        ↓
Kafka Producer
        ↓
Kafka Topic (fraud_transactions)
        ↓
Spark Structured Streaming
        ↓
Bronze Layer
        ↓
Silver Layer
        ↓
Gold Layer
        ↓
PostgreSQL Warehouse
        ↓
Streamlit Dashboard
```

---

## Technology Stack

| Category | Technologies |
|----------|-------------|
| Programming | Python |
| Streaming | Apache Kafka |
| Stream Processing | Apache Spark Structured Streaming |
| Storage Format | Apache Parquet |
| Data Warehouse | PostgreSQL |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data Processing | Pandas |
| Architecture | Medallion Architecture |

---

## Core Features

### Real-Time Transaction Processing
- Generates realistic financial transaction streams
- Supports customer behavioral simulation
- Simulates merchant activity and transaction patterns

### Fraud Detection Engine
- High-value transaction detection
- Transaction velocity analysis
- New device detection
- Night-time transaction monitoring
- Merchant category risk analysis
- Rule-based risk scoring

### Medallion Architecture

#### Bronze Layer
- Raw immutable transaction ingestion
- Historical replay capability
- Schema preservation

#### Silver Layer
- Data cleaning
- Feature engineering
- Data validation
- Standardization

#### Gold Layer
- Customer risk metrics
- Merchant risk metrics
- Fraud aggregations
- Dashboard-ready datasets

---

## Fraud Detection Logic

| Fraud Indicator | Condition |
|----------------|-----------|
| High Amount Transaction | Amount > ₹100,000 |
| Velocity Fraud | More than 5 transactions within 5 minutes |
| New Device Usage | Customer uses unseen device |
| Night Activity | Transactions between 12 AM and 5 AM |
| High Risk Merchant Category | Suspicious merchant category detected |

---

## Project Structure

```text
Fraud-Intelligence-Platform/
│
├── config/
├── database/
├── dashboards/
├── docs/
├── fraud_engine/
├── logs/
├── notebooks/
├── simulator/
├── spark/
├── streaming/
├── tests/
│
├── multi_gold_to_postgres_loader.py
├── warehouse_refresh_scheduler.py
└── README.md
```

---

## Dashboard Capabilities

- Fraud Monitoring Dashboard
- Transaction Distribution Analysis
- Merchant Risk Analysis
- Customer Risk Analysis
- Fraud Trend Visualization
- High-Risk Transaction Tracking
- Interactive Filtering and Drilldowns

---

## Skills Demonstrated

### Data Engineering
- Apache Kafka
- Apache Spark
- Streaming ETL Pipelines
- Medallion Architecture
- Data Warehousing
- PostgreSQL

### Data Analytics
- Fraud Analytics
- Behavioral Analysis
- Risk Scoring
- KPI Development
- Dashboard Design

### Software Engineering
- Modular Architecture
- Configuration Management
- Logging
- Documentation
- Pipeline Orchestration

---

## Use Cases

- Banking Fraud Monitoring
- Payment Fraud Detection
- Transaction Risk Analysis
- Merchant Risk Monitoring
- Behavioral Anomaly Detection
- Financial Crime Analytics

---

## Future Enhancements

- Machine Learning Fraud Scoring
- XGBoost Risk Prediction
- Isolation Forest Anomaly Detection
- Real-Time Alert Notifications
- Docker Deployment
- Cloud Deployment

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Anurag-2601/Fraud-Intelligence-Platform.git
cd Fraud-Intelligence-Platform
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Kafka

```bash
zookeeper-server-start.bat config/zookeeper.properties

kafka-server-start.bat config/server.properties
```

### Run Streaming Pipeline

```bash
python simulator/simulator.py

python spark/bronze.py
python spark/silver.py
python spark/gold.py
```

### Load Warehouse

```bash
python multi_gold_to_postgres_loader.py
python warehouse_refresh_scheduler.py
```

### Launch Dashboard

```bash
streamlit run dashboards/app.py
```

---

## Author

**Pallela Anurag**

Computer Science Engineering Graduate

Osmania University

Interested in:
- Data Analytics
- Fraud Analytics
- Risk Analytics
- Data Engineering
- Analytics Engineering
