from pydantic import BaseModel
from datetime import datetime


# 임시 로그인 정보 응답 값
class UserTempLoginResponse(BaseModel):
    id: int
    username: str
    access_token: str
    token_type: str


class UserValidationResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


class UserLogoutResponse(BaseModel):
    message: str
    success: bool
