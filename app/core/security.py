import secrets
from typing import Optional
from fastapi import Security
from fastapi.security import APIKeyHeader
from app.core.config import Config
from app.core.exceptions import AppException, UnauthorizedException

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> None:
    """Exige el header X-API-Key en cada endpoint. n8n lo envía con una credencial Header Auth."""
    if not Config.API_KEY:
        raise AppException("API_KEY no está configurada en el servidor", status_code=500)

    if not api_key or not secrets.compare_digest(api_key.encode(), Config.API_KEY.encode()):
        raise UnauthorizedException("API key inválida o ausente")
