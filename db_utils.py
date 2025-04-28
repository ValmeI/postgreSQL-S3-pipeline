import pandas as pd
from config import settings
from datetime import datetime, timedelta
from sqlalchemy import create_engine


from app_logging import logger


class Database_Utils:
    def __init__(self):
        logger.info("Initializing Database connection...")
        db_url = (
            f"postgresql+psycopg2://{settings.PG_USER}:{settings.PG_PASSWORD}"
            f"@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}"
        )
        self.engine = create_engine(db_url)
        logger.info(f"Database connection established: {self.engine}")

    def get_client_loans(
        self,
        client_id: int,
        current_loan_id: int,
        current_created_on: str,
    ):
        logger.info(
            f"Fetching client loans for client_id: {client_id}, current_loan_id: {current_loan_id}, current_created_on: {current_created_on}"
        )
        query = f"""
            SELECT * FROM loan
            WHERE client_id = {client_id}
            AND id != {current_loan_id}
            AND created_on < '{current_created_on}'
        """
        logger.debug(f"Executing query: {query}")
        return pd.read_sql_query(query, self.engine)

    def get_days_since_last_late_payment(self, client_id: int):
        logger.info(f"Fetching days since last late payment for client_id: {client_id}")
        query = f"""
            SELECT COALESCE((NOW()::date - MAX(payment.created_on)::date), 0) AS days_since_last_late_payment
            FROM payment
            JOIN loan ON payment.loan_id = loan.id
            WHERE loan.client_id = {client_id} AND payment.status = 'late'
        """
        logger.debug(f"Executing query: {query}")
        return pd.read_sql_query(query, self.engine)

    def get_profit_in_last_90_days(self, client_id: int, loan_created_on: str):
        loan_created_on_date = datetime.strptime(loan_created_on, "%Y-%m-%d").date()
        date_90_days_ago = loan_created_on_date - timedelta(days=90)
        logger.info(f"Fetching profit in last 90 days for client_id: {client_id}, loan_created_on: {loan_created_on}")
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
        logger.debug(f"Executing query: {query}")
        return pd.read_sql_query(query, self.engine)
