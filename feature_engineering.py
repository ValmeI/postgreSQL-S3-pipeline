import pandas as pd
from db_utils import Database_Utils
from app_logging import logger


def calc_paid_loans_count(loans_df: pd.DataFrame) -> int:
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
        logger.warning("No data in input payload")
        return {}
    client_id = data.get("client_id")
    current_loan_id = data.get("id")
    current_created_on = data.get("created_on")
    db = Database_Utils()
    loans_df = db.get_client_loans(client_id, current_loan_id, current_created_on)
    data["client_paid_loans_count"] = calc_paid_loans_count(loans_df)
    payments_df = db.get_days_since_last_late_payment(client_id)
    data["client_days_since_last_late_payment_count"] = calc_days_since_last_late_payment(payments_df)
    profit_row = db.get_profit_in_last_90_days(client_id, current_created_on)
    sum_interest = profit_row.iloc[0]["sum_interest"]
    data["client_profit_in_last_90_days_rate"] = sum_interest
    # Convert all numpy types to native Python types for JSON serialization
    data_with_features = {k: (v.item() if hasattr(v, "item") else v) for k, v in data.items()}
    return data_with_features
