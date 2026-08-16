CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    permissions VARCHAR(50) NOT NULL DEFAULT 'user'
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL REFERENCES users(id)
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(id),
    file_path VARCHAR(255) NOT NULL
);

CREATE TABLE project_access (
    user_id INT NOT NULL REFERENCES users(id),
    project_id INT NOT NULL REFERENCES projects(id),
    is_owner BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id, project_id)
);