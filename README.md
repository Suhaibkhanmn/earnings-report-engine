# Earnings Call Intelligence Engine

A production-ready system that ingests earnings call transcripts, performs semantic search using RAG (Retrieval-Augmented Generation), and generates structured, evidence-backed comparison reports between quarters.

## Features

- **Document Ingestion**: Upload earnings call transcripts with automatic chunking
- **Vector Search**: Semantic search using Google Gemini embeddings and pgvector
- **Structured Reports**: Generate JSON reports comparing quarters with evidence quotes
- **Evidence Validation**: Every claim includes citations (document_id, chunk_id)
- **Quality Evaluation**: Automated validation of report quality (evidence coverage, citations)
- **Minimal UI**: Clean, professional frontend for viewing reports

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL with pgvector
- **LLM**: Google Gemini (gemini-2.5-flash for generation, text-embedding-004 for embeddings)
- **Frontend**: Next.js 14, React, TypeScript
- **Database**: Neon PostgreSQL (or any Postgres with pgvector)

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database with pgvector extension (Neon recommended)
- Google AI Studio API key

### Backend Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Create `.env` in the project root:
   ```env
   DATABASE_URL=postgresql+psycopg://user:password@host/database
   GEMINI_API_KEY=your-google-ai-studio-api-key
   ENVIRONMENT=development
   ```

3. **Initialize database**:
   ```bash
   python scripts/init_db.py
   ```

4. **Start the server**:
   ```bash
   python -m uvicorn backend.app.main:app --reload --port 8001
   ```

   API will be available at `http://localhost:8001`
   Interactive docs at `http://localhost:8001/docs`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL**:
   Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8001
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

## API Documentation

### Health Check

#### `GET /health`
Check if the API is running.

**Response**:
```json
{
  "status": "ok"
}
```

---

### Document Ingestion

#### `POST /ingest`
Upload a transcript as JSON.

**Request Body**:
```json
{
  "ticker": "GOOG",
  "quarter": "2025_Q3",
  "call_date": "2025-01-20T00:00:00",
  "raw_text": "Full transcript text here..."
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "ticker": "GOOG",
  "quarter": "2025_Q3",
  "call_date": "2025-01-20T00:00:00",
  "created_at": "2025-01-20T18:00:00Z"
}
```

**Notes**:
- Automatically creates chunks for the document
- Returns 409 Conflict if document with same (ticker, quarter) already exists

---

#### `POST /ingest/file`
Upload a transcript as a file.

**Request** (multipart/form-data):
- `ticker`: string (required)
- `quarter`: string (required)
- `call_date`: date string (optional, format: YYYY-MM-DD)
- `file`: text file (required, UTF-8 encoded)

**Example** (curl):
```bash
curl -X POST http://localhost:8001/ingest/file \
  -F "ticker=GOOG" \
  -F "quarter=2025_Q3" \
  -F "call_date=2025-01-20" \
  -F "file=@data/raw_transcripts/GOOG_2025_Q3.txt"
```

**Response** (201 Created):
Same as `POST /ingest`

---

#### `GET /documents`
List all ingested documents.

**Response**:
```json
[
  {
    "id": "uuid",
    "ticker": "GOOG",
    "quarter": "2025_Q3",
    "call_date": "2025-01-20T00:00:00",
    "created_at": "2025-01-20T18:00:00Z"
  }
]
```

---

#### `GET /documents/{document_id}`
Get full document details including raw text.

**Response**:
```json
{
  "id": "uuid",
  "ticker": "GOOG",
  "quarter": "2025_Q3",
  "call_date": "2025-01-20T00:00:00",
  "created_at": "2025-01-20T18:00:00Z",
  "raw_text": "Full transcript text..."
}
```

---

#### `GET /documents/{document_id}/chunks`
List all chunks for a document.

**Response**:
```json
[
  {
    "id": "uuid",
    "document_id": "uuid",
    "chunk_index": 0,
    "section": "prepared_remarks",
    "speaker": null,
    "text": "Chunk text...",
    "created_at": "2025-01-20T18:00:00Z"
  }
]
```

---

### RAG (Retrieval-Augmented Generation)

#### `POST /rag/documents/{document_id}/embed`
Generate embeddings for all chunks of a document.

**Response**:
```json
{
  "document_id": "uuid",
  "chunks_embedded": 58,
  "total_chunks": 58
}
```

**Notes**:
- Automatically creates chunks if they don't exist
- Uses Google Gemini `text-embedding-004` model
- Processes in batches of 32

---

#### `POST /rag/search`
Perform semantic search across embedded chunks.

**Request Body**:
```json
{
  "query": "capex guidance",
  "k": 8,
  "document_id": "uuid"
}
```

**Parameters**:
- `query`: Search query string (required)
- `k`: Number of results to return (default: 8)
- `document_id`: Optional, filter by document

**Response**:
```json
{
  "query": "capex guidance",
  "k": 8,
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "chunk_index": 28,
      "section": "prepared_remarks",
      "speaker": null,
      "text": "We now expect CapEx to be in the range of $91 billion to $93 billion..."
    }
  ]
}
```

---

### Report Generation

#### `POST /report`
Generate a structured comparison report between quarters.

**Request Body**:
```json
{
  "ticker": "GOOG",
  "quarter": "2025_Q3",
  "prev_quarter": "2025_Q2"
}
```

**Parameters**:
- `ticker`: Stock ticker symbol (required)
- `quarter`: Current quarter identifier, e.g., "2025_Q3" (required)
- `prev_quarter`: Previous quarter for comparison (optional)

**Response**:
```json
{
  "data": {
    "ticker": "GOOG",
    "quarter": "2025_Q3",
    "prev_quarter": "2025_Q2",
    "summary": {
      "high_level": "Alphabet delivered strong Q3 results...",
      "tone": "positive"
    },
    "guidance": [
      {
        "claim": "CapEx guidance raised to $91-93B",
        "direction_vs_prev": "up",
        "evidence_current": "We now expect CapEx... (document_id: abc, chunk_id: xyz, chunk_index: 28)",
        "evidence_prev": "previous estimate of $85 billion..."
      }
    ],
    "growth_drivers": [...],
    "risks": [...],
    "margin_dynamics": [...],
    "qa_pressure_points": [...]
  }
}
```

**Notes**:
- Reports are cached in the database
- Same (ticker, quarter, prev_quarter) returns cached result
- Uses Gemini 2.5 Flash for generation
- All evidence quotes include citations

---

#### `GET /report/health`
Health check for report service.

**Response**:
```json
{
  "status": "ok"
}
```

---

### Evaluation

#### `POST /evaluation/report`
Generate a report with quality evaluation metrics.

**Request Body**:
Same as `POST /report`

**Response**:
```json
{
  "evaluation": {
    "is_valid": true,
    "structure_errors": [],
    "evidence_coverage": {
      "total_claims": 18,
      "claims_with_evidence": 18,
      "claims_without_evidence": 0,
      "evidence_coverage_rate": 1.0,
      "details": []
    },
    "citation_quality": {
      "total_evidence_fields": 27,
      "evidence_with_citations": 27,
      "evidence_without_citations": 0,
      "citation_rate": 1.0
    },
    "overall_score": 1.0,
    "recommendations": []
  },
  "report_data": {
    // Full report JSON (same as POST /report)
  }
}
```

**Evaluation Metrics**:
- `overall_score`: 0.0 to 1.0 (100% = perfect)
- `evidence_coverage_rate`: % of claims with evidence quotes
- `citation_rate`: % of evidence fields with document/chunk citations
- `recommendations`: List of improvement suggestions

---

## Usage Examples

### Complete Workflow

1. **Ingest a transcript**:
   ```bash
   curl -X POST http://localhost:8001/ingest/file \
     -F "ticker=GOOG" \
     -F "quarter=2025_Q3" \
     -F "file=@data/raw_transcripts/GOOG_2025_Q3.txt"
   ```

2. **Embed the document**:
   ```bash
   curl -X POST http://localhost:8001/rag/documents/{document_id}/embed
   ```

3. **Generate a report**:
   ```bash
   curl -X POST http://localhost:8001/report \
     -H "Content-Type: application/json" \
     -d '{"ticker": "GOOG", "quarter": "2025_Q3", "prev_quarter": "2025_Q2"}'
   ```

4. **Evaluate report quality**:
   ```bash
   curl -X POST http://localhost:8001/evaluation/report \
     -H "Content-Type: application/json" \
     -d '{"ticker": "GOOG", "quarter": "2025_Q3", "prev_quarter": "2025_Q2"}'
   ```

### Using Python Scripts

```bash
# Test report generation
python scripts/test_report.py

# Evaluate a report
python scripts/evaluate_report.py GOOG 2025_Q3 2025_Q2

# Embed a document
python scripts/embed_document.py {document_id}
```

---

## Architecture

### Data Flow

1. **Ingestion**: Transcript → Document → Chunks
2. **Embedding**: Chunks → Gemini Embeddings → pgvector
3. **Retrieval**: Query → Embed Query → Vector Search → Top-K Chunks
4. **Generation**: Chunks + Prompt → Gemini → Structured JSON Report
5. **Validation**: Report → Quality Metrics → Evaluation Score

### Database Schema

- **documents**: Stores raw transcripts
- **chunks**: Text chunks with embeddings (pgvector)
- **reports**: Cached generated reports

### Key Components

- `backend/app/ingestion/`: Chunking and parsing logic
- `backend/app/rag/`: Embeddings, vector search, retrieval
- `backend/app/llm/`: Report generation and validation
- `backend/app/api/`: FastAPI route handlers
- `frontend/`: Next.js UI

---

## Report Schema

Reports follow this structure:

```json
{
  "ticker": "string",
  "quarter": "string",
  "prev_quarter": "string | null",
  "summary": {
    "high_level": "string",
    "tone": "neutral | positive | negative"
  },
  "guidance": [
    {
      "claim": "string",
      "direction_vs_prev": "up | down | flat | unknown",
      "evidence_current": "string (with citations)",
      "evidence_prev": "string (with citations)"
    }
  ],
  "growth_drivers": [
    {
      "claim": "string",
      "evidence": "string (with citations)"
    }
  ],
  "risks": [
    {
      "claim": "string",
      "is_new": boolean,
      "evidence_first_mention": "string | null",
      "evidence_current": "string (with citations)"
    }
  ],
  "margin_dynamics": [
    {
      "claim": "string",
      "evidence": "string (with citations)"
    }
  ],
  "qa_pressure_points": [
    {
      "theme": "string",
      "analyst_name": "string | null",
      "evidence_question": "string (with citations)",
      "evidence_answer": "string (with citations)"
    }
  ]
}
```

---

## Error Handling

### Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Document created
- `404 Not Found`: Document/quarter not found
- `409 Conflict`: Document with same (ticker, quarter) already exists
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error (check logs)

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (use `postgresql+psycopg://` prefix) | Yes |
| `GEMINI_API_KEY` | Google AI Studio API key | Yes |
| `ENVIRONMENT` | `development` or `production` | No (default: development) |

---

## Development

### Running Tests

```bash
# Test embedding
python scripts/test_gemini_embed.py

# Test report generation
python scripts/test_report.py

# Test validation
python scripts/test_validation.py
```

### Database Management

```bash
# Initialize tables
python scripts/init_db.py

# View cached reports (SQL)
SELECT ticker, quarter, prev_quarter, created_at FROM reports;
```

---

## Production Deployment

### Backend (FastAPI)

Recommended platforms:
- **Render**: Free tier available, easy PostgreSQL integration
- **Railway**: Simple deployment, auto-detects FastAPI
- **Fly.io**: Good for containerized apps

**Environment variables** to set:
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `ENVIRONMENT=production`

### Frontend (Next.js)

Recommended platforms:
- **Vercel**: Free tier, zero-config Next.js deployment
- **Netlify**: Alternative with good Next.js support

**Environment variables** to set:
- `NEXT_PUBLIC_API_URL` (your deployed backend URL)

### Database

- **Neon**: Serverless Postgres with pgvector support (recommended)
- **Supabase**: Alternative with pgvector
- **Self-hosted**: Any Postgres 12+ with pgvector extension

---

## License

MIT

---

## Contributing

This is a portfolio project. For questions or improvements, open an issue or submit a PR.
