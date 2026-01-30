# Personal Knowledge Vault

A production-grade RAG (Retrieval-Augmented Generation) application for managing personal notes with AI-powered semantic search and question answering.

## Features

- **Authentication**: JWT-based email/password authentication
- **Notes CRUD**: Create, read, update, delete notes with tags
- **Semantic Search**: Vector similarity search using pgvector
- **RAG Q&A**: Ask questions about your notes and get AI-generated answers with citations
- **Automatic Embeddings**: Notes are automatically vectorized using OpenAI embeddings
- **Production Ready**: Structured logging, error handling, tests, migrations

## Tech Stack

- **Backend**: Python 3.12 + FastAPI
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose) + bcrypt password hashing
- **AI**: OpenAI embeddings + chat completions
- **Testing**: pytest + TestClient

## Architecture

```
app/
├── api/v1/          # API routes (auth, notes, search, rag)
├── core/            # Security utilities, exceptions
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic (auth, notes, embeddings, RAG)
├── config.py        # Pydantic settings from .env
├── database.py      # SQLAlchemy engine + session
└── main.py          # FastAPI app initialization
```

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- OpenAI API key (optional for development)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd knowledge-vault

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create database
createdb knowledge_vault

# Configure environment
cp .env.example .env
# Edit .env and add your DATABASE_URL and OPENAI_API_KEY
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/knowledge_vault

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-min-32-characters

# OpenAI (optional for development)
OPENAI_API_KEY=sk-your-key-here
```

### Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or use the app startup (creates tables + pgvector extension)
uvicorn app.main:app --reload
```

## Running the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the API:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Usage

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Create Note

```bash
curl -X POST http://localhost:8000/api/v1/notes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning Basics",
    "content": "Neural networks are composed of layers...",
    "tags": ["ml", "ai"]
  }'
```

### 4. Semantic Search

```bash
curl -X GET "http://localhost:8000/api/v1/search/?query=neural%20networks&top_k=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Ask Question (RAG)

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask?query=What%20did%20I%20learn%20about%20ML?" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "answer": "Based on your notes, you learned that neural networks...",
  "citations": [
    {
      "note_id": 1,
      "title": "Machine Learning Basics",
      "excerpt": "Neural networks are composed...",
      "similarity": 0.89
    }
  ]
}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY` (32+ characters)
- Set `DEBUG=false`
- Configure `ALLOWED_ORIGINS` for your frontend domain
- Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)

## Interview Talking Points

### Architecture Decisions

- **Layered Architecture**: Routes → Services → Repositories for clean separation
- **Provider Abstraction**: `EmbeddingProvider` interface allows swapping OpenAI for other providers
- **Graceful Degradation**: App runs without OpenAI key (CRUD works, AI features return safe errors)
- **Dependency Injection**: FastAPI's DI system for testability and clean code

### Production Readiness

- **Structured Logging**: JSON logs for monitoring tools (Datadog, CloudWatch)
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Security**: JWT tokens, bcrypt password hashing, CORS configuration
- **Testing**: Integration tests with isolated test database
- **Migrations**: Alembic for reproducible schema changes

### Scalability Considerations

- **Connection Pooling**: SQLAlchemy pool (5 base + 10 overflow)
- **Vector Indexing**: pgvector HNSW index for fast similarity search
- **Pagination**: All list endpoints support skip/limit
- **Batch Embeddings**: Process multiple notes in one API call

## License

MIT

## Author

Your Name - [GitHub](https://github.com/yourusername)
