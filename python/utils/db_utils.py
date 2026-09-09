# Utility functions to interact with PostgreSQL AWS database

# Imports
import psycopg

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
    def credential_checks(self):
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
                logger.error(f"Fail to create connection with the database : {e}")

        return conn

    # Upsert data
    def upsert(self):
        pass

    # Select data
    def select(self):
        pass
