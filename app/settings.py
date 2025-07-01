from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    OPENAI_API_KEY: str
    VECTOR_STORE_PATH: str = 'vector-db'


settings = Settings()
