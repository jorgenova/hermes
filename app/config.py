from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	database_url: str
	ollama_base_url: str
	ollama_model: str
	api_secret: str | None = None
	api_debug: bool = False


settings = Settings()
