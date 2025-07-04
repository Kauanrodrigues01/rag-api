from fastapi import (
    HTTPException,
    status,
    Security
)
from fastapi.security.api_key import APIKeyHeader
from app.settings import settings

API_KEY_NAME = 'X-API-Key'

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return api_key
