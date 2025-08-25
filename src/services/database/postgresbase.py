"""
PostgreSQL Database Utility using SQLAlchemy.
Provides functionality to fetch and save pandas DataFrames to PostgreSQL.
"""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import logging
import asyncio

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# PostgreSQL Database Handler
class PostgresDB:
    """
    Handles PostgreSQL database operations using SQLAlchemy.
    """

    def __init__(
        self,
        user: str = "postgres",
        password: str = "913791",
        host: str = "postgres-service",
        port: int = 5432,
        db_name: str = "stockdb",
    ):
        """
        Initializes the PostgresDB connection.
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.engine = self._db_connect()

    def _db_connect(self):
        """
        Establishes a connection to the PostgreSQL database.

        Returns:
            SQLAlchemy Engine object or None if connection fails.
        """
        try:
            engine = create_engine(
                f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            )
            logging.info(f"Connected to PostgreSQL database: {self.db_name}")
            return engine
        except Exception as e:
            logging.error(f"Unable to connect to the database: {e}")
            return None

    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Fetches data from PostgreSQL.

        Args:
            query (str): SQL query string.

        Returns:
            pd.DataFrame: Query results. Empty DataFrame if error occurs.
        """
        if self.engine is None:
            logging.warning("Database engine not initialized. Returning empty DataFrame.")
            return pd.DataFrame()
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql(query, connection)
                logging.info(f"Fetched {len(df)} records from database.")
                return df
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    async def save_data(self, dataframe: pd.DataFrame, table_name: str, if_exists: str = "replace"):
        """
        Saves a pandas DataFrame to PostgreSQL.

        Args:
            dataframe (pd.DataFrame): Data to save.
            table_name (str): Target table name.
            if_exists (str): Behavior if table exists ("replace", "append", "fail").
        """
        if self.engine is None:
            logging.warning("Database engine not initialized. Data not saved.")
            return
        try:
            with self.engine.connect() as connection:
                dataframe.to_sql(table_name, connection, if_exists=if_exists, index=False)
                logging.info(f"Data saved to table '{table_name}' successfully.")
        except Exception as e:
            logging.error(f"Error saving data: {e}")


if __name__ == "__main__":
    db = PostgresDB()

    # Path to CSV
    csv_data = Path(__file__).resolve().parents[3] / "assets" / "dataPrice" / "dataPriceAMZN.csv"

    if csv_data.exists():
        # Save CSV to DB
        df = pd.read_csv(csv_data)
        asyncio.run(db.save_data(df, "dataPriceAMZN"))

        # Fetch sample from DB
        result = db.fetch_data('SELECT * FROM "dataPriceAMZN" LIMIT 5;')
        logging.info(f"\n{result}\nType: {type(result)}")
    else:
        logging.error(f"CSV file not found at {csv_data}")
