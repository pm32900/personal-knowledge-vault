class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication Failed"):
        super().__init__(message, status_code=401)
class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient Permissions"):
        super().__init__(message, status_code=403)

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ValidationError(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)

class AIServiceError(AppException):
    def __init__(self, message:str = "AI service unavailable"):
        super().__init__(message, status_code=503)