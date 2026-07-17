CREATE OR REPLACE VIEW fraud.merchant_risk_view AS
SELECT *
FROM fraud.merchant_risk_metrics
ORDER BY risk_score DESC;
