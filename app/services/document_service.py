import os
import shutil
import uuid
from fastapi import UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.services import project_service, storage_service

ALLOWED_EXTENSIONS = [".pdf", ".docx"]
UPLOAD_DIR = settings.UPLOAD_DIR


#-----------Create Document----------------#
def create_document(db: Session, project_id: int, file_path: str) -> models.Documents:
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise ValueError("Project not found")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    new_document = models.Documents(
        project_id=project_id,
        file_path=file_path,
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document



#-----------Update Document----------------#
def update_document(db: Session, document: models.Documents, new_file_path: str) -> models.Documents:
    ext = os.path.splitext(new_file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    old_file_path = document.file_path

    document.file_path = new_file_path
    db.commit()
    db.refresh(document)

    if old_file_path and os.path.exists(old_file_path):
        os.remove(old_file_path)

    return document

#-----------Get Document List----------------#
def list_documents(db: Session, project_id: int) -> list[models.Documents]:
    return db.query(models.Documents).filter(models.Documents.project_id == project_id).all()


#-----------Delete Document----------------#
def delete_document(db: Session, document: models.Documents) -> None:
    storage_service.delete_file(document.file_path)
    db.delete(document)
    db.commit()