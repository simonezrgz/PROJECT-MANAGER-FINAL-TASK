from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import app.models as models
from app.api.deps import get_current_user
from app.database import get_db

#----------------------------------------------------------------------------#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_project_access(project_id: int, 
                       db: Session, 
                       user: models.Users) -> models.ProjectAccess:    
    access = db.query(models.ProjectAccess).filter_by(
        project_id=project_id, user_id=user.id
    ).first()
        
    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project."
        )
    return access


def check_project_access(
    project_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)
        ) -> models.ProjectAccess:
    """Dependency: any access (owner or participant) is enough."""
    return get_project_access(project_id, db, user)


def check_project_owner(
    project_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)
        ) -> models.ProjectAccess:
    """Dependency: only owners pass. Use for DELETE endpoints etc."""
    access = get_project_access(project_id, db, user)
    if not access.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action."
        )
    return access


#-----------------------Document access---------------------#

def get_document_access(document_id: int, 
                        db: Session, 
                        user: models.Users) -> models.ProjectAccess:
    """Resolve a document to its project, then check access on that project."""
    document = db.query(models.Documents).filter_by(id=document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    access = get_project_access(document.project_id, db, user)
    access.document = document  
    return access


def check_document_access(
    document_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)) -> models.ProjectAccess:
    """Owner or participant — use for GET/PUT on a document."""
    return get_document_access(document_id, db, user)


def check_document_owner(
    document_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)
        ) -> models.ProjectAccess:
    """Owner only — use for DELETE on a document, per your spec."""
    access = get_document_access(document_id, db, user)
    if not access.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete this document."
        )
    return access