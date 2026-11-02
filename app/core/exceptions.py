class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        
class NotFoundException(AppException):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404)
        
class UnauthorizedException(AppException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, status_code=401)

class ForbiddenException(AppException):
    def __init__(self, message: str = "No tienes permiso para esta operación"):
        super().__init__(message, status_code=403)

class FinanceException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)