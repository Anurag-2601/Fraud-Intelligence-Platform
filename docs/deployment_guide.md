# Deployment Guide

## Prerequisites

Install:

- Python 3.11+
- Java 17
- Apache Kafka
- PostgreSQL
- Apache Spark

---

# Step 1: Start Zookeeper

```bash
zookeeper-server-start.bat config/zookeeper.properties
```

---

# Step 2: Start Kafka

```bash
kafka-server-start.bat config/server.properties
```

---

# Step 3: Create Kafka Topic

```bash
kafka-topics.bat --create ^
--topic fraud_transactions ^
--bootstrap-server localhost:9092 ^
--partitions 1 ^
--replication-factor 1
```

---

# Step 4: Start Transaction Producer

```bash
python kafka_producer.py
```

---

# Step 5: Start Spark Streaming Jobs

Bronze Layer:

```bash
python bronze.py
```

Silver Layer:

```bash
python silver.py
```

Gold Layer:

```bash
python gold.py
```

---

# Step 6: Load Gold Data into PostgreSQL

```bash
python multi_gold_to_postgres_loader.py
```

---

# Step 7: Start Warehouse Scheduler

```bash
python warehouse_refresh_scheduler.py
```

---

# Step 8: Launch Dashboard

```bash
streamlit run dashboard/app.py
```

---

# Platform Workflow

Simulator
    ↓
Kafka
    ↓
Spark Bronze
    ↓
Spark Silver
    ↓
Spark Gold
    ↓
PostgreSQL
    ↓
Streamlit Dashboard

---

# Project Status

Completed Components:

- Transaction Simulator
- Fraud Injection Engine
- Kafka Producer
- Spark Streaming Pipeline
- Bronze Layer
- Silver Layer
- Gold Layer
- PostgreSQL Warehouse
- Streamlit Dashboard
