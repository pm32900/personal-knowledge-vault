# Interview Preparation Guide - Personal Knowledge Vault

This document contains all interview questions and talking points for discussing your Personal Knowledge Vault project.

---

## Architecture & Design Decisions

### Q: Why did you structure the project with a layered architecture?

**Answer**: "I used a layered architecture with clear separation of concerns. Routes handle HTTP requests and responses, services contain all business logic like the RAG pipeline, and repositories abstract database access. This makes the code testable—I can mock the repository layer in unit tests without touching the database."

**Follow-up depth**: "For example, my `rag_service.py` orchestrates the entire RAG flow: it calls the embedding service to vectorize the query, calls the note repository to retrieve top-k similar notes, then calls OpenAI to generate an answer with citations. Each layer has a single responsibility."

---

### Q: Why `app/api/v1/` for routes?

**Answer**: "I structured routes under `api/v1/` to support API versioning. If I need to make breaking changes later—like changing the authentication flow or response format—I can create `api/v2/` and run both versions in parallel. This prevents breaking existing clients."

**Real-world example**: "Stripe and GitHub both do this. They maintain `/v1/` and `/v2/` endpoints simultaneously during migration periods."

---

### Q: What's the difference between `core/` and `services/`?

**Answer**: "`core/` contains low-level utilities used across the app—password hashing, JWT encoding, custom exceptions. `services/` contains business logic specific to features—the RAG pipeline, embedding generation, note management. Core is infrastructure, services are domain logic."

---

### Q: How would you swap out OpenAI for another provider?

**Answer**: "I designed an `EmbeddingProvider` interface in `embedding_service.py`. The OpenAI implementation is just one concrete class. To switch to Cohere or a local model, I'd create a new class implementing the same interface and swap it in the dependency injection container. Zero changes to the RAG service."

**Why it matters**: "This follows the dependency inversion principle—high-level modules (RAG service) depend on abstractions (the interface), not concrete implementations (OpenAI client)."

---

## Production Readiness

### Q: What happens if the OpenAI API key is missing?

**Answer**: "The system doesn't crash. I check for the API key in the config layer. If it's missing, the embedding service returns a safe placeholder response like 'AI service unavailable' instead of throwing a 500 error. This prevents the entire app from being unusable if one external dependency fails."

**Real-world context**: "In production, you might have rate limits or temporary outages. Graceful degradation keeps the core CRUD functionality working even when AI features are down."

---

### Q: Why structured logging over standard Python logging?

**Answer**: "`structlog` outputs structured JSON logs instead of plain text. This makes logs machine-parseable for tools like Datadog or CloudWatch Insights. I can query 'show me all RAG requests where latency > 2 seconds' easily. Standard logging requires regex parsing, which is fragile."

**Example output**:
```json
{"event": "rag_request", "user_id": 123, "query": "...", "latency_ms": 450, "timestamp": "2026-01-28T14:43:00Z"}
```

---

### Q: How do you test the RAG pipeline without making real API calls?

**Answer**: "I use FastAPI's dependency injection system. In tests, I override the `get_embedding_service` dependency with a mock that returns fake vectors. This lets me test the entire RAG flow—retrieval logic, citation formatting, error handling—without spending money on API calls or dealing with network flakiness."

---

## Database & Performance

### Q: Why PostgreSQL instead of a vector database like Pinecone?

**Answer**: "For an MVP, I wanted to minimize operational complexity. PostgreSQL with pgvector gives me relational data (users, notes) and vector search in one database. No need to sync between two systems. For scale, I could later migrate vectors to a dedicated vector DB, but for thousands of notes, Postgres is plenty fast."

**Technical depth**: "pgvector supports HNSW indexing for approximate nearest neighbor search, which scales to millions of vectors. I'm using cosine similarity for semantic search."

---

### Q: Why `pool_pre_ping=True` in database configuration?

**Answer**: "Verifies connections are alive before using them. Prevents 'connection already closed' errors when database restarts or connections timeout."

---

### Q: Explain connection pooling: `pool_size=5, max_overflow=10`

**Answer**: "Maintains 5 persistent connections, can create 10 more under load. Reusing connections is faster than creating new ones for each request."

---

### Q: Why `yield` in `get_db()` dependency?

**Answer**: "FastAPI's dependency injection uses generators. `yield` pauses execution, returns the session to the route, then resumes to close it. Guarantees cleanup even if the route raises an exception."

---

### Q: What does `DATABASE_ECHO` do?

**Answer**: "When true, SQLAlchemy logs every SQL query to stdout. This is useful for debugging—you can see exactly what queries are being generated. But in production, it's noise and a performance hit. I keep it false by default and enable it only when troubleshooting."

---

## Security & Authentication

### Q: Why bcrypt over SHA256 for passwords?

**Answer**: "bcrypt is designed for passwords—it's slow by design (work factor) and includes automatic salting. SHA256 is fast, making it vulnerable to brute-force. bcrypt's computational cost scales with hardware improvements."

---

### Q: JWT vs Session Cookies?

**Answer**: "JWTs are stateless—no database lookup per request. The token contains the user ID, so I can verify authentication by checking the signature. Scales better than session storage for distributed systems."

---

### Q: Why `datetime.utcnow()` for timestamps?

**Answer**: "Always use UTC for timestamps in distributed systems. Avoids timezone confusion when servers are in different regions."

---

### Q: Token expiration strategy?

**Answer**: "30-minute expiration balances security and UX. Short enough to limit damage if stolen, long enough users aren't constantly re-authenticating. Production apps add refresh tokens for longer sessions."

---

### Q: Why return `None` instead of raising exception in `decode_access_token`?

**Answer**: "`decode_access_token` returns `None` for invalid tokens so the caller can decide how to handle it—maybe return 401, maybe try refresh token. Exceptions force one error-handling path."

---

### Q: Why same error message for wrong email/password?

**Answer**: "Security best practice. If I say 'email not found' vs 'wrong password', attackers can enumerate valid emails. Generic 'invalid credentials' prevents user enumeration."

---

### Q: Token payload: Why `str(user.id)`?

**Answer**: "JWT payloads are JSON. Python integers serialize fine, but explicit string conversion ensures consistency across different JWT libraries."

---

## Configuration & Environment

### Q: Why Pydantic Settings over `os.getenv()`?

**Answer**: "Pydantic Settings provides automatic type conversion and validation. If I set `ACCESS_TOKEN_EXPIRE_MINUTES=abc` in `.env`, Pydantic raises a validation error at startup instead of failing later when I try to use it as an integer. This 'fail fast' approach catches config errors before they reach production."

**Type safety**: "With `os.getenv()`, everything is a string. With Pydantic, I get proper types—`DEBUG` is a bool, `TOP_K_RESULTS` is an int. My IDE autocompletes and catches type errors."

---

### Q: What does `@lru_cache()` do on `get_settings()`?

**Answer**: "`lru_cache` ensures settings are loaded only once and cached in memory. Without it, every call to `get_settings()` would re-read the `.env` file and re-validate. This is wasteful. The cache makes it a singleton pattern—one settings instance shared across the entire app."

---

### Q: Why allow an empty OpenAI API key?

**Answer**: "I want the app to start even without an OpenAI key, so developers can work on auth and CRUD features without needing API access. The `is_openai_configured` property checks if the key is valid. When someone calls the RAG endpoint, I check this property and return a friendly error instead of crashing the entire app."

**Production consideration**: "In production, I'd make this required by removing the default value. But for development, graceful degradation improves developer experience."

---

### Q: Why a `cors_origins` property?

**Answer**: "Environment variables are strings. CORS middleware needs a list of strings. The `cors_origins` property parses the comma-separated string into a list and strips whitespace. This keeps parsing logic in one place instead of scattered across the codebase."

---

### Q: Why `extra='ignore'` in `model_config`?

**Answer**: "My `.env` file might have variables for other tools—like `PATH` or `HOMEBREW_PREFIX`. Without `extra='ignore'`, Pydantic would raise an error for every unknown variable. This setting tells Pydantic to only validate the fields I've defined and ignore everything else."

---

### Q: Why separate `is_production` property?

**Answer**: "Centralized logic. If I later decide production means `ENVIRONMENT in ['production', 'prod', 'prd']`, I change one property instead of hunting through the codebase. It also makes the code more readable—`if settings.is_production` is clearer than `if settings.ENVIRONMENT.lower() == 'production'`."

---

### Q: Why `.env.example` vs `.env`?

**Answer**: "`.env` contains secrets like API keys and database passwords. Committing it would expose credentials in Git history forever—even if you delete it later. `.env.example` documents what variables are needed without exposing real values. Every developer copies it to `.env` and fills in their own credentials."

**Security principle**: "This follows the 12-factor app methodology—configuration belongs in the environment, not in code."

---

### Q: Why `SECRET_KEY` must be 32+ characters?

**Answer**: "JWT tokens are signed with HMAC-SHA256. A short secret key is vulnerable to brute-force attacks. The algorithm requires at least 256 bits (32 bytes) for cryptographic security. In production, I'd generate this with `openssl rand -hex 32` to ensure randomness."

---

## Dependencies & Packages

### Q: Why pin exact versions in `requirements.txt`?

**Answer**: "I pin exact versions to ensure reproducible builds. If someone clones this repo in 6 months, they'll get the exact same dependency tree I tested with. Unpinned versions can introduce breaking changes—for example, Pydantic v2 broke compatibility with v1. In production, surprises are bad."

**Follow-up**: "For a library I'd publish to PyPI, I'd use ranges. But for an application, exact pins are the standard."

---

### Q: Why `psycopg2-binary` instead of `psycopg2`?

**Answer**: "`psycopg2-binary` is a pre-compiled wheel that installs without needing PostgreSQL development headers. `psycopg2` requires compiling from source. For development and small-scale production, binary is faster and easier. For high-performance production at scale, you'd compile from source for optimization."

---

### Q: Why `pgvector` specifically?

**Answer**: "`pgvector` is a PostgreSQL extension that adds vector similarity search. For an MVP, keeping vectors and relational data in one database simplifies architecture—no data syncing between systems. It supports cosine similarity and HNSW indexing, which scales to millions of vectors. If I needed sub-10ms latency at billion-vector scale, I'd migrate to Pinecone or Weaviate."

---

### Q: What does `tiktoken` do?

**Answer**: "`tiktoken` is OpenAI's tokenizer library. I use it to count tokens before sending prompts to the API. This prevents hitting context limits and helps estimate costs. For example, GPT-4 has an 8k token limit—if my retrieved notes + query exceed that, I truncate intelligently instead of getting an API error."

---

### Q: Testing stack: `pytest` + `pytest-asyncio` + `faker`?

**Answer**: "`pytest` is the industry standard—cleaner syntax than unittest. `pytest-asyncio` lets me test async FastAPI endpoints without blocking. `faker` generates realistic test data (emails, names, text) so my tests aren't full of 'test@test.com' and 'foo bar'—this catches edge cases like unicode handling."

---

### Q: Why `pyproject.toml` AND `requirements.txt`?

**Answer**: "`pyproject.toml` is the modern Python standard (PEP 518) for project metadata and build configuration. `requirements.txt` is for simple pip installs. I keep both for compatibility—some CI/CD systems still expect `requirements.txt`, but `pyproject.toml` lets me configure tools like pytest and black in one place."

---

## Models & Data

### Q: Why `index=True` on email in User model?

**Answer**: "Email is used for login lookups. Without an index, Postgres does a full table scan—O(n). With an index, it's O(log n). Critical for performance at scale."

---

### Q: What does `cascade='all, delete-orphan'` do?

**Answer**: "When a user is deleted, all their notes are automatically deleted. Prevents orphaned data. 'delete-orphan' also deletes notes if removed from the `user.notes` list."

---

### Q: Why `hashed_password` not `password`?

**Answer**: "Naming makes it clear we never store plaintext passwords. Code review would catch `user.password = 'foo'` immediately."

---

### Q: What does `onupdate=datetime.utcnow` do?

**Answer**: "Automatically updates `updated_at` whenever any field changes. Useful for audit trails and cache invalidation."

---

### Q: Why is the `embedding` column nullable in Note model?

**Answer**: "Notes can be created before embeddings are generated (async processing). The app remains functional even if OpenAI is down—users can still CRUD notes."

---

### Q: Why `ARRAY(String)` for tags?

**Answer**: "Postgres native array type. Can query with `tags @> ['python']` to find notes containing 'python' tag. More efficient than a separate tags table for simple use cases."

---

### Q: Why index on `created_at`?

**Answer**: "Common query: 'show my recent notes'. Without an index, Postgres scans the entire table and sorts. With an index, it's a simple range scan."

---

### Q: Vector dimension: Why 1536?

**Answer**: "That's the output size of OpenAI's `text-embedding-3-small` model. Each text gets converted to a 1536-dimensional vector. The pgvector column must match this dimension. If I switch to a different embedding model (like `text-embedding-ada-002` which is also 1536, or a local model), I'd update this value and run a migration."

---

## Schemas & Validation

### Q: Why separate Create/Response schemas for users?

**Answer**: "Never return passwords in API responses. `UserCreate` has password, `UserResponse` doesn't. Pydantic enforces this at the type level—can't accidentally leak secrets."

---

### Q: What is `EmailStr` validation?

**Answer**: "Pydantic validates email format automatically. Rejects 'notanemail' but accepts 'user@domain.com'. Saves writing regex validators."

---

### Q: What does `from_attributes = True` do?

**Answer**: "Lets Pydantic convert SQLAlchemy models to schemas. Without this, `UserResponse.from_orm(user)` fails. Replaces old `orm_mode = True` in Pydantic v2."

---

### Q: Password constraints - why `min_length=8`?

**Answer**: "`min_length=8` enforces basic security. Production apps add complexity rules (uppercase, numbers, symbols) but 8 chars is the minimum standard."

---

### Q: Why all fields `Optional` in `NoteUpdate`?

**Answer**: "All fields are `Optional` so clients can update just title, just content, or just tags. The service layer handles merging with existing data."

---

### Q: What is `NoteSearchResult` schema for?

**Answer**: "Wraps the note with metadata—similarity score (0-1) and an excerpt. Clients can show 'Match: 87%' and highlight relevant passages."

---

### Q: Why `Field(default_factory=list)` for tags?

**Answer**: "Mutable defaults in Python are dangerous. `tags: List[str] = []` would share the same list across all instances. `default_factory` creates a new list each time."

---

## Services & Business Logic

### Q: Why custom exceptions instead of generic ones?

**Answer**: "Instead of raising generic `ValueError` everywhere, custom exceptions make intent clear. `raise NotFoundError('Note not found')` is more semantic than `raise Exception('Not found')`."

---

### Q: Why include status code in exception?

**Answer**: "Each exception knows its HTTP status code. The FastAPI exception handler can catch `AppException` and automatically return the right status—no if/else chains in routes."

---

### Q: Exception hierarchy - why inherit from `AppException`?

**Answer**: "All inherit from `AppException`, so I can catch all app errors with one handler while letting system errors (like `MemoryError`) propagate differently."

---

### Q: Why `AIServiceError` with 503?

**Answer**: "503 Service Unavailable tells clients the failure is temporary (OpenAI rate limit, timeout). Clients can retry. 500 would imply a bug in my code."

---

### Q: Strategy pattern in embedding service?

**Answer**: "`EmbeddingProvider` is an interface. To swap OpenAI for Cohere, create `CohereEmbeddingProvider` implementing the same methods. Change one line in `get_embedding_service()`."

---

### Q: Why batch processing in `embed_batch`?

**Answer**: "`embed_batch` sends multiple texts in one API call. OpenAI charges per token, not per request. Batching 100 notes is 100x cheaper than 100 separate calls."

---

### Q: Automatic embedding generation?

**Answer**: "`create_note` and `update_note` automatically generate embeddings. Users don't need to think about it—just create a note and it's searchable."

---

### Q: Authorization check in `get_note`?

**Answer**: "Every read/update/delete goes through `get_note`, which validates ownership. Prevents user A from accessing user B's notes. Single point of enforcement."

---

### Q: Pagination in `list_notes`?

**Answer**: "`skip` and `limit` parameters enable pagination. Without this, loading 10,000 notes would crash the client. Standard REST pattern."

---

## RAG Pipeline

### Q: Explain pgvector cosine similarity?

**Answer**: "`<=>` is pgvector's cosine distance operator. `1 - distance` converts to similarity (0-1). Ordering by distance directly is faster than computing similarity for all rows."

---

### Q: Two-stage RAG pipeline?

**Answer**: "Stage 1: Vector search retrieves top-k relevant notes. Stage 2: LLM generates answer from retrieved context. Separating retrieval and generation makes each component testable."

---

### Q: Citation format?

**Answer**: "Answer references notes as [1], [2]. Citations array maps these to note IDs, titles, and excerpts. Frontend can make citations clickable links to full notes."

---

### Q: Context window management?

**Answer**: "Only send top-k notes to avoid exceeding token limits. With 1000 max tokens for answer and ~200 tokens per note, 5 notes leaves room for the prompt."

---

### Q: Semantic vs keyword search?

**Answer**: "Traditional search matches exact words. Semantic search understands meaning—'ML models' matches notes about 'machine learning algorithms'. Uses vector embeddings to measure conceptual similarity."

---

### Q: Similarity scores?

**Answer**: "Returns 0-1 similarity score. Frontend can show 'Match: 87%' or filter results below threshold. Helps users understand relevance."

---

## API Design

### Q: Dependency injection for database sessions?

**Answer**: "`db: Session = Depends(get_db)` automatically provides a database session. FastAPI calls `get_db()`, passes result to route, then closes session. No manual session management."

---

### Q: Why response models in routes?

**Answer**: "`response_model=UserResponse` ensures password is never returned. Even if service accidentally includes it, FastAPI filters to schema fields. Security by default."

---

### Q: Status codes - 201 vs 200?

**Answer**: "201 Created for registration (resource created), 200 OK for login (no new resource). Semantic HTTP codes help clients distinguish success types."

---

### Q: Protected routes with `get_current_user_dep`?

**Answer**: "Every endpoint requires authentication. `current_user: User = Depends(get_current_user_dep)` extracts user from JWT. If token is invalid, FastAPI returns 401 before route runs."

---

### Q: RESTful design?

**Answer**: "Standard REST patterns: POST `/` creates, GET `/` lists, GET `/{id}` reads one, PUT `/{id}` updates, DELETE `/{id}` deletes. Predictable for frontend developers."

---

### Q: Why 204 No Content for delete?

**Answer**: "DELETE returns 204 with no body. Signals success without wasting bandwidth. Standard HTTP practice for destructive operations."

---

### Q: Query parameters with validation?

**Answer**: "`Query(..., min_length=1)` validates query isn't empty. `ge=1, le=20` constrains top_k to 1-20. FastAPI returns 422 if validation fails. No manual checks needed."

---

### Q: POST vs GET for RAG ask endpoint?

**Answer**: "Using POST even though it's a read operation. Query strings have length limits—complex questions might exceed URL limits. POST body has no such constraint."

---

## FastAPI & Application

### Q: Exception handler hierarchy?

**Answer**: "Custom `AppException` handler catches domain errors (401, 404) and returns clean JSON. General handler catches unexpected errors (bugs) and logs full traceback while returning generic 500."

---

### Q: CORS configuration?

**Answer**: "Allows frontend on `localhost:3000` to call API on `localhost:8000`. `allow_credentials=True` enables cookies/auth headers. Production would restrict origins to deployed domain."

---

### Q: Startup event for DB init?

**Answer**: "`@app.on_event('startup')` runs once when server starts. Creates pgvector extension and tables. Idempotent—safe to run multiple times."

---

### Q: API versioning with `/api/v1/`?

**Answer**: "All routes under `/api/v1/`. When breaking changes needed, add `/api/v2/` and run both versions. Clients migrate gradually. Standard REST practice."

---

### Q: Cascading dependencies?

**Answer**: "`get_current_user_dep` depends on `get_db`. FastAPI resolves dependencies in order—creates session, then validates user. Single declaration, multiple dependencies."

---

### Q: HTTPBearer security scheme?

**Answer**: "Extracts `Authorization: Bearer <token>` header automatically. Clients send tokens in standard format. FastAPI generates OpenAPI docs with 'Authorize' button."

---

## Testing

### Q: Test database isolation?

**Answer**: "`scope='function'` creates fresh database per test. Tests don't interfere with each other. SQLite in-memory is fast for testing, Postgres for production."

---

### Q: Dependency override in tests?

**Answer**: "`app.dependency_overrides[get_db]` replaces production DB with test DB. Routes use test database without code changes. FastAPI's dependency injection makes this trivial."

---

### Q: Fixture composition?

**Answer**: "`auth_headers` depends on `client` and `test_user`. Pytest resolves dependencies automatically. Tests just declare `auth_headers` fixture and get authenticated requests."

---

### Q: Integration vs unit tests?

**Answer**: "These are integration tests—they test the full stack (route → service → database). Unit tests would mock the database, but integration tests catch issues like SQL syntax errors."

---

### Q: Test data isolation?

**Answer**: "Each test creates its own notes. `scope='function'` in conftest ensures clean database per test. Tests can run in any order without interference."

---

### Q: Negative tests?

**Answer**: "`test_create_note_without_auth` verifies authentication is enforced. Security tests are as important as feature tests."

---

### Q: Test coverage?

**Answer**: "Tests cover happy path (successful registration/login) and error cases (duplicate email, wrong password). Good tests verify both success and failure modes."

---

### Q: Assertions in tests?

**Answer**: "Check status codes AND response structure. `assert 'access_token' in data` verifies the token exists. `assert 'hashed_password' not in data` ensures passwords never leak."

---

## Deployment & DevOps

### Q: Why Alembic for migrations?

**Answer**: "Alembic tracks schema changes as migration files. Each migration has a revision ID. Upgrading applies migrations in order, downgrading reverts them. Like Git for database schema."

---

### Q: Why migrations vs direct DDL?

**Answer**: "Migrations are reproducible. Team members run `alembic upgrade head` to get the same schema. In production, migrations apply changes without manual SQL scripts."

---

### Q: Docker deployment strategy?

**Answer**: "Multi-stage build: install dependencies, copy code, run uvicorn. Keep image small by using `python:3.12-slim`. Production uses managed Postgres (RDS, DigitalOcean) not containerized DB."

---

### Q: Production environment variables?

**Answer**: "Set `ENVIRONMENT=production`, strong `SECRET_KEY`, `DEBUG=false`, configure `ALLOWED_ORIGINS` for frontend domain. Use managed PostgreSQL for reliability."

---

## Project Presentation

### Q: Walk me through your project architecture

**Answer**: "I built a production-grade RAG application with clean layered architecture. The backend is FastAPI with PostgreSQL + pgvector for vector search. Users can create notes which are automatically embedded using OpenAI. The semantic search uses cosine similarity on embeddings, and the RAG endpoint retrieves relevant notes then generates answers with citations. I focused on production readiness—structured logging, error handling, tests, and graceful degradation when AI services are unavailable."

---

### Q: What was the most challenging part?

**Answer**: "Designing the RAG pipeline to be both accurate and cost-effective. I had to balance retrieval quality (top-k selection), context window limits (token counting), and API costs (batch embeddings). I also implemented graceful degradation so the app remains functional even when OpenAI is down—CRUD operations work independently of AI features."

---

### Q: How would you scale this application?

**Answer**: "Current architecture handles thousands of users. For scale: (1) Add read replicas for database, (2) Implement caching layer (Redis) for frequent queries, (3) Use message queue (Celery) for async embedding generation, (4) Migrate to dedicated vector DB (Pinecone) if search latency becomes critical, (5) Add CDN for static assets, (6) Horizontal scaling with load balancer across multiple uvicorn workers."

---

### Q: What would you add next?

**Answer**: "Priority features: (1) Refresh tokens for better auth UX, (2) Note sharing/collaboration, (3) Evaluation harness to measure retrieval quality (precision@k), (4) Support for file uploads (PDFs, docs), (5) Real-time updates with WebSockets, (6) Admin dashboard for monitoring, (7) Rate limiting to prevent abuse."

---

## End of Interview Prep Guide

**Remember**: 
- Be specific with technical details
- Reference actual code you wrote
- Explain trade-offs and alternatives considered
- Connect to real-world production scenarios
- Show you understand both theory and practice

Good luck with your interviews! 🚀
