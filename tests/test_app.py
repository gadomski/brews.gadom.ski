import pytest
from fastapi.testclient import TestClient

from brews import app as app_module
from brews import extract
from brews.models import Beer


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("BREWS_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("BREWS_UPLOAD_TOKEN", "secret")
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
    monkeypatch.setattr(extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="x")])
    response = client.post(
        "/api/beers/upload",
        files={"file": ("notes.txt", b"hi", "text/plain")},
        headers={"X-Upload-Token": "secret"},
    )
    assert response.status_code == 400


def test_successful_upload_replaces_list(client, monkeypatch):
    monkeypatch.setattr(
        extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="Pils"), Beer(name="Stout")]
    )
    response = client.post(
        "/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"}
    )
    assert response.status_code == 200
    assert [beer["name"] for beer in response.json()] == ["Pils", "Stout"]
    assert [beer["name"] for beer in client.get("/api/beers").json()] == ["Pils", "Stout"]


def test_empty_extraction_leaves_list_untouched(client, monkeypatch):
    monkeypatch.setattr(extract, "extract_beers", lambda image_bytes, media_type: [Beer(name="Keep")])
    client.post("/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"})

    monkeypatch.setattr(extract, "extract_beers", lambda image_bytes, media_type: [])
    response = client.post(
        "/api/beers/upload", files=_image_file(), headers={"X-Upload-Token": "secret"}
    )
    assert response.status_code == 422
    assert [beer["name"] for beer in client.get("/api/beers").json()] == ["Keep"]
