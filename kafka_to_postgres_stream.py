import json
import psycopg2
from kafka import KafkaConsumer

# ---------------------------------------
# PostgreSQL Connection
# ---------------------------------------

connection = psycopg2.connect(
    host="localhost",
    port=5432,
    database="fraud_intelligence",
    user="postgres",
    password="Anurag@2601"
)

cursor = connection.cursor()

print("Connected to PostgreSQL")

# ---------------------------------------
# Kafka Consumer
# ---------------------------------------

consumer = KafkaConsumer(
    "fraud-transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="fact-transactions-loader",
    value_deserializer=lambda x: json.loads(
        x.decode("utf-8")
    )
)

print("Kafka consumer started...")

# ---------------------------------------
# Consume Kafka Messages
# ---------------------------------------

for message in consumer:

    txn = message.value

    try:

        # ---------------------------------------
        # Derived Fraud Fields
        # ---------------------------------------

        fraud_type = txn.get(
            "fraud_type",
            "NONE"
        )

        risk_score = txn.get(
            "risk_score",
            0
        )

        fraud_probability = round(
            risk_score / 100,
            2
        )

        fraud_flag = (
            fraud_type != "NONE"
        )

        # ---------------------------------------
        # Insert Into PostgreSQL
        # ---------------------------------------

        cursor.execute(
            """
            INSERT INTO fraud.fact_transactions (
                transaction_id,
                transaction_time,

                customer_id,
                device_id,
                merchant_id,

                merchant_category,
                transaction_type,

                transaction_amount,

                city,
                state,
                bank,

                status,

                risk_score,
                fraud_probability,
                fraud_flag,
                fraud_type,

                created_at
            )
            VALUES (
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s,
                %s, %s, %s,
                %s,
                %s, %s, %s, %s,
                NOW()
            )
            ON CONFLICT (transaction_id)
            DO NOTHING
            """,
            (
                txn.get("transaction_id"),
                txn.get("timestamp"),

                txn.get("customer_id"),
                txn.get("device_id"),
                txn.get("merchant_id"),

                txn.get("merchant_category"),
                txn.get("transaction_type"),

                txn.get("amount"),

                txn.get("city"),
                txn.get("state"),
                txn.get("bank"),

                txn.get("status"),

                risk_score,
                fraud_probability,
                fraud_flag,
                fraud_type
            )
        )

        connection.commit()

        print(
            f"Inserted "
            f"{txn.get('transaction_id')} | "
            f"Amount={txn.get('amount')} | "
            f"Fraud={fraud_type} | "
            f"Risk={risk_score}"
        )

    except Exception as e:

        print(
            f"Insert failed: {e}"
        )

        connection.rollback()