import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from brews import storage


@pytest.fixture
def bucket(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("BREWS_BUCKET_NAME", "brews-images")
    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(
            Bucket="brews-images"
        )
        yield


def test_create_upload_url_returns_uploads_key_and_url(bucket):
    url, key = storage.create_upload_url("image/jpeg")
    assert key.startswith("uploads/")
    assert "brews-images" in url


def test_get_image_round_trips_bytes(bucket):
    boto3.client("s3", region_name="us-east-1").put_object(
        Bucket="brews-images", Key="uploads/photo", Body=b"rawbytes"
    )
    assert storage.get_image("uploads/photo") == b"rawbytes"


def test_get_image_raises_for_missing_object(bucket):
    with pytest.raises(ClientError):
        storage.get_image("uploads/missing")
