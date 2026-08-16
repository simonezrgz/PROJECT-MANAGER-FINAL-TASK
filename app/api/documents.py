import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session


from app.database import get_db
from app.security import check_project_access, check_document_access, check_document_owner
import app.schemas as schemas
from app.services import document_service, storage_service

router = APIRouter(tags=["Documents"])


#-----------Create Document----------------#
@router.post("/project/{project_id}/documents", response_model=schemas.DocumentBase, status_code=status.HTTP_201_CREATED)
def create_document(
    project_id: int,
    file: UploadFile = File(...),
    access = Depends(check_project_access),
    db: Session = Depends(get_db)
):
    file_path = document_service.save_upload_file(file)
    try:
        return document_service.create_document(
            db=db,
            project_id=project_id,
            file_path=file_path
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#-----------Update Document----------------#
@router.put("/document/{document_id}", response_model=schemas.DocumentBase)
def update_document(
    document_id: int,
    new_file: UploadFile = File(...),
    access = Depends(check_document_owner),
    db: Session = Depends(get_db)
):
    new_file_path = document_service.save_upload_file(new_file)
    try:
        return document_service.update_document(
            db=db,
            document=access.document,
            new_file_path=new_file_path
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


#-----------Get Document List----------------#
@router.get("/project/{project_id}/documents", response_model=list[schemas.DocumentBase])
def list_documents(
    project_id: int,
    access = Depends(check_project_access),
    db: Session = Depends(get_db)
):
    return document_service.list_documents(db=db, project_id=project_id)


#-----------Download Document----------------#
@router.get("/document/{document_id}")
def download_document(
    document_id: int,
    access = Depends(check_document_access),
):
    url = storage_service.get_download_url(access.document.file_path)
    print(f"DEBUG: presigned URL = {url}")   


#-----------Delete Document----------------#
@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    access = Depends(check_document_owner),
    db: Session = Depends(get_db)
):
    document_service.delete_document(db=db, document=access.document)
    return None