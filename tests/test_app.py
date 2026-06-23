import base64

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from brews import app as app_module
from brews import config, extract
from brews.models import Beer


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("BREWS_TABLE_NAME", "brews-test")
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
        with TestClient(app_module.app) as test_client:
            yield test_client


def _image_file(content=b"rawbytes"):
    return {"file": ("list.jpg", content, "image/jpeg")}


def test_get_beers_starts_empty(client):
    response = client.get("/api/beers")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_without_token_is_rejected(client):
    response = client.post("/api/beers/upload", files=_image_file())
    assert response.status_code == 401


def test_upload_with_wrong_token_is_rejected(client):
    response = client.post(
        "/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "nope"}
    )
    assert response.status_code == 401


def test_non_image_upload_is_rejected(client, monkeypatch):
    monkeypatch.setattr(
        extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="x")]
    )
    response = client.post(
        "/api/beers/upload",
        files={"file": ("notes.txt", b"hi", "text/plain")},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 400


def test_successful_upload_replaces_list(client, monkeypatch):
    monkeypatch.setattr(
        extract,
        "extract_beers",
        lambda image_bytes, media_type: [Beer(name="Pils"), Beer(name="Stout")],
    )
    response = client.post(
        "/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"}
    )
    assert response.status_code == 200
    assert [beer["name"] for beer in response.json()] == ["Pils", "Stout"]
    assert [beer["name"] for beer in client.get("/api/beers").json()] == ["Pils", "Stout"]


def test_empty_extraction_leaves_list_untouched(client, monkeypatch):
    monkeypatch.setattr(
        extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="Keep")]
    )
    client.post("/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"})

    monkeypatch.setattr(extract, "extract_beers", lambda image_bytes, media_type: [])
    response = client.post(
        "/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"}
    )
    assert response.status_code == 422
    assert [beer["name"] for beer in client.get("/api/beers").json()] == ["Keep"]


def test_cors_allow_origin_header_present(client):
    response = client.get("/api/beers", headers={"Origin": "https://brews.gadom.ski"})
    assert response.headers["access-control-allow-origin"] == "https://brews.gadom.ski"


class _Context:
    aws_request_id = "test"
    function_name = "test"
    memory_limit_in_mb = 512
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"

    def get_remaining_time_in_millis(self):
        return 30000


def _apigw_upload_event(body_bytes, content_type, token):
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/api/beers/upload",
        "rawQueryString": "",
        "headers": {"content-type": content_type, "x-upload-token": token},
        "requestContext": {
            "http": {"method": "POST", "path": "/api/beers/upload", "sourceIp": "127.0.0.1"}
        },
        "body": base64.b64encode(body_bytes).decode(),
        "isBase64Encoded": True,
    }


def test_handler_decodes_base64_multipart_upload(client, monkeypatch):
    captured = {}

    def fake_extract(image_bytes, media_type):
        captured["image_bytes"] = image_bytes
        return [Beer(name="Pils")]

    monkeypatch.setattr(extract, "extract_beers", fake_extract)

    image = b"\xff\xd8imagebytes"
    boundary = "BOUNDARY"
    multipart = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="list.jpg"\r\n'
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + image + f"\r\n--{boundary}--\r\n".encode()

    event = _apigw_upload_event(
        multipart, f"multipart/form-data; boundary={boundary}", "secret"
    )
    response = app_module.handler(event, _Context())

    assert response["statusCode"] == 200
    assert captured["image_bytes"] == image
