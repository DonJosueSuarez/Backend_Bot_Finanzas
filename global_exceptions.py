from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

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
        # Aquí puedes agregar logs reales para el desarrollador
        return JSONResponse(
            status_code=500,
            content={
                "status": "critical",
                "message": "Error interno del servidor",
                "details": str(exc) # Quitar esto en producción por seguridad
            }
        )