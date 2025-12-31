from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # API Configuration
    API_KEY: str
    OPENAI_API_KEY: str
    
    # Database Configuration
    DATABASE_URL: str
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = 'vector-db'
    EMBEDDING_MODEL: str = Field(default='text-embedding-3-small')
    
    # LLM Configuration
    LLM_MODEL: str = Field(default='gpt-3.5-turbo')
    LLM_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    LLM_MAX_TOKENS: int = Field(default=500, gt=0)
    
    # Document Processing Configuration
    CHUNK_SIZE: int = Field(default=1000, gt=0)
    CHUNK_OVERLAP: int = Field(default=200, ge=0)
    MAX_FILE_SIZE_MB: int = Field(default=10, gt=0)
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=['*'])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: List[str] = Field(default=['*'])
    CORS_ALLOW_HEADERS: List[str] = Field(default=['*'])
    
    # Application Configuration
    APP_NAME: str = Field(default='RAG API')
    APP_VERSION: str = Field(default='1.0.0')
    DEBUG: bool = Field(default=False)
    
    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, gt=0)
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('CHUNK_OVERLAP')
    @classmethod
    def validate_chunk_overlap(cls, v, info):
        chunk_size = info.data.get('CHUNK_SIZE', 1000)
        if v >= chunk_size:
            raise ValueError('CHUNK_OVERLAP must be less than CHUNK_SIZE')
        return v


settings = Settings()
