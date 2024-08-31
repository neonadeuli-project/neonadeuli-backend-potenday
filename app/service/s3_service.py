import uuid
import boto3
import logging

from botocore.exceptions import ClientError
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.error.image_exception import S3UploadException

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.NCP_ENDPOINT,
            aws_access_key_id=settings.NCP_ACCESS_KEY,
            aws_secret_access_key=settings.NCP_SECRET_KEY,
        )
        self.bucket_name = settings.BUCKET_NAME
        self.cdn_domain = settings.CDN_DOMAIN

    async def upload_file(self, file: UploadFile, folder: str = ""):
        file_extension = file.filename.split(".")[-1].lower()
        file_name = (
            f"{folder}/{uuid.uuid4()}.{file_extension}"
            if folder
            else f"{uuid.uuid4()}.{file_extension}"
        )

        try:
            contents = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=file_name, Body=contents
            )
            return f"https://{self.cdn_domain}/{file_name}"
        except ClientError as e:
            logging.error(f"S3 업로드 중 오류 발생: {e}")
            raise S3UploadException(file.filename, str(e))
