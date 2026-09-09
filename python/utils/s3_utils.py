# Class of utility functions to interact with S3

# Imports
import json
import boto3
import os.path

from loguru import logger
from botocore.exceptions import ClientError


# -------------------------------------------------------------
class S3:
    """
    Class of utility functions to interact with S3 buckets.

    Require AWS credentials configured for `boto3` to automatically pick up.
    """

    # Class constructor
    def __init__(self):
        # Global authentication
        self.s3_client = boto3.client("s3")

    def list_files(self, bucket_name: str, prefix: str = "") -> list[str]:
        """
        List all files in the specified S3 bucket and folder.

        Args:
            bucket_name (str): Name of the S3 bucket.
            prefix (str): Prefix to filter files in the bucket.

        Returns:
            list: List of files in the specified S3 bucket.
        """
        try:
            # Get all files from the specified bucket
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            # Check for contents from response
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
        except ClientError as e:
            logger.error(f"Error with S3 client: {e}")
            return []

    def upload_file(self, file_name: str, bucket_name: str, key: str = "") -> bool:
        """
        Upload a specified file to the specified S3 bucket.

        Args:
            file_name (str): File name, and/or path leading to the file.
            bucket_name (str): Name of the S3 bucket.

        Returns:
            bool: True if the file was successfully uploaded, False if it was not.
        """

        try:
            is_upload_succeed: bool = self.s3_client.upload_file(
                Filename=file_name, Bucket=bucket_name, Key=key
            )

            if is_upload_succeed:
                logger.success(
                    f"{file_name} successfully uploaded to bucket {bucket_name}."
                )
            else:
                logger.error(
                    f"Failed to upload file {file_name} to bucket {bucket_name}."
                )

            return is_upload_succeed
        except ClientError as e:
            logger.error(f"Error with S3 client: {e}")
            return False

    def download_file(
        self,
        file_name: str,
        bucket_name: str,
        key: str = "",
    ):
        """
        Download a specified file to the specified S3 bucket.

        Args:
            file_name (str): File name, and/or destination path to store the file locally.
            key (str): Name of the file on the bucket.
            bucket_name (str): Name of the S3 bucket.

        Returns:
            Content of the file if the file was successfully uploaded, None if it was not.
        """

        try:
            self.s3_client.download_file(
                Bucket=bucket_name, Key=key, Filename=file_name
            )

            if os.path.isfile(file_name):
                logger.success(
                    f"Successfully downloaded file {key} to path {file_name}!"
                )
            else:
                logger.error(f"File {key} is not found at path {file_name}!")
        except ClientError as e:
            logger.error(f"Error with S3 client: {e}")
            return False
