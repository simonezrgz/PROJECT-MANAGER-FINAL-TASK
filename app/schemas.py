from typing import List, Optional

from pydantic import BaseModel, EmailStr, model_validator

#-----------------User Schemas-----------------#

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    name: str
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    permissions: str

    class Config:
        from_attributes = True


#---------Document Schemas-------------#
class DocumentBase(BaseModel):
    id: int
    project_id: int
    file_path: str

    class Config:
        from_attributes = True


#------------Project Schemas-------------#
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: str = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    documents: List[DocumentBase] = []

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str