from unittest.mock import MagicMock, patch
from app.services import storage_service, document_service

import pytest
import io
import json 


@patch.object(storage_service.s3_client, "upload_fileobj")
def test_save_upload_file(mock_upload):
    fake_file = MagicMock()
    fake_file.filename = "doc.pdf"
    fake_file.file = io.BytesIO(b"fake data")

    result = storage_service.save_upload_file(fake_file)

    assert result.endswith(".pdf")
    mock_upload.assert_called_once()


@patch.object(storage_service.s3_client, "generate_presigned_url")
def test_get_download_url(mock_presign):
    mock_presign.return_value = "https://s3.amazonaws.com/test-bucket/doc.pdf?signature=123"
    
    url = storage_service.get_download_url("doc.pdf")
    
    assert "https://s3.amazonaws.com" in url
    mock_presign.assert_called_once_with(
        "get_object",
        Params={"Bucket": storage_service.BUCKET_NAME, "Key": "doc.pdf"},
        ExpiresIn=300
    )


def test_save_upload_file_invalid_extension():
    fake_file = MagicMock()
    fake_file.filename = "script.exe" 

    with pytest.raises(ValueError) as exc_info:
        storage_service.save_upload_file(fake_file)

    assert "Invalid file type" in str(exc_info.value)

@patch.object(storage_service.s3_client, "delete_object")
def test_delete_file(mock_delete):
    storage_service.delete_file("sample-uuid.pdf")

    mock_delete.assert_called_once_with(
        Bucket=storage_service.BUCKET_NAME, 
        Key="sample-uuid.pdf"
    )

#---------------Lambda Tests------------#
def make_fake_lambda_response(total_size_bytes: int):
    """Builds a fake object matching what lambda_client.invoke() returns."""
    payload_mock = MagicMock()
    payload_mock.read.return_value = json.dumps({"total_size_bytes": total_size_bytes}).encode()
    return {"Payload": payload_mock}


@patch.object(storage_service, "lambda_client")
def test_validate_project_size_limit_blocks_over_limit(mock_lambda_client, db_session, test_project, monkeypatch):
    mock_lambda_client.invoke.return_value = make_fake_lambda_response(90)
    monkeypatch.setattr("app.services.document_service.settings.MAX_PROJECT_SIZE_BYTES", 100)

    with pytest.raises(ValueError) as exc_info:
        document_service.validate_project_size_limit(db_session, test_project.id, incoming_file_size=20)

    assert "exceed" in str(exc_info.value).lower()

@patch.object(storage_service, "lambda_client")
def test_validate_project_size_limit_allows_under_limit(mock_lambda_client, db_session, test_project, monkeypatch):
    mock_lambda_client.invoke.return_value = make_fake_lambda_response(30)
    monkeypatch.setattr("app.services.document_service.settings.MAX_PROJECT_SIZE_BYTES", 100)

    document_service.validate_project_size_limit(db_session, test_project.id, incoming_file_size=20)
