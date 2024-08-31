class ImageException(Exception):
    """기본 이미지 관련 예외 클래스"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ImageUploadException(ImageException):
    """이미지 업로드 중 발생하는 예외"""

    def __init__(self, filename: str, error: str):
        super().__init__(f"이미지 '{filename}' 업로드 중 오류 발생: {error}")


class ImageNotFoundException(ImageException):
    """이미지 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, image_id: int):
        super().__init__(f"이미지 ID {image_id}를 찾을 수 없습니다.")


class ImageDeleteException(ImageException):
    """이미지 삭제 중 발생하는 예외"""

    def __init__(self, image_id: int, error: str):
        super().__init__(f"이미지 ID {image_id} 삭제 중 오류 발생: {error}")


class InvalidImageFormatException(ImageException):
    """유효하지 않은 이미지 형식일 때 발생하는 예외"""

    def __init__(self, filename: str, allowed_formats: list):
        super().__init__(
            f"파일 '{filename}'의 형식이 유효하지 않습니다. 허용된 형식: {', '.join(allowed_formats)}"
        )


class NoImagesFoundException(ImageException):
    """건물에 대한 이미지를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, building_id: int):
        super().__init__(
            f"건축물 ID {building_id}에 대한 이미지를 찾을 수 없습니다."
        )


class S3UploadException(Exception):
    def __init__(self, filename: str, error: str):
        self.filename = filename
        self.error = error
        super().__init__(
            f"파일명 : {filename} 인 파일을 S3에 업로드를 하지 못했습니다.: {error}"
        )
