# Fraud Detection Logic

The Fraud Intelligence Platform uses a rule-based fraud detection framework to identify suspicious financial behavior.

---

# Fraud Indicators

## 1. High Transaction Amount

Condition:

Transaction Amount > ₹100,000

Risk Impact:

+0.35 Risk Score

---

## 2. Rapid Transaction Velocity

Condition:

More than 5 transactions within 5 minutes.

Risk Impact:

+0.25 Risk Score

---

## 3. New Device Usage

Condition:

Customer uses an unseen device.

Risk Impact:

+0.20 Risk Score

---

## 4. Night-Time Transactions

Condition:

Transactions between 12:00 AM and 5:00 AM.

Risk Impact:

+0.15 Risk Score

---

## 5. High Risk Merchant Categories

Examples:

- Gambling
- Cryptocurrency
- Gift Cards
- Online Wallets

Risk Impact:

+0.30 Risk Score

---

# Risk Score Calculation

Total Risk Score is calculated by summing the individual fraud indicators.

Example:

High Amount Transaction:
0.35

New Device:
0.20

Night Transaction:
0.15

Final Risk Score:
0.70

---

# Risk Classification

| Score Range | Risk Level |
|------------|-----------|
| 0.00 - 0.30 | LOW |
| 0.31 - 0.60 | MEDIUM |
| 0.61 - 1.00 | HIGH |

---

# Fraud Alert Generation

Transactions classified as HIGH risk generate fraud alerts for investigation.

The generated alerts can be visualized in the dashboard and prioritized by analysts.
