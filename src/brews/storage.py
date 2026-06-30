from __future__ import annotations

import functools
import os
import uuid
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config

from .models import UploadUrlResponse
from .settings import Settings

if TYPE_CHECKING:
    from types_boto3_s3.client import S3Client

_EXPIRES_IN = 900


def _config(addressing_style: str) -> Config:
    return Config(signature_version="s3v4", s3={"addressing_style": addressing_style})


@functools.cache
def _client() -> S3Client:
    addressing_style = "path" if os.environ.get("AWS_ENDPOINT_URL_S3") else "virtual"
    return boto3.client("s3", config=_config(addressing_style))


@functools.cache
def _presign_client(public_endpoint: str | None) -> S3Client:
    if public_endpoint is None:
        return _client()
    return boto3.client("s3", endpoint_url=public_endpoint, config=_config("path"))


def create_upload_url(content_type: str, settings: Settings) -> UploadUrlResponse:
    key = f"uploads/{uuid.uuid4()}"
    url = _presign_client(settings.s3_public_endpoint).generate_presigned_url(
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
