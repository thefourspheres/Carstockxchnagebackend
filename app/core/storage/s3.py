from app.core.storage.base import StorageProvider
import boto3
from uuid import uuid4
from app.core.config import settings

s3 = boto3.client(
    "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
)

class S3Storage(StorageProvider):

    async def upload(self, file, path: str) -> str:
        filename = f"{uuid4()}.webp"
        s3_key = f"{path}/{filename}"

        s3.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": "image/webp",
                "ACL": "public-read"
            }
        )

        return f"{settings.AWS_S3_BASE_URL}/{s3_key}"
