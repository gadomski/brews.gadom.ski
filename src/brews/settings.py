from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    image_bucket_name: str = "brews-images"
    table_name: str = "brews"
    upload_token: SecretStr
    anthropic_api_key: SecretStr
    s3_public_endpoint: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="BREWS_", env_file=".env", extra="allow"
    )
