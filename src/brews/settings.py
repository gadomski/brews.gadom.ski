from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    image_bucket_name: str = "brews-images"
    table_name: str = "brews"
    upload_token: SecretStr
    anthropic_api_key: SecretStr

    model_config = SettingsConfigDict(
        env_prefix="BREWS_", env_file=".env", extra="allow"
    )
