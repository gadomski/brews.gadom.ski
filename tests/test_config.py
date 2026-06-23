import boto3
import pytest
from moto import mock_aws

from brews import config


@pytest.fixture(autouse=True)
def clear_cache():
    config._ssm_value.cache_clear()
    yield
    config._ssm_value.cache_clear()


def test_upload_token_from_env(monkeypatch):
    monkeypatch.delenv("UPLOAD_TOKEN_PARAM", raising=False)
    monkeypatch.setenv("BREWS_UPLOAD_TOKEN", "envtoken")
    assert config.get_upload_token() == "envtoken"


def test_upload_token_missing_returns_none(monkeypatch):
    monkeypatch.delenv("UPLOAD_TOKEN_PARAM", raising=False)
    monkeypatch.delenv("BREWS_UPLOAD_TOKEN", raising=False)
    assert config.get_upload_token() is None


@mock_aws
def test_anthropic_key_from_ssm(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(
        Name="/brews/anthropic-api-key", Value="sk-secret", Type="SecureString"
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY_PARAM", "/brews/anthropic-api-key")
    assert config.get_anthropic_api_key() == "sk-secret"
