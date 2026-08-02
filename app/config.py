from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	database_url: str
	ollama_base_url: str
	ollama_model: str
	ollama_num_thread: int = 2
	ollama_num_ctx: int = 2048
	api_secret: str | None = None
	api_debug: bool = False


settings = Settings()
