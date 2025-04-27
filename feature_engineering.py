import pandas as pd
from db_utils import get_engine, get_client_loans, get_days_since_last_late_payment, get_profit_in_last_90_days


def calc_paid_loans_count(loans_df):
    if loans_df.empty:
        return 0
    return (loans_df["status"] == "paid").sum()


def calc_days_since_last_late_payment(payments_df: pd.DataFrame) -> int:
    if payments_df.empty:
        return 0
    return payments_df.iloc[0, 0]


def calculate_features(payload_json: dict) -> dict:
    data = payload_json.get("data", {})
    if not data:
        return {}
    features = {}
    client_id = data.get("client_id") or data.get("id")
    current_loan_id = data.get("id")
    current_created_on = data.get("created_on")
    features["new_loan_user_id"] = client_id
    features["new_loan_amount"] = data.get("amount")
    features["new_loan_status"] = data.get("status")

    engine = get_engine()
    loans_df = get_client_loans(engine, client_id, current_loan_id, current_created_on)
    features["client_paid_loans_count"] = calc_paid_loans_count(loans_df)
    payments_df = get_days_since_last_late_payment(engine, client_id)
    features["client_days_since_last_late_payment_count"] = calc_days_since_last_late_payment(payments_df)
    profit_row = get_profit_in_last_90_days(engine, client_id, current_created_on)
    sum_interest = profit_row.iloc[0]["sum_interest"]
    features["client_profit_in_last_90_days_rate"] = sum_interest
    # Convert all numpy types to native Python types for JSON serialization
    features = {k: (v.item() if hasattr(v, "item") else v) for k, v in features.items()}
    return features
