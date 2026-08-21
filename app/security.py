from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import get_current_user
import app.models as models
from app.database import get_db
from app.utils import decode_access_token
#----------------------------------------------------------------------------#


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    #decode Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    #extract user id
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    #fetch user from db 
    user = db.query(models.Users).filter(models.Users.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user




def get_project_access(project_id: int, db: Session, user: models.Users) -> models.ProjectAccess:
    print(f"DEBUG: looking for project_id={project_id} (type={type(project_id)}), user_id={user.id} (type={type(user.id)})")
    
    access = db.query(models.ProjectAccess).filter_by(
        project_id=project_id, user_id=user.id
    ).first()
    
    print(f"DEBUG: query result = {access}")
    
    all_rows = db.query(models.ProjectAccess).all()
    print(f"DEBUG: all project_access rows = {[(r.project_id, r.user_id, r.is_owner) for r in all_rows]}")

    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project."
        )
    return access


def check_project_access(
    project_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)) -> models.ProjectAccess:
    """Dependency: any access (owner or participant) is enough."""
    return get_project_access(project_id, db, user)


def check_project_owner(
    project_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)) -> models.ProjectAccess:
    """Dependency: only owners pass. Use for DELETE endpoints etc."""
    access = get_project_access(project_id, db, user)
    if not access.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action."
        )
    return access


#-----------------------Document access---------------------#

def get_document_access(document_id: int, db: Session, user: models.Users) -> models.ProjectAccess:
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
    user: models.Users = Depends(get_current_user)) -> models.ProjectAccess:
    """Owner only — use for DELETE on a document, per your spec."""
    access = get_document_access(document_id, db, user)
    if not access.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete this document."
        )
    return access