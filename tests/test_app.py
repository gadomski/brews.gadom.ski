import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from brews import app as app_module
from brews import config, extract, images
from brews.models import Beer


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("BREWS_TABLE_NAME", "brews-test")
    monkeypatch.setenv("BREWS_BUCKET_NAME", "brews-images")
    monkeypatch.delenv("UPLOAD_TOKEN_PARAM", raising=False)
    monkeypatch.setenv("BREWS_UPLOAD_TOKEN", "secret")
    config._ssm_value.cache_clear()
    with mock_aws():
        boto3.client("dynamodb", region_name="us-east-1").create_table(
            TableName="brews-test",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        boto3.client("s3", region_name="us-east-1").create_bucket(
            Bucket="brews-images"
        )
        with TestClient(app_module.app) as test_client:
            yield test_client


def _put_image(key="uploads/photo", body=b"rawbytes"):
    boto3.client("s3", region_name="us-east-1").put_object(
        Bucket="brews-images", Key=key, Body=body
    )
    return key


def _no_downscale(monkeypatch):
    monkeypatch.setattr(images, "downscale", lambda data: (data, "image/jpeg"))


def test_get_beers_starts_empty(client):
    response = client.get("/api/beers")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_url_without_token_is_rejected(client):
    response = client.post(
        "/api/beers/upload-url", json={"content_type": "image/jpeg"}
    )
    assert response.status_code == 401


def test_upload_url_with_wrong_token_is_rejected(client):
    response = client.post(
        "/api/beers/upload-url",
        json={"content_type": "image/jpeg"},
        headers={"X-Upload-Token": "nope"},
    )
    assert response.status_code == 401


def test_upload_url_rejects_non_image_content_type(client):
    response = client.post(
        "/api/beers/upload-url",
        json={"content_type": "text/plain"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 400


def test_upload_url_returns_url_and_key(client):
    response = client.post(
        "/api/beers/upload-url",
        json={"content_type": "image/jpeg"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["key"].startswith("uploads/")
    assert body["url"].startswith("http")


def test_process_without_token_is_rejected(client):
    response = client.post("/api/beers/process", json={"key": "uploads/photo"})
    assert response.status_code == 401


def test_process_rejects_key_outside_uploads_prefix(client):
    response = client.post(
        "/api/beers/process",
        json={"key": "secrets/photo"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 400


def test_process_missing_object_returns_404(client):
    response = client.post(
        "/api/beers/process",
        json={"key": "uploads/missing"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 404


def test_process_unreadable_image_returns_400(client):
    _put_image(body=b"not an image")
    response = client.post(
        "/api/beers/process",
        json={"key": "uploads/photo"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 400


def test_process_replaces_list(client, monkeypatch):
    _no_downscale(monkeypatch)
    monkeypatch.setattr(
        extract,
        "extract_beers",
        lambda image_bytes, media_type: [Beer(name="Pils"), Beer(name="Stout")],
    )
    key = _put_image()
    response = client.post(
        "/api/beers/process",
        json={"key": key},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 200
    assert [beer["name"] for beer in response.json()] == ["Pils", "Stout"]
    assert [beer["name"] for beer in client.get("/api/beers").json()] == [
        "Pils",
        "Stout",
    ]


def test_process_empty_extraction_leaves_list_untouched(client, monkeypatch):
    _no_downscale(monkeypatch)
    monkeypatch.setattr(
        extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="Keep")]
    )
    _put_image()
    client.post(
        "/api/beers/process",
        json={"key": "uploads/photo"},
        headers={"X-Upload-Token": "secret"},
    )

    monkeypatch.setattr(extract, "extract_beers", lambda image_bytes, media_type: [])
    response = client.post(
        "/api/beers/process",
        json={"key": "uploads/photo"},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 422
    assert [beer["name"] for beer in client.get("/api/beers").json()] == ["Keep"]


def test_cors_allow_origin_header_present(client):
    response = client.get("/api/beers", headers={"Origin": "https://brews.gadom.ski"})
    assert response.headers["access-control-allow-origin"] == "https://brews.gadom.ski"
