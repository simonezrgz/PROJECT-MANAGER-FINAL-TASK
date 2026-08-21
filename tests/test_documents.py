import os
from unittest.mock import patch

import app.models as models
from app.services import document_service, storage_service


def test_create_document(db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    assert new_document.project_id == test_project.id
    assert new_document.file_path == file_path

def test_create_document_invalid_project(db_session):
    file_path = "test_file.pdf"
    invalid_project_id = 9999  #Assuming this project ID does not exist

    try:
        document_service.create_document(
            db=db_session,
            project_id=invalid_project_id,
            file_path=file_path
        )
        assert False, "Expected an exception for invalid project ID"
    except Exception as e:
        assert str(e) == "Project not found"


def test_create_document_invalid_extension(db_session, test_project):
    invalid_file_path = "invalid_file.txt"  #Invalid extension

    try:
        document_service.create_document(
            db=db_session,
            project_id=test_project.id,
            file_path=invalid_file_path
        )
        assert False, "Expected an exception for invalid file extension"
    except Exception as e:
        assert str(e) == "Invalid file type. Allowed types: .docx, .pdf"

def test_list_documents(db_session, test_project):
    file_path1 = "test_file1.pdf"
    file_path2 = "test_file2.docx"

    document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path1
    )

    document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path2
    )

    documents = document_service.list_documents(db=db_session, project_id=test_project.id)

    assert len(documents) == 2
    assert documents[0].file_path == file_path1
    assert documents[1].file_path == file_path2


def test_delete_document(db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    #Delete the document
    document_service.delete_document(db=db_session, document=new_document)
    
    #Check that the document is deleted from the database
    deleted_document = (
        db_session.query(models.Documents)
        .filter(models.Documents.id == new_document.id)
        .first()
    )
    assert deleted_document is None

def test_delete_document_file_not_found(db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    if os.path.exists(new_document.file_path):
        os.remove(new_document.file_path)

    #Delete
    document_service.delete_document(db=db_session, document=new_document)

    #Check that the document is deleted from the database
    deleted_document = (
        db_session.query(models.Documents)
        .filter(models.Documents.id == new_document.id)
        .first()
    )
    assert deleted_document is None


def test_update_document(db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    new_file_path = "updated_file.docx"
    updated_document = document_service.update_document(
        db=db_session,
        document=new_document,
        new_file_path=new_file_path
    )

    assert updated_document.file_path == new_file_path

def test_update_document_invalid_extension(db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    invalid_new_file_path = "invalid_file.txt"  # Invalid extension

    try:
        document_service.update_document(
            db=db_session,
            document=new_document,
            new_file_path=invalid_new_file_path
        )
        assert False, "Expected an exception for invalid file extension"
    except Exception as e:
        assert str(e) == "Invalid file type. Allowed types: .docx, .pdf"


@patch.object(storage_service.s3_client, "delete_object")
def test_update_document_removes_old_document(mock_delete, db_session, test_project):
    file_path = "test_file.pdf"
    new_document = document_service.create_document(
        db=db_session,
        project_id=test_project.id,
        file_path=file_path
    )

    new_file_path = "updated_file.docx"
    document_service.update_document(
        db=db_session,
        document=new_document,
        new_file_path=new_file_path
    )

    mock_delete.assert_called_once_with(Bucket=storage_service.BUCKET_NAME, Key=file_path)