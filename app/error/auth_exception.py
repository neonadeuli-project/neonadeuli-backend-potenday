class AuthServiceException(Exception):
    """Auth 서비스 기본 예외 클래스"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(AuthServiceException):
    """사용자를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, identifier: str):
        super().__init__(f"식별자 '{identifier}'에 해당하는 사용자를 찾을 수 없습니다.")


class InvalidTokenException(AuthServiceException):
    """토큰이 유효하지 않을 때 발생하는 예외"""

    def __init__(self, token: str = ""):
        message = "유효하지 않은 토큰입니다."
        if token:
            message += f" 토큰: {token}"
        super().__init__(message)


class UserCreationException(AuthServiceException):
    """사용자 생성 중 오류가 발생했을 때 발생하는 예외"""

    def __init__(self, reason: str):
        super().__init__(f"사용자 생성 중 오류가 발생했습니다: {reason}")


class DatabaseOperationException(AuthServiceException):
    """데이터베이스 작업 중 오류가 발생했을 때 발생하는 예외"""

    def __init__(self, operation: str):
        super().__init__(f"데이터베이스 작업 중 오류 발생: {operation}")
