# Mini-RAG-App

A modular **Retrieval-Augmented Generation (RAG)** API built with **FastAPI, MongoDB, Qdrant, and LLM/embedding providers**.

## Features

* Document upload and processing
* Configurable document chunking
* Embedding generation
* Semantic search with Qdrant
* RAG-based question answering
* MongoDB for document metadata and chunks
* Health and readiness endpoints
* Docker Compose infrastructure

## Architecture

The application follows a pipeline-based RAG architecture:

                    ┌──────────────────┐
                    │      Client      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │      Routes      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌───────────┐   ┌───────────┐
        │Documents │   │    RAG    │   │   Health  │
        │  Routes  │   │   Routes  │   │   Routes  │
        └────┬─────┘   └─────┬─────┘   └───────────┘
             │               │
             ▼               ▼
        ┌─────────────────────────┐
        │       Controllers       │
        │ Asset / Process / RAG   │
        └────────────┬────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌─────────────┐       ┌─────────────┐
    │   MongoDB   │       │   Qdrant    │
    │             │       │             │
    │ Projects    │       │  Embeddings │
    │ Assets      │       │             │
    │ Chunks      │       │             │
    └─────────────┘       └─────────────┘
                                 ▲
                                 │
                          ┌──────┴──────┐
                          │  Embedding  │
                          │    Model    │
                          └─────────────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │  Chat Model │
                          └─────────────┘
## Tech Stack

* **Python**
* **FastAPI**
* **MongoDB**
* **Qdrant**
* **OpenAI**
* **OpenRouter**
* **LangChain**
* **Docker**
* **uv**

## Project Structure
```text
Mini-RAG/
│
├── Docker/
│   ├── docker-compose.yml       # MongoDB and Qdrant services
│   ├── mongodb_data/            # MongoDB persistent data
│   └── qdrant_data/             # Qdrant persistent data
│
├── src/
│   │
│   ├── assets/                   # Application assets and uploaded files
│   │
│   ├── controllers/              # Application/business logic
│   │   ├── AssetController.py    # Asset and document operations
│   │   ├── BaseController.py     # Shared controller functionality
│   │   ├── ProcessController.py  # Document processing and chunking
│   │   ├── ProjectController.py  # Project-related operations
│   │   └── RagController.py      # RAG pipeline operations
│   │
│   ├── helpers/                  # Shared utilities and helper functions
│   │
│   ├── models/                   # Data models and database operations
│   │
│   ├── routes/                   # FastAPI API routes
│   │   ├── documents.py          # Document upload and processing endpoints
│   │   ├── rag.py                # Embedding, retrieval, and RAG endpoints
│   │   ├── health.py             # Liveness and readiness endpoints
│   │   ├── enums/                # API-related enumerations
│   │   └── request_schemes/      # Request and response schemas
│   │
│   ├── stores/                   # External service integrations
│   │   ├── llm/                  # LLM provider implementations
│   │   └── vectorDB/             # Vector database implementations
│   │
│   ├── .env.example              # Example environment configuration
│   ├── main.py                   # FastAPI application entry point
│   ├── pyproject.toml            # Project metadata and dependencies
│   └── uv.lock                   # Locked Python dependencies
│
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/MOH-YAHIA/Mini-RAG.git
cd Mini-RAG
```

### 2. Configure environment variables

```bash
cp src/.env.example src/.env
```

Update the values in `src/.env` with your database and LLM configuration.

### 3. Start MongoDB and Qdrant

```bash
cd Docker
docker compose up -d
```

Check the running containers:

```bash
docker compose ps
```

### 4. Install Python dependencies

```bash
cd ../src
uv sync
```

### 5. Start the FastAPI application

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint                            | Description                       |
| ------ | ----------------------------------- | --------------------------------- |
| `POST` | `/documents/upload/{project_id}`    | Upload a document                 |
| `POST` | `/documents/process/{project_id}`   | Process and chunk documents       |
| `POST` | `/rag/embed/{project_id}`           | Generate document embeddings      |
| `POST` | `/rag/retrieve/{project_id}`        | Retrieve relevant chunks          |
| `POST` | `/rag/chat/{project_id}`            | Generate a RAG answer             |
| `GET`  | `/rag/collection_info/{project_id}` | Get Qdrant collection information |
| `GET`  | `/health/live`                      | Check API liveness                |
| `GET`  | `/health/ready`                     | Check service readiness           |

## RAG Workflow

The application follows the standard RAG pipeline:

```text
1. Upload document
        ↓
2. Process and split into chunks
        ↓
3. Store chunks in MongoDB
        ↓
4. Generate embeddings
        ↓
5. Store vectors in Qdrant
        ↓
6. Embed user query
        ↓
7. Retrieve relevant chunks
        ↓
8. Generate answer using the LLM
```

## Database Responsibilities

### MongoDB

MongoDB stores application and document data, including:

* Projects
* Assets Metadata
* Document chunks

### Qdrant

Qdrant is used as the vector database for:

* Document embeddings
* Semantic similarity search
* Retrieval of relevant chunks


