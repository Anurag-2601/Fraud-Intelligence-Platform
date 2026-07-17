CREATE OR REPLACE VIEW fraud.high_risk_transactions AS
SELECT *
FROM fraud.fact_transactions
WHERE risk_level='HIGH';
