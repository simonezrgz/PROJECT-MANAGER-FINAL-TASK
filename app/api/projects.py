from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.security as security
from app.api.deps import get_current_user
from app.database import get_db
from app.services import project_service

#----------------------------------------------------------------------------#


router = APIRouter(prefix="/projects", tags=["Projects"])

#----------Create Project---------#
@router.post("", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)):

    return project_service.create_project(
        db=db,
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )

#----------Read Project---------#
"""Get a list of all the projects accesible to the current user"""
@router.get("", response_model=list[schemas.ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    return project_service.list_projects(db=db, user_id=current_user.id)


"""Get single requested project"""
@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    access = Depends(security.check_project_access),
):
    return access.project


#----------Update Project---------#
@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project_data: schemas.ProjectUpdate,
    access = Depends(security.check_project_access),
    db: Session = Depends(get_db)
):
    return project_service.update_project(
        db=db,
        project=access.project,
        name=project_data.name,
        description=project_data.description
    )


#-----------Delete Project----------------#
@router.delete("/{project_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    access = Depends(security.check_project_owner),
    db: Session = Depends(get_db)
):
    project_service.delete_project(db=db, project=access.project)
    return None

#-----------------------Share Project---------------------#
@router.post("/{project_id}/invite",
             response_model=schemas.MessageResponse,
            status_code=status.HTTP_201_CREATED)
def invite_user(
    project_id:int,
    email: str,
    access = Depends(security.check_project_owner),
    db: Session = Depends(get_db)
):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    project_service.shared_project_with_email(db=db, project_id=project_id, user_id=user.id)

    return {"message": f"Project shared with {email} successfully."}