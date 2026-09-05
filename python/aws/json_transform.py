# Access JSON files on S3, list them, and transform them into PostgreSQL.

# Imports
import os
import json
import boto3

from loguru import logger
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()


# -------------------------------------------------------------
# Extract files from S3 bucket
def extract_files(
    bucket_name: str,
    prefix: str = "",
) -> list[str]:
    """
    Extract files from specified S3 bucket.

    Args:
        bucket_name (str): Name of the S3 bucket.
        prefix (str): Prefix to filter files in the bucket.

    Returns:
        list: List of file keys in the specified S3 bucket.
    """

    # Authenticate with S3
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Check for Contents
    if "Contents" not in response:
        logger.warning(
            f"No files found in bucket '{bucket_name}' with prefix '{prefix}'."
        )
        return []
    else:
        files = [
            obj["Key"]
            for obj in response.get("Contents", [])
            if obj["Key"].endswith(".json")
        ]
        logger.info(
            f"Found {len(files)} JSON files in bucket '{bucket_name}' with prefix '{prefix}'."
        )
        return files


# -------------------------------------------------------------
if __name__ == "__main__":
    bucket_name = "mat-raw-data-files"
    prefix = "3kqpx2mwvn7e4rft6lhcbj8ys/matches/"

    files = extract_files(bucket_name, prefix)
    logger.info(f"Extracted files: {files}")
