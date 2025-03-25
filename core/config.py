"""Define configuration settings using Pydantic and manage environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class defining configuration settings using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    DIFY_API_KEY: str

    DIFY_WORKFLOW_URL: str = "https://api.dify.ai/v1/workflows/run"

    ENOM_RESELLER_ID: str
    ENOM_RESELLER_PASSWORD: str
    ENOM_TEST_MODE: bool = True


settings = Settings()
