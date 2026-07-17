-- Total Transactions
SELECT COUNT(*) FROM fraud.fact_transactions;

-- Fraud Rate
SELECT AVG(is_fraud::int)*100
FROM fraud.fact_transactions;

-- High Risk Transactions
SELECT COUNT(*)
FROM fraud.fact_transactions
WHERE risk_level='HIGH';
