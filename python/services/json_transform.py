# Access JSON files on S3, list them, and transform them into PostgreSQL.

# Imports
import os
import json

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# -------------------------------------------------------------
