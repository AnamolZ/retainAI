import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

class PostgresDB:
    """
    Handles PostgreSQL database operations using SQLAlchemy.
    """

    def __init__(self, user="postgres", password="913791", host="postgres-service", port=5432, db_name="stockdb"):
        """
        Initializes the PostgresDB connection details.
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
            SQLAlchemy engine object or None if connection fails.
        """
        try:
            engine = create_engine(
                f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            )
            return engine
        except Exception as e:
            print(f"ERROR: Unable to connect to the database: {e}")
            return None

    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Fetches data from the PostgreSQL database.
        Args:
            query (str): SQL query string.
        Returns:
            pd.DataFrame: Query results.
        """
        if self.engine is None:
            return pd.DataFrame()
        try:
            with self.engine.connect() as connection:
                return pd.read_sql(query, connection)
        except Exception as e:
            print(f"ERROR: An error occurred while fetching data: {e}")
            return pd.DataFrame()

    async def save_data(self, dataframe: pd.DataFrame, table_name: str, if_exists="replace"):
        """
        Saves a pandas DataFrame to the PostgreSQL database.
        Args:
            dataframe (pd.DataFrame): Data to save.
            table_name (str): Target table name.
            if_exists (str): Behavior when the table exists ("replace", "append", "fail").
        """
        if self.engine is None:
            return
        try:
            with self.engine.connect() as connection:
                dataframe.to_sql(table_name, connection, if_exists=if_exists, index=False)
                print(f"Data saved to table '{table_name}'")
        except Exception as e:
            print(f"ERROR: An error occurred while saving data: {e}")


if __name__ == "__main__":
    db = PostgresDB()

    csvData = Path(__file__).resolve().parents[3] / "assets" / "dataPrice" / "dataPriceAMZN.csv"

    if csvData.exists():
        # Save to DB
        df = pd.read_csv(csvData)
        import asyncio; asyncio.run(db.save_data(df, "dataPriceAMZN"))

        # Fetch from DB
        result = db.fetch_data('SELECT * FROM "dataPriceAMZN" LIMIT 5;')
        print(result)
        print(type(result))
    else:
        print(f"CSV file not found at {csvData}")