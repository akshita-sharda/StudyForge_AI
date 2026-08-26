from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./studyforge.db"
    secret_key: str = "development-secret-change-me"
    frontend_url: str = "http://localhost:3000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    mock_ai: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
