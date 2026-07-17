CREATE OR REPLACE VIEW fraud.customer_risk_view AS
SELECT *
FROM fraud.customer_risk_metrics
ORDER BY risk_score DESC;
