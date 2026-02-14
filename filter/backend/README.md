# Embedding Service

Lightweight Python backend for generating embeddings using BGE-small-en-v1.5.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate it:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Server runs at: http://localhost:5000

## Endpoints

### Health Check
```
GET /health
```

### Generate Embedding (generic)
```
POST /api/embed
Body: { "text": "your text here" }
```

### Embed Resume
```
POST /api/embed-resume
Body: {
  "username": "john_doe",
  "resume_data": { ... }
}
```
Saves to: `data/candidates/username/embedding.json`

### Embed Job
```
POST /api/embed-job
Body: {
  "job_id": "job_123",
  "job_data": { ... }
}
```
Saves to: `data/jobs/job_id/embedding.json`

## Model Info

- Model: BAAI/bge-small-en-v1.5
- Dimension: 384
- Normalized embeddings for cosine similarity
