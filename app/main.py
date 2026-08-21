from fastapi import FastAPI

import app.models
from app.api.auth import router as auth_router
from app.api.documents import router as document_router
from app.api.projects import router as project_router
from app.database import Base, engine

#######################################################

app = FastAPI(title="Project Management")

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(document_router)

@app.get("/")
def read_root():
    return {"message": "API is up and running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)