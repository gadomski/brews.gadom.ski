import functools
import os

import boto3


@functools.cache
def _ssm_value(param_name: str) -> str:
    client = boto3.client("ssm")
    response = client.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def _resolve(param_env: str, value_env: str) -> str | None:
    param_name = os.environ.get(param_env)
    if param_name:
        return _ssm_value(param_name)
    return os.environ.get(value_env)


def get_anthropic_api_key() -> str | None:
    """Return the Anthropic API key from SSM if configured, else from the environment."""
    return _resolve("ANTHROPIC_API_KEY_PARAM", "ANTHROPIC_API_KEY")


def get_upload_token() -> str | None:
    """Return the upload token from SSM if configured, else from the environment."""
    return _resolve("UPLOAD_TOKEN_PARAM", "BREWS_UPLOAD_TOKEN")


def get_bucket_name() -> str:
    """Return the S3 bucket name for uploaded images from the environment."""
    return os.environ["BREWS_BUCKET_NAME"]
