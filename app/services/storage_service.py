import boto3
import os
import uuid 
import json

from fastapi import UploadFile  
from app.config import settings



ALLOWED_EXTENSIONS = [".pdf", ".docx"]
BUCKET_NAME = settings.S3_BUCKET_NAME


lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

def get_total_project_size(keys: list[str]) -> int:
    response = lambda_client.invoke(
        FunctionName=settings.LAMBDA_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"keys": keys}),
    )
    result = json.loads(response["Payload"].read())
    return result["total_size_bytes"]


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

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

def get_upload_file_size(file: UploadFile) -> int:
    file.file.seek(0,2)
    size = file.file.tell()
    file.file.seek(0)
    return size

def delete_file(key: str) -> None:
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)