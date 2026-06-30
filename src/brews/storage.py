import functools
import uuid

import boto3
from botocore.config import Config
from types_boto3_s3.client import S3Client

from .models import UploadUrlResponse
from .settings import Settings

_EXPIRES_IN = 900
_S3_CONFIG = Config(signature_version="s3v4", s3={"addressing_style": "virtual"})


@functools.cache
def _client() -> S3Client:
    return boto3.client("s3", config=_S3_CONFIG)


def create_upload_url(content_type: str, settings: Settings) -> UploadUrlResponse:
    key = f"uploads/{uuid.uuid4()}"
    url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.image_bucket_name,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=_EXPIRES_IN,
    )
    return UploadUrlResponse(url=url, key=key)


def get_image(key: str, settings: Settings) -> bytes:
    return (
        _client().get_object(Bucket=settings.image_bucket_name, Key=key)["Body"].read()
    )
