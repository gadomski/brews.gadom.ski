import os
from pathlib import Path
from typing import Iterator

import boto3
import pytest
from botocore.exceptions import EndpointConnectionError
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pytest import MonkeyPatch
from types_boto3_s3.client import S3Client

import brews.app
from brews.settings import Settings


@pytest.fixture(autouse=True)
def aws_environment(monkeypatch: MonkeyPatch) -> None:
    defaults = {
        "AWS_ENDPOINT_URL_DYNAMODB": "http://localhost:8000",
        "AWS_ENDPOINT_URL_S3": "http://localhost:5000",
        "AWS_ACCESS_KEY_ID": "local",
        "AWS_SECRET_ACCESS_KEY": "local",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    for key, value in defaults.items():
        if key not in os.environ:
            monkeypatch.setenv(key, value)


@pytest.fixture
def settings() -> Iterator[Settings]:
    settings = Settings(
        table_name="brews-test",
        upload_token=SecretStr("icanhasbeerz"),
        anthropic_api_key=SecretStr("dummy-value"),
    )
    resource = boto3.resource("dynamodb")
    try:
        table = resource.create_table(
            TableName=settings.table_name,
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    except EndpointConnectionError:
        pytest.skip("local DynamoDB is not running (try `docker compose up -d`)")
    table.wait_until_exists()
    try:
        yield settings
    finally:
        table.delete()


@pytest.fixture
def s3_client(settings: Settings) -> Iterator[S3Client]:
    client = boto3.client("s3")
    try:
        client.create_bucket(Bucket=settings.image_bucket_name)
    except EndpointConnectionError:
        pytest.skip("local S3 is not running (try `docker compose up -d`)")
    try:
        yield client
    finally:
        objects = client.list_objects_v2(Bucket=settings.image_bucket_name)
        for object in objects.get("Contents", []):
            assert "Key" in object
            client.delete_object(Bucket=settings.image_bucket_name, Key=object["Key"])
        client.delete_bucket(Bucket=settings.image_bucket_name)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = brews.app.create(settings)
    with TestClient(app) as app:
        yield app


@pytest.fixture
def image() -> bytes:
    with open(
        Path(__file__).parents[1] / "img" / "PXL_20260621_230338060.MP.jpg", "rb"
    ) as f:
        return f.read()
