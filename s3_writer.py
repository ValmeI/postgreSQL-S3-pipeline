import json
import boto3
from config import settings
from datetime import datetime, timezone
from app_logging import logger


def generate_s3_object_partition():
    now = datetime.now(timezone.utc)
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    return f"{year}/{month}/{day}"


def write_to_s3(features: dict, bucket_name: str, bucket_folder_name: str, object_key: str):
    try:
        data = json.dumps(features, indent=2)
        s3 = boto3.client(
            "s3", aws_access_key_id=settings.S3_ACCESS_KEY, aws_secret_access_key=settings.S3_ACCESS_SECRET
        )
        partition = generate_s3_object_partition()
        s3_key = f"{bucket_folder_name}/{partition}/{object_key}.json"
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=data)
        logger.info(f"Successfully wrote features to s3://{bucket_name}/{object_key}")
    except Exception as e:
        logger.error(f"Failed to write to S3: {e}")
