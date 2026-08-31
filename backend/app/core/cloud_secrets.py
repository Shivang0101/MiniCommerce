import logging
import os

logger = logging.getLogger(__name__)


def get_secret(secret_name: str, region_name: str = "us-east-1") -> str | None:
    """
    Fetches a secret string from AWS Secrets Manager using boto3.
    Returns None if boto3 fails, credentials are missing, or running locally.
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env not in ("staging", "prod", "production"):
        return None

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return response["SecretString"]
    except (ImportError, BotoCoreError, ClientError, Exception) as e:
        logger.warning(f"Unable to fetch AWS secret '{secret_name}': {e}. Falling back to local env.")

    return None
