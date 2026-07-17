CREATE INDEX idx_transaction_time
ON fraud.fact_transactions(transaction_time);

CREATE INDEX idx_customer_id
ON fraud.fact_transactions(customer_id);

CREATE INDEX idx_merchant_id
ON fraud.fact_transactions(merchant_id);

CREATE INDEX idx_risk_level
ON fraud.fact_transactions(risk_level);
