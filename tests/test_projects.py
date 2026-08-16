from app.services import project_service
import app.models as models

def test_create_project_grants_owner_access(db_session, test_user):
    project_name = "Test Project"
    project_description = "This is a test project."
    new_project = project_service.create_project(
        db=db_session,
        name=project_name,
        description=project_description,
        owner_id=test_user.id
    )

    assert new_project.name == project_name
    assert new_project.description == project_description
    assert new_project.owner_id == test_user.id

    #Check that the owner has access to the project
    access = db_session.query(models.ProjectAccess).filter_by(
        user_id=test_user.id, project_id=new_project.id).first()
    assert access is not None
    assert access.is_owner is True


def test_list_projects_returns_only_user_projects(db_session, test_user, test_user2):
    #Create projects for both users
    project1 = project_service.create_project(
        db=db_session,
        name="User 1 Project",
        description="Project for user 1",
        owner_id=test_user.id
    )
    project2 = project_service.create_project(
        db=db_session,
        name="User 2 Project",
        description="Project for user 2",
        owner_id=test_user2.id
    )

    #List projects for test_user
    user_projects = project_service.list_projects(db=db_session, user_id=test_user.id)

    #Check that only the project for test_user is returned
    assert len(user_projects) == 1
    assert user_projects[0].id == project1.id

def test_get_project_by_id_returns_correct_project(db_session, test_user):
    #Create a project for the test user
    project = project_service.create_project(
        db=db_session,
        name="Test Project",
        description="This is a test project.",
        owner_id=test_user.id
    )

    #Retrieve the project by its ID
    retrieved_project = project_service.get_project_by_id(db=db_session, project_id=project.id)

    #Check that the retrieved project matches the created project
    assert retrieved_project is not None
    assert retrieved_project.id == project.id
    assert retrieved_project.name == project.name
    assert retrieved_project.description == project.description
    assert retrieved_project.owner_id == test_user.id


def test_update_project_updates_fields(db_session, test_user):
    #Create a project for the test user
    project = project_service.create_project(
        db=db_session,
        name="Old Project Name",
        description="Old description.",
        owner_id=test_user.id
    )

    #Update the project's name and description
    updated_name = "Updated Project Name"
    updated_description = "Updated description."
    updated_project = project_service.update_project(
        db=db_session,
        project=project,
        name=updated_name,
        description=updated_description
    )

    #Check that the project's fields were updated
    assert updated_project.name == updated_name
    assert updated_project.description == updated_description


def test_delete_project_removes_project(db_session, test_user):
    #Create a project for the test user
    project = project_service.create_project(
        db=db_session,
        name="Project to Delete",
        description="This project will be deleted.",
        owner_id=test_user.id
    )

    #Delete the project
    project_service.delete_project(db=db_session, project=project)

    #Check that the project no longer exists in the database
    deleted_project = project_service.get_project_by_id(db=db_session, project_id=project.id)
    assert deleted_project is None

def test_shared_project_with_email_grants_access(db_session, test_user, test_user2):
    #Create a project for the test user
    project = project_service.create_project(
        db=db_session,
        name="Project to Share",
        description="This project will be shared.",
        owner_id=test_user.id
    )

    #Share the project with test_user2
    project_service.shared_project_with_email(
        db=db_session,
        project_id=project.id,
        user_id=test_user2.id,
        requesting_user_id=test_user.id
    )

    #Check that test_user2 has access to the shared project
    access = db_session.query(models.ProjectAccess).filter_by(
        user_id=test_user2.id, project_id=project.id).first()
    assert access is not None
    assert access.is_owner is False  