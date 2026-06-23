import uuid

import boto3
from botocore.config import Config

from brews import config

_EXPIRES_IN = 900
_S3_CONFIG = Config(signature_version="s3v4", s3={"addressing_style": "virtual"})


def _client():
    return boto3.client("s3", config=_S3_CONFIG)


def create_upload_url(content_type: str) -> tuple[str, str]:
    """Return a presigned `PUT` URL and the object key for a new upload."""
    key = f"uploads/{uuid.uuid4()}"
    url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": config.get_bucket_name(),
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=_EXPIRES_IN,
    )
    return url, key


def get_image(key: str) -> bytes:
    """Read and return the bytes of an uploaded image from S3."""
    response = _client().get_object(Bucket=config.get_bucket_name(), Key=key)
    return response["Body"].read()
