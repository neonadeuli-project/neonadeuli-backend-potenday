class ChatServiceException(Exception):
    """Chat 서비스 기본 예외 클래스"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SessionNotFoundException(ChatServiceException):
    """채팅 세션을 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, session_id: int):
        super().__init__(
            f"세션 ID {session_id}인 채팅 세션을 찾을 수 없습니다."
        )


class QuizGenerationException(ChatServiceException):
    """퀴즈 생성 중 오류가 발생했을 때 발생하는 예외"""

    def __init__(self, reason: str):
        super().__init__(f"퀴즈 생성 중 오류 발생: {reason}")


class NoQuizAvailableException(ChatServiceException):
    """더 이상 사용 가능한 퀴즈가 없을 때 발생하는 예외"""

    def __init__(self, session_id: int):
        super().__init__(
            f"세션 ID {session_id}에 더 이상 사용 가능한 퀴즈가 없습니다."
        )


class SummaryNotFoundException(ChatServiceException):
    """채팅 요약을 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, session_id: int):
        super().__init__(
            f"세션 ID {session_id}의 채팅 요약을 찾을 수 없습니다."
        )


class QuizParsingException(ChatServiceException):
    """퀴즈 파싱 중 발생하는 예외"""

    def __init__(self, message: str):
        super().__init__(f"퀴즈 파싱 오류: {message}")


class APICallException(ChatServiceException):
    """API 호출 중 발생하는 예외"""

    def __init__(self, api_name: str, status_code: int, error_message: str):
        super().__init__(
            f"API 호출 실패: {api_name}, 상태 코드: {status_code}, 오류 메시지: {error_message}"
        )
        self.api_name = api_name
        self.status_code = status_code
        self.error_message = error_message
