import boto3
import os
import uuid 

from fastapi import UploadFile  
from app.config import settings



ALLOWED_EXTENSIONS = [".pdf", ".docx"]


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

BUCKET_NAME = settings.S3_BUCKET_NAME

def save_upload_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file type. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    unique_filename = f"{uuid.uuid4()}{ext}"

    s3_client.upload_fileobj(file.file, BUCKET_NAME, unique_filename)

    return unique_filename


def get_download_url(key: str, expires_in: int = 300) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in
    )


def delete_file(key: str) -> None:
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)