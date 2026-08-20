import os
import boto3

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    keys = event.get("keys", [])
    total_size = 0

    for key in keys:
        try:
            response = s3.head_object(Bucket=BUCKET_NAME, Key=key)
            total_size += response["ContentLength"]
        except s3.exceptions.ClientError:
            continue

    return {"total_size_bytes":total_size}