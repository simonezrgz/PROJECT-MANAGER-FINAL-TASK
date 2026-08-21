from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    permissions = Column(String(50), nullable=False, default="user")

    #relationships
    owned_projects = relationship(
        "Projects", back_populates="owner", cascade="all, delete-orphan"
        )
    shared_projects = relationship(
        "ProjectAccess", back_populates="user", cascade="all, delete-orphan"
        )


class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    #relationships
    owner = relationship(
        "Users", back_populates="owned_projects"
        )
    documents = relationship(
        "Documents", back_populates="project", cascade="all, delete-orphan"
        )
    access_list = relationship(
        "ProjectAccess", back_populates="project", cascade="all, delete-orphan"
        )


class Documents(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(255), nullable=False)

    #relationships
    project = relationship("Projects", back_populates="documents")

class ProjectAccess(Base):
    __tablename__ = "project_access"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    is_owner = Column(Boolean, nullable=False, default=False)

    #relationships
    user = relationship("Users", back_populates="shared_projects")
    project = relationship("Projects", back_populates="access_list")