# Projeto Enem Corretor

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg)
![Celery](https://img.shields.io/badge/celery-%2337814A.svg)

## Overview

This project implements a scalable backend architecture for the automated correction of ENEM essays using Generative Artificial Intelligence (Google Gemini). The system allows users to submit essays and receive detailed feedback based on the official competency matrix.

The architecture is designed to be asynchronous and resilient, utilizing a message broker (Redis) and distributed workers (Celery) to handle the AI processing load without blocking the main application API.

## Architecture

The system consists of four main containerized services orchestrated via Docker Compose:

1.  **API (FastAPI)**: Serves as the entry point, handling authentication (JWT), request validation, and task dispatching.
2.  **Worker (Celery)**: Consumes correction tasks from the queue, interacts with the LLM (Large Language Model), and processes business rules (scoring, discrepancy checks).
3.  **Database (PostgreSQL)**: Persists user data, essays, and correction results.
4.  **Broker/Cache (Redis)**: Manages the task queue for Celery and potentially caches frequent queries.

## Prerequisites

*   **Docker Engine** (v20.10+)
*   **Docker Compose** (v2.0+)
*   **Google API Key** (for Gemini Model access)

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd projeto-enem-corretor
    ```

2.  **Environment Configuration:**
    Ensure the `.env` file is present in the root directory with the following keys:
    ```env
    DATABASE_URL=postgresql://user:password@db/dbname
    CELERY_BROKER_URL=redis://redis:6379/0
    GOOGLE_API_KEY=your_api_key_here
    SECRET_KEY=your_secure_secret_key
    ```

3.  **Build and Run:**
    Execute the following command to build the images and start the containers. The `--build` flag ensures dependencies are up to date.
    ```bash
    docker compose up --build -d
    ```

4.  **Verification:**
    Access the OpenAPI documentation to verify the service status:
    *   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Documentation

### Authentication

The API uses **OAuth2 with Password Flow** and **Bearer JWT** tokens.

1.  **Registration**: `POST /register`
    *   Payload: `{ "email": "user@example.com", "password": "secure_password" }`
2.  **Login**: `POST /token`
    *   Payload (Form Data): `username=user@example.com`, `password=secure_password`
    *   Response: `{ "access_token": "...", "token_type": "bearer" }`

All subsequent requests to protected endpoints must include the header:
`Authorization: Bearer <access_token>`

### Workflow: Essay Correction

The correction process is asynchronous. The frontend application should implement a polling mechanism or webhook listener (future implementation) to retrieve results.

1.  **Submission**:
    *   Endpoint: `POST /api/v1/redacoes/`
    *   Description: Queues the text for correction.
    *   Response: `202 Accepted` with the Essay ID and status `PENDENTE`.

2.  **Status Check (Polling)**:
    *   Endpoint: `GET /api/v1/redacoes/{id}`
    *   Description: Returns the current status of the essay.
    *   **Statuses**:
        *   `PENDENTE`: Queued for execution.
        *   `PROCESSANDO`: Worker is currently analyzing the text.
        *   `CONCLUIDO`: analysis complete, results available.
        *   `ERRO`: Processing failed.

3.  **Result Retrieval**:
    *   When status is `CONCLUIDO`, the response will contain a `resultado_json` field with the detailed breakdown:
        ```json
        {
          "nota_final": 960,
          "competencias": [
            { "competencia": 1, "nota": 160, "justificativa": "..." },
            ...
          ]
        }
        ```

## Project Structure

*   `backend/`: FastAPI application source code (Routers, Core logic).
*   `worker/`: Celery worker source code (Agents, Business Rules).
*   `shared/`: Shared modules (Pydantic Schemas, SQLAlchemy Models, Configuration).
*   `tests/`: Automated test suite (Pytest).
*   `alembic/`: Database migration scripts.

## Database Migrations

Access the running container to apply database schema changes:

```bash
docker compose run --rm api alembic upgrade head
```

## Security

*   **Non-Root Execution**: services run as a dedicated `appuser` to minimize privilege escalation risks.
*   **Network Isolation**: Database ports are bound to `127.0.0.1` on the host, preventing external access.
*   **Validation**: All inputs are strictly validated using Pydantic V2.


