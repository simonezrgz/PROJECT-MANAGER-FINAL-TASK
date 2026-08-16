import app.models as models
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture()
def test_user(db_session):
    user = models.Users(
        name="Test User",
        email="test@test.com",
        hashed_password="hashedpassword"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def test_user2(db_session):
    user = models.Users(
        name="Test User 2",
        email="test2@test2.com",
        hashed_password="hashedpassword2"
    ) 
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def test_project(db_session, test_user):
    project = models.Projects(
        name="Test Project",
        description="This is a test project.",
        owner_id=test_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Grant access to the owner
    access = models.ProjectAccess(
        user_id=test_user.id,
        project_id=project.id,
        is_owner=True
    )
    db_session.add(access)
    db_session.commit()

    return project

 #-----------Auth Login/Register Fixtures----------------#
@pytest.fixture()
def test_user_data():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "repeat_password": "testpassword"
    }
