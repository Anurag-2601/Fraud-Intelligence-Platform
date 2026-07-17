# Medallion Architecture

The Fraud Intelligence Platform follows the Medallion Architecture consisting of Bronze, Silver, and Gold layers.

---

# Bronze Layer

## Purpose
Store raw transaction data exactly as received from Kafka.

## Characteristics
- Immutable
- Schema preservation
- Historical replay capability
- No business transformations

## Example Fields

- transaction_id
- customer_id
- merchant_id
- amount
- timestamp
- device_id
- merchant_category

---

# Silver Layer

## Purpose
Create trusted and validated transactional datasets.

## Transformations Performed

- Missing value handling
- Timestamp standardization
- Duplicate removal
- Data type corrections
- Derived feature creation

## Additional Features

- Transaction hour
- Day of week
- Transaction velocity
- Device risk indicators

---

# Gold Layer

## Purpose
Generate business-ready datasets for analytics and dashboards.

## Gold Datasets

### Customer Risk Metrics
Contains:
- Total transactions
- Fraud count
- Fraud rate
- Average transaction amount
- Risk score

---

### Merchant Risk Metrics
Contains:
- Merchant transaction volume
- Fraud count
- Fraud rate
- Average amount
- Risk score

---

### Fraud Alerts
Contains:
- High-risk transactions
- Alert type
- Alert severity

---

## Benefits of Medallion Architecture

- Improved data quality
- Better scalability
- Simplified analytics
- Historical traceability
- Reproducible processing pipelines
