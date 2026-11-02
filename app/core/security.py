import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qsl

from fastapi import Depends, Header, Query, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import Config
from app.core.exceptions import AppException, ForbiddenException, UnauthorizedException
from app.database.postgresql_connection import get_db
from app.repository.sqlalchemy_user_repository import PostgresUserRepository

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Un initData más viejo que esto se rechaza (la Mini App lo renueva al abrirse)
INIT_DATA_MAX_EDAD = 24 * 60 * 60


@dataclass
class Caller:
    """Quién hace la petición: n8n con la API key, o un usuario desde la Mini App."""
    es_servicio: bool
    user_id: Optional[int] = None


def validar_init_data(init_data: str, bot_token: str) -> str:
    """Comprueba la firma del initData de Telegram y devuelve el id del usuario.

    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    datos = dict(parse_qsl(init_data, keep_blank_values=True))
    hash_recibido = datos.pop("hash", None)
    if not hash_recibido:
        raise UnauthorizedException("initData sin firma")

    data_check = "\n".join(f"{k}={v}" for k, v in sorted(datos.items()))
    clave = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    esperado = hmac.new(clave, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, hash_recibido):
        raise UnauthorizedException("initData con firma inválida")

    if time.time() - int(datos.get("auth_date", 0)) > INIT_DATA_MAX_EDAD:
        raise UnauthorizedException("La sesión expiró; vuelve a abrir el dashboard desde Telegram")

    try:
        return str(json.loads(datos["user"])["id"])
    except (KeyError, ValueError, TypeError):
        raise UnauthorizedException("initData sin usuario")


def authenticate(
    api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Caller:
    """Se aplica a todos los endpoints. Acepta X-API-Key (n8n) o `Authorization: tma <initData>` (Mini App)."""
    if api_key:
        if not Config.API_KEY:
            raise AppException("API_KEY no está configurada en el servidor", status_code=500)
        if not secrets.compare_digest(api_key.encode(), Config.API_KEY.encode()):
            raise UnauthorizedException("API key inválida o ausente")
        return Caller(es_servicio=True)

    if authorization and authorization.startswith("tma "):
        if not Config.TELEGRAM_BOT_TOKEN:
            raise AppException("TELEGRAM_BOT_TOKEN no está configurado en el servidor", status_code=500)
        telegram_id = validar_init_data(authorization[4:], Config.TELEGRAM_BOT_TOKEN)
        user = PostgresUserRepository(db).get_by_telegram_id(telegram_id)
        if not user:
            raise UnauthorizedException("Primero regístrate escribiéndole al bot")
        return Caller(es_servicio=False, user_id=user.id)

    raise UnauthorizedException("API key inválida o ausente")


def require_service(caller: Caller = Depends(authenticate)) -> None:
    """Endpoints que solo usa n8n: registrar usuarios y transacciones."""
    if not caller.es_servicio:
        raise ForbiddenException()


def current_user_id(
    user_id: Optional[int] = Query(default=None),
    caller: Caller = Depends(authenticate),
) -> int:
    """n8n indica el usuario con ?user_id; la Mini App solo puede ver al usuario de su initData."""
    if caller.es_servicio:
        if user_id is None:
            raise AppException("Falta el parámetro user_id", status_code=422)
        return user_id
    if user_id is not None and user_id != caller.user_id:
        raise ForbiddenException("Solo puedes ver tus propios movimientos")
    return caller.user_id
