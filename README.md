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

## Demo

> **Note**: A demo GIF/video will be added here showing the complete workflow

To run the demo script:

```bash
# Start the server first
uvicorn app.main:app --reload

# In another terminal, run the demo
./scripts/demo.sh
```

The demo showcases:
1. User registration and authentication
2. Creating notes about machine learning
3. Semantic search with similarity scores
4. RAG-based question answering with citations
5. CRUD operations (update, delete)

### Recording a Demo

```bash
# Install asciinema and agg
brew install asciinema
cargo install --git https://github.com/asciinema/agg

# Record the demo
asciinema rec demo.cast
./scripts/demo.sh
exit

# Convert to GIF
agg demo.cast demo.gif
```

## Docker Deployment

### Quick Start with Docker Compose

The easiest way to run the entire stack (API + PostgreSQL with pgvector):

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

This starts:
- PostgreSQL 17 with pgvector extension on port 5432
- FastAPI application on port 8000

### Environment Configuration

Create a `.env` file in the project root:

```bash
SECRET_KEY=your-generated-secret-key-here
OPENAI_API_KEY=sk-your-openai-key
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
```

### Manual Docker Build

```bash
# Build the image
docker build -t knowledge-vault:latest .

# Run with external PostgreSQL
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  -e OPENAI_API_KEY=sk-your-key \
  knowledge-vault:latest
```

### Production Deployment

For production deployments:

- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Set `DEBUG=false`
- Configure `ALLOWED_ORIGINS` for your frontend domain
- Use managed PostgreSQL (AWS RDS, DigitalOcean, Render, etc.)
- Enable HTTPS/TLS
- Set up monitoring and logging aggregation

## Evaluation

This project includes a comprehensive evaluation framework for measuring RAG system performance.

### Metrics

- **Precision@K**: Fraction of retrieved notes that are relevant
- **Recall@K**: Fraction of relevant notes that were retrieved
- **Mean Reciprocal Rank (MRR)**: Quality of ranking
- **Latency**: Average query response time in milliseconds

### Running Evaluation

```bash
# Create evaluation dataset (see data/eval_queries.json)
# Then run evaluation
python scripts/evaluate_rag.py --dataset data/eval_queries.json --k 5
```

### Sample Results

Example evaluation on a test dataset of 50 queries:

| Metric | Value |
|--------|-------|
| Precision@5 | 0.8400 |
| Recall@5 | 0.7200 |
| MRR | 0.8950 |
| Avg Latency | 145.32 ms |

### Creating Evaluation Datasets

Format for `data/eval_queries.json`:

```json
[
  {
    "query": "What are neural networks?",
    "relevant_note_ids": [1, 3, 5],
    "description": "Query about ML fundamentals"
  }
]
```

See `data/README.md` for detailed instructions.

## Continuous Integration

This project uses GitHub Actions for automated testing on every push and pull request.

### CI Pipeline

- **Linting**: Flake8 for code quality
- **Testing**: pytest with coverage reporting
- **Docker Build**: Validates Docker image builds
- **Coverage**: Automatic upload to Codecov

### Running Locally

```bash
# Run linting
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Run tests with coverage
pytest tests/ --cov=app --cov-report=term --cov-report=html

# View coverage report
open htmlcov/index.html
```

### CI Status

[![CI](https://github.com/pm32900/personal-knowledge-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/pm32900/personal-knowledge-vault/actions/workflows/ci.yml)

## Known Limitations & Roadmap

### Current Limitations

- **Embedding Provider**: Currently locked to OpenAI embeddings
  - No support for local models (Sentence Transformers, etc.)
  - No fallback if OpenAI rate limits are hit
- **Retrieval**: Basic cosine similarity only
  - No reranking step
  - No hybrid search (keyword + semantic)
- **Caching**: No embedding or response caching
  - Repeated queries regenerate embeddings
  - LLM responses not cached
- **Scalability**: Single-instance deployment
  - No horizontal scaling support yet
  - No distributed vector index



## License

MIT

## Author

Prajwal Moras - [GitHub](https://github.com/pm32900)
