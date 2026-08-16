from app import models
from sqlalchemy.orm import Session

#----------Create Project---------#
def create_project(db: Session, name: str, description: str | None, owner_id: int) -> models.Projects:
    new_project = models.Projects(
        name=name,
        description=description,
        owner_id=owner_id
        )

    db.add(new_project)
    db.flush()  

    new_access = models.ProjectAccess(
        user_id=owner_id,
        project_id=new_project.id,
        is_owner=True
    )
    db.add(new_access)
    db.commit()
    db.refresh(new_project)

    return new_project

#----------Read Project---------#
def list_projects(db: Session, user_id: int) -> list[models.Projects]:
    return (
        db.query(models.Projects)
        .join(models.ProjectAccess)
        .filter(models.ProjectAccess.user_id == user_id)
        .all()
    )

def get_project_by_id(db: Session, project_id: int) -> models.Projects | None:
    return db.query(models.Projects).filter(models.Projects.id == project_id).first()


#----------Update Project---------#
def update_project(db: Session, project: models.Projects, name: str | None = None, description: str | None = None) -> models.Projects:
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description

    db.commit()
    db.refresh(project)
    return project


#-----------Delete Project----------------#
def delete_project(db: Session, project: models.Projects) -> None:
    db.delete(project)
    db.commit()


#-----------------------Share Project---------------------#
def shared_project_with_email(
        db: Session, 
        project_id: int, 
        user_id: int,
        requesting_user_id: int
        ) -> models.ProjectAccess:
    if user_id == requesting_user_id:
        raise ValueError("You cannot share the project with yourself.")

    existing_access = (
        db.query(models.ProjectAccess)
        .filter(
            models.ProjectAccess.project_id == project_id,
            models.ProjectAccess.user_id == user_id
        )
        .first()
    )

    if existing_access:
        raise ValueError("The user is already a member of this project.")

    new_access = models.ProjectAccess(
        user_id=user_id,
        project_id=project_id,
        is_owner=False
    )
    db.add(new_access)
    db.commit()
    db.refresh(new_access)
    return new_access