# Project Management API

A backend API for creating, updating, sharing, and deleting projects and their associated documents. Built with FastAPI, PostgreSQL, and AWS (S3 + Lambda), containerized with Docker, and packaged with Poetry.

## Features

- **Auth** — registration, login, JWT-based sessions (1 hour expiry)
- **Projects** — create, read, update, delete, with owner/participant access control
- **Documents** — upload, download, update, delete PDF/DOCX files, stored in AWS S3
- **Sharing** — invite users by email to collaborate on a project; optional token-based join links
- **Size limits** — project storage size is calculated via an AWS Lambda function and enforced in real time on upload
- **Tests** — unit tests (service layer, isolated with mocks) and integration tests (full HTTP flow)
- **CI** — GitHub Actions pipeline runs linting (ruff) and the full test suite on every pull request

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy (ORM) |
| Auth | JWT (PyJWT), bcrypt password hashing |
| File storage | AWS S3 |
| Size calculation | AWS Lambda |
| Containerization | Docker + Docker Compose |
| Packaging | Poetry |
| Testing | pytest, unittest.mock |
| Linting | ruff |
| CI | GitHub Actions |

## Architecture

The app is organized into three layers, each with a single responsibility:

- **Routes** (`app/api/`) — handle HTTP concerns only: request parsing, dependency injection, response shaping.
- **Services** (`app/services/`) — contain business logic (validation rules, orchestration) with no knowledge of FastAPI or HTTP.
- **Security** (`app/security.py` / `app/api/deps.py`) — authentication (`deps.py`, "who is this user") is separated from authorization (`security.py`, "what are they allowed to do").

This split means business rules can be unit tested directly, without spinning up a server or making real HTTP requests.

The database schema exists in two forms: `app/models.py` (SQLAlchemy ORM, used by the running app) and `schema.sql` (hand-written raw SQL, demonstrating the same structure without an ORM).

## Project Structure

```
.
├── app/
│   ├── api/            # routers (auth, projects, documents)
│   ├── services/        # business logic (project_service, document_service, storage_service)
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── security.py       # authorization dependencies
│   ├── config.py          # environment-based settings
│   └── main.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                 # unit + integration tests
├── .github/workflows/      # CI pipeline
├── schema.sql               # raw SQL schema (ORM-free)
└── pyproject.toml            # Poetry project + dependencies
```


### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker Desktop
- A PostgreSQL database (or use the provided Docker Compose setup)
- An AWS account with an S3 bucket and a Lambda function (for document storage and size limits)

### Environment variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://user:password@localhost:5432/project_manager
SECRET_KEY=your-jwt-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

LAMBDA_FUNCTION_NAME=your-lambda-function-name
MAX_PROJECT_SIZE_BYTES=104857600

POSTGRES_PASSWORD=your-postgres-password
```

### Run locally

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`.

### Run with Docker

```bash
cd docker
docker compose --env-file ../.env up --build
```

This starts both the API container and a PostgreSQL container, with the schema loaded automatically from `schema.sql`.

### Run tests

```bash
poetry run pytest tests/ -v
```

### Run the linter

```bash
poetry run ruff check .
```

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new user |
| POST | `/auth/login` | Log in, receive a JWT |
| GET | `/auth/me` | Get the current user |
| POST | `/projects` | Create a project (creator becomes owner) |
| GET | `/projects` | List all projects accessible to the user |
| GET | `/projects/{id}` | Get a project's details |
| PUT | `/projects/{id}` | Update a project's name/description |
| DELETE | `/projects/{id}` | Delete a project (owner only) |
| POST | `/projects/{id}/invite` | Grant a user access to a project (owner only) |
| GET | `/projects/{id}/share` | Generate a hashed, time-limited join link |
| GET | `/join` | Consume a join link and gain project access |
| POST | `/project/{id}/documents` | Upload a document (PDF/DOCX) |
| GET | `/project/{id}/documents` | List a project's documents |
| GET | `/document/{id}` | Get a presigned download URL |
| PUT | `/document/{id}` | Replace a document's file |
| DELETE | `/document/{id}` | Delete a document (owner only) |

All endpoints (except register/login) require a `Bearer` JWT in the `Authorization` header. Access control distinguishes **owners** (full control) from **participants** (can view/modify, cannot delete).

## CI

Every pull request into `main` triggers a GitHub Actions workflow (`.github/workflows/pr-checks.yml`) that:

1. Installs dependencies via Poetry
2. Runs `ruff check .` for linting
3. Runs the full `pytest` suite

Tests run against an in-memory SQLite database and mock all AWS (S3, Lambda) calls, so the pipeline requires no real credentials or external services.

## Notes on Scope

- The focus for this project was a working CI pipeline.
- Image resizing via Lambda was left out, as marked optional in the project spec.