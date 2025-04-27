import pandas as pd
from config import settings
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine


def get_engine():
    db_url = (
        f"postgresql+psycopg2://{settings.PG_USER}:{settings.PG_PASSWORD}"
        f"@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}"
    )
    return create_engine(db_url)


def get_client_loans(
    engine,
    client_id: int,
    current_loan_id: int,
    current_created_on: str,
):
    query = f"""
        SELECT * FROM loan
        WHERE client_id = {client_id}
          AND id != {current_loan_id}
          AND created_on < '{current_created_on}'
    """
    return pd.read_sql_query(query, engine)


def get_days_since_last_late_payment(engine, client_id: int):
    query = f"""
        SELECT COALESCE((NOW()::date - MAX(payment.created_on)::date), 0) AS days_since_last_late_payment
        FROM payment
        JOIN loan ON payment.loan_id = loan.id
        WHERE loan.client_id = {client_id} AND payment.status = 'late'
    """
    return pd.read_sql_query(query, engine)


def get_profit_in_last_90_days(engine, client_id: int, loan_created_on: str):
    loan_created_on_date = datetime.strptime(loan_created_on, "%Y-%m-%d").date()
    date_90_days_ago = loan_created_on_date - timedelta(days=90)
    query = f"""
        WITH recent_loans AS (
            SELECT id, amount
            FROM loan
            WHERE client_id = {client_id}
              AND created_on >= '{date_90_days_ago}'
        ),
        recent_payments AS (
            SELECT interest, loan_id
            FROM payment
            WHERE loan_id IN (SELECT id FROM recent_loans)
        )
        SELECT COALESCE(SUM(interest), 0) AS sum_interest FROM recent_payments
    """
    return pd.read_sql_query(query, engine)
