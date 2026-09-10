# Utility functions to interact with PostgreSQL AWS database

# Imports
import psycopg
import pandas as pd

from loguru import logger
from dotenv import dotenv_values
from psycopg.types.json import Jsonb

# ------------------------------------------


class DB:
    """
    Class of utility functions to interact with PostgreSQL AWS database

    Require AWS credentials in the `.env` file to automatically pick up.
    """

    # Class constructor
    def __init__(self, env_path: str):
        """
        Initialise the DB class and retrieve credentials from the .env file.

        Args:
            env_path (str): Path to the .env file. `.env` file must include these variables: `aws_host`, `aws_user`, `aws_pass`, `aws_db`.
        """
        # Retrieve credentials from .env file
        self.aws_host: str = dotenv_values(env_path).get("AWS_HOST", None)
        self.aws_user: str = dotenv_values(env_path).get("AWS_USER", None)
        self.aws_pass: str = dotenv_values(env_path).get("AWS_PASS", None)
        self.aws_db: str = dotenv_values(env_path).get("AWS_DB", None)

        # Perform a credential check
        self.credential_checks()

        # Connect to the database
        self.conn = self.connect()

    # Check for credentials
    def credential_checks(self) -> None:
        """
        Perform checks for whether AWS credentials have been retrieved successfully.
        """
        required: dict = {
            "AWS_HOST": self.aws_host,
            "AWS_USER": self.aws_user,
            "AWS_PASS": self.aws_pass,
            "AWS_DB": self.aws_db,
        }
        missing: list = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Cannot find {', '.join(missing)} in the `.env` file."
                "Please make sure all credentials are present in the `.env` file!"
            )
        else:
            logger.success(
                "All necessary credentials found. Connecting to the database..."
            )

    # Set up connection
    def connect(self) -> psycopg.Connection:
        """
        Create connection to the PostgreSQL database.

        Returns:
            psycopg.Connection: Connection object from `psycopg`.
        """
        conn = psycopg.connect(
            conninfo=f"host={self.aws_host} user={self.aws_user} password={self.aws_pass} dbname={self.aws_db}",
            autocommit=True,
        )

        # Fetch the current database version as a test
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT version();").fetchall()
                logger.success("Successfully created connection!")
                cur.close()
            except Exception as e:
                logger.error(f"Failed to create connection with the database: {e}")

        return conn

    # Upsert data
    def upsert(self, df: pd.DataFrame, table: str) -> bool:
        """
        Upserting data in a DataFrame to the specified table.

        Args:
            df (pd.DataFrame): DataFrame containing the data to be upserted.

                **Note:** Column names of DataFrame must match column names in the specified table.

            table (str): Name of the table where the data will be upserted to.

        Returns:
            b
        """

        # Performs check on the dataframe
        if len(df) == 0:
            raise IndexError(
                "Cannot find the first row in the dataframe. Is there data in the specified dataframe?"
            )

        with self.conn.cursor() as df_check_cur:
            try:
                # Get the column names from the table
                response: list = df_check_cur.execute(
                    query=f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';",
                ).fetchall()
                expected_columns: list = [column[0] for column in response]

                # Check for number of columns
                if len(df.columns) != len(expected_columns):
                    raise IndexError(
                        f"Specified dataframe does not have enough columns (expected {len(expected_columns)}, given {len(df.columns)}.)"
                    )
                elif len(set(df.columns) - set(expected_columns)) > 0:
                    raise ValueError(
                        f"Cannot find the expected columns in table {table} (expected {", ".join(expected_columns)}), given {", ".join(df.columns.to_list())}"
                    )
            except Exception as e:
                logger.error(
                    f"Cannot validate the columns of the specified dataframe: {e}"
                )
                return False

        # Create a cursor
        with self.conn.cursor() as upsert_cur:
            try:
                # Build the `update set` section of the query
                cols_to_update: pd.Index[str] = df.columns[1:]
                set_section: str = ", ".join(
                    f"{col} = EXCLUDED.{col}" for col in cols_to_update
                )

                # Upsert data (assuming first column is the ID column)
                upsert_cur.executemany(
                    query=f"""
                        INSERT INTO {table} ({", ".join(df.columns)}) 
                        VALUES ({", ".join(["%s"] * len(df.columns))})
                        ON CONFLICT ({df.columns[0]})
                        DO UPDATE SET
                            {set_section}
                    """,
                    params_seq=[tuple(row) for row in df.itertuples(index=False)],
                )
                logger.success(
                    f"Successfully upserted {len(df)} rows to table {table}!"
                )

                # Commit the upsert results
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to upsert data to table {table}: {e}")
                return False

    # Select data
    def select(
        self,
        table: str,
        columns: list[str] | None = None,
        filters: list[tuple] | None = None,
    ) -> list:
        """
        Select data from a specific table and filter that data.

        Args:
            table (str): Name of the table to select data from.
            columns (list[str] | None): List of columns in the specified table to select data from. Leave it at None (default) to select all columns.
            filters (list[tuple] | None): List of filters to apply to the `where` section of the query. Default is None for no filtering required.

                Tuples have to be arranged in this order: (`column_name`, `operation`, `filter_value`)

        Returns:
            list: List of data rows from the specified table.
        """
        # Checks
        if (not columns) and (len(columns) == 0):
            logger.warning(
                "No column names found. Defaulting to selecting all columns."
            )
            columns = None
        if (not filters) and (len(filters) == 0):
            logger.warning(
                "No filtering conditions found. Will not include filter conditions in the final query."
            )
            filters = None
