import os
from typing import Any

import boto3
from pydantic import SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class SsmSettingsSource(PydanticBaseSettingsSource):
    """Resolves secret fields from SSM parameters named by `*_PARAM` env vars."""

    _param_envs = {
        "upload_token": "UPLOAD_TOKEN_PARAM",
        "anthropic_api_key": "ANTHROPIC_API_KEY_PARAM",
    }

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        client = None
        values: dict[str, Any] = {}
        for field_name, param_env in self._param_envs.items():
            name = os.environ.get(param_env)
            if not name:
                continue
            client = client or boto3.client("ssm")
            parameter = client.get_parameter(Name=name, WithDecryption=True)
            values[field_name] = parameter["Parameter"]["Value"]
        return values


class Settings(BaseSettings):
    image_bucket_name: str = "brews-images"
    table_name: str = "brews"
    upload_token: SecretStr
    anthropic_api_key: SecretStr
    s3_public_endpoint: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="BREWS_", env_file=".env", extra="allow"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            SsmSettingsSource(settings_cls),
            file_secret_settings,
        )
