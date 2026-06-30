from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from types_boto3_s3.client import S3Client

import brews.extract
from brews.models import Beer, Extraction, UploadUrlResponse
from brews.settings import Settings


def test_get_beers_empty(client: TestClient) -> None:
    response = client.get("/beers")
    assert response.status_code == 200
    assert response.json() == []


def test_post_upload_url_no_token(client: TestClient) -> None:
    response = client.post("/beers/upload-url")
    assert response.status_code == 401


def test_post_process(
    client: TestClient,
    settings: Settings,
    s3_client: S3Client,
    image: bytes,
    monkeypatch: MonkeyPatch,
) -> None:
    extraction = Extraction(beers=[Beer(name="Pliny the Elder")], comments=[])

    class FakeMessages:
        def parse(self, *args: object, **kwargs: object) -> object:
            return type("Response", (), {"parsed_output": extraction})()

    class FakeAnthropic:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.messages = FakeMessages()

    monkeypatch.setattr(brews.extract, "Anthropic", FakeAnthropic)

    response = client.post(
        "/beers/upload-url",
        headers={"Authorization": "Bearer icanhasbeerz"},
        params={"content_type": "image/jpg"},
    )
    assert response.status_code == 200
    response = UploadUrlResponse.model_validate(response.json())
    s3_client.put_object(
        Bucket=settings.image_bucket_name,
        Key=response.key,
        Body=image,
    )
    response = client.post(
        "/beers/process",
        headers={"Authorization": "Bearer icanhasbeerz"},
        params={"key": response.key},
    )
    assert response.status_code == 200
