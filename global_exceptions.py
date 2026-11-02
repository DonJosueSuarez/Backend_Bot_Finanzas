import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from app.core.config import Config

logger = logging.getLogger("bot_finanzas")


def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "type": exc.__name__ if hasattr(exc, '__name__') else exc.__class__.__name__
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # El detalle completo va al log del servidor, nunca al cliente: revelaría SQL, tablas y rutas
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        content = {"status": "critical", "message": "Error interno del servidor"}
        # Solo en desarrollo se incluye el detalle, para depurar sin exponerlo en producción
        if Config.IS_DEV:
            content["details"] = str(exc)
        return JSONResponse(status_code=500, content=content)
