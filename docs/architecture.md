# Fraud Intelligence Platform Architecture

## Overview

The Fraud Intelligence Platform is an end-to-end real-time fraud analytics and behavioral anomaly detection system designed to simulate, process, analyze, and visualize financial transactions.

The platform combines data engineering, streaming analytics, fraud detection, and business intelligence into a single production-style architecture.

---

## Architecture Flow

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
Bronze Layer (Raw Data)
        ↓
Silver Layer (Cleaned Data)
        ↓
Gold Layer (Aggregated Metrics)
        ↓
PostgreSQL Warehouse
        ↓
Streamlit Dashboard

---

## Components

### 1. Transaction Simulator
Generates realistic financial transactions for customers using:
- Customer profiles
- Merchant profiles
- Device information
- Geographic locations
- Behavioral patterns

---

### 2. Fraud Scenario Engine
Injects realistic fraud scenarios into transaction streams including:
- High value transactions
- Suspicious merchant activity
- Abnormal customer behavior
- Device anomalies

---

### 3. Kafka Streaming Layer
Kafka acts as the real-time messaging system between transaction generation and stream processing.

Topic:
- fraud_transactions

---

### 4. Spark Structured Streaming
Processes transactions in real time and moves them through the Medallion Architecture.

---

### 5. Bronze Layer
Stores raw immutable transaction data exactly as received from Kafka.

---

### 6. Silver Layer
Performs:
- Data cleaning
- Data standardization
- Feature engineering
- Quality validation

---

### 7. Gold Layer
Creates business-ready datasets:
- Customer Risk Metrics
- Merchant Risk Metrics
- Fraud Alerts
- Transaction Aggregations

---

### 8. PostgreSQL Warehouse
Stores analytical datasets optimized for dashboard consumption and reporting.

---

### 9. Streamlit Dashboard
Provides:
- Fraud monitoring
- Risk visualization
- Merchant analysis
- Customer analysis
- Transaction exploration

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Programming | Python |
| Messaging | Apache Kafka |
| Streaming | Apache Spark |
| Storage | Parquet |
| Data Warehouse | PostgreSQL |
| Dashboard | Streamlit |
| Visualization | Plotly |
