# Filter - Candidate Ranking Platform

## Contributors:
Mohammed Yaseen
Mohammed Junaid Adil
Eshwar

An intelligent job matching system that evaluates candidates across multiple platforms using an adaptive scoring algorithm with confidence-based ranking.

## Overview

Filter aggregates candidate data from 6 different sources (GitHub, LeetCode, Codeforces, LinkedIn, Resume, and custom assessments) to create comprehensive profiles and rank candidates fairly, even with incomplete data.

## Key Features

- **Multi-Platform Aggregation**: Collects data from GitHub, LeetCode, Codeforces, LinkedIn, resumes, and custom questions
- **Adaptive Ranking Algorithm**: Fairly evaluates candidates with varying data completeness using dynamic weight redistribution
- **Confidence-Based Scoring**: Provides confidence intervals (±3 to ±12 points) showing score reliability
- **Compensatory Mechanisms**: Allows strengths in one area to offset weaknesses in another
- **AI-Powered Embeddings**: Uses BGE-small-en-v1.5 model for semantic matching between candidates and jobs
- **Real-Time Processing**: Instant candidate evaluation and ranking

## Tech Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: Python Flask
- **ML Model**: BAAI/bge-small-en-v1.5 (384-dimensional embeddings)
- **PDF Processing**: pdf-parse, pdfjs-dist
- **Data Storage**: JSON-based file system

## Prerequisites

- Node.js 22.11+
- Python 3.8+
- npm or yarn

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd filter
```

### 2. Frontend Setup
```bash
npm install
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application

You need to run TWO services simultaneously:

### Terminal 1 - Frontend (Vite Dev Server)
```bash
npm run dev
```
Runs at: http://localhost:5173

### Terminal 2 - Backend (Python Flask)
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
python app.py
```
Runs at: http://localhost:5000

## Usage

### For Job Seekers

1. Navigate to the Job Seeker Dashboard
2. Upload your PDF resume
3. System auto-parses and extracts:
   - Personal information
   - Education history
   - Work experience
   - Skills and certifications
4. Add optional platform profiles (GitHub, LeetCode, etc.)
5. Click "Save Profile & Generate Embedding"
6. Profile saved to `data/candidates/username/`

### For Companies

1. Navigate to the Company Dashboard
2. Fill out job posting form:
   - Job title and description
   - Required skills
   - Minimum education
   - Experience requirements
3. Click "Post Job & Rank Candidates"
4. View ranked candidates with:
   - Final scores (0-100)
   - Confidence levels
   - Confidence intervals
   - Strengths and weaknesses
   - Recommendations

## Project Structure

```
filter/
├── src/                          # Frontend React app
│   ├── components/
│   │   ├── CompanyDashboard.tsx  # Company interface
│   │   └── JobSeekerDashboard.tsx # Job seeker interface
│   └── utils/
│       └── pdfParser.ts          # PDF parsing utilities
├── backend/                      # Python backend
│   ├── app.py                    # Flask server
│   ├── services/
│   │   ├── adaptive_ranker.py    # Adaptive ranking algorithm
│   │   ├── candidate_ranker.py   # Standard ranking
│   │   ├── resume_parser.py      # Resume parsing
│   │   ├── scraper.py            # Platform data scraping
│   │   └── company_questions.py  # Assessment handling
│   ├── utils/
│   │   └── candidate_manager.py  # Candidate data management
│   └── scripts/
│       ├── batch_candidate_processor.py
│       ├── complete_candidate_evaluation.py
│       └── view_candidates.py
├── data/                         # Data storage
│   ├── candidates/               # Candidate profiles
│   │   └── username/
│   │       ├── resume.json
│   │       ├── embedding.json
│   │       ├── github.json
│   │       ├── leetcode.json
│   │       ├── linkedin.json
│   │       └── metadata.json
│   └── jobs/                     # Job postings
│       └── job_id/
│           ├── job.json
│           └── embedding.json
└── scripts/
    └── extractResume.js          # Resume extraction utility
```

## Adaptive Ranking Algorithm

The system uses a sophisticated two-level adaptive ranking algorithm:

### How It Works

1. **Attribute-Level Scoring**: Evaluates 29 individual attributes across all platforms
2. **Dynamic Weight Redistribution**: Redistributes weights from missing platforms to available ones
3. **Confidence Calculation**: Applies confidence multiplier (70%-100%) based on data completeness
4. **Compensatory Bonuses**: Rewards strong performance in one area compensating for weaknesses
5. **Final Score**: Combines all factors with bonuses/penalties for a 0-100 score

### Confidence Levels

- **High** (5-6 platforms): ±3 points margin
- **Good** (3-4 platforms): ±5 points margin
- **Moderate** (2 platforms): ±8 points margin
- **Low** (1 platform): ±12 points margin

### Platform Weights (Default)

- GitHub: 25%
- LeetCode: 20%
- Codeforces: 15%
- LinkedIn: 15%
- Resume: 15%
- Company Questions: 10%

For detailed algorithm explanation, see [ALGORITHM_EXPLAINED.md](ALGORITHM_EXPLAINED.md) and [ADAPTIVE_RANKING_SUMMARY.md](ADAPTIVE_RANKING_SUMMARY.md).

## API Endpoints

### Backend (Flask - Port 5000)

#### Health Check
```
GET /health
```

#### Generate Embedding
```
POST /api/embed
Body: { "text": "your text here" }
```

#### Embed Resume
```
POST /api/embed-resume
Body: {
  "username": "john_doe",
  "resume_data": { ... }
}
```

#### Embed Job
```
POST /api/embed-job
Body: {
  "job_id": "job_123",
  "job_data": { ... }
}
```

#### Rank Candidates
```
POST /api/rank-candidates
Body: {
  "job_requirements": {
    "required_skills": ["python", "javascript"],
    "min_education": "Bachelor's",
    "min_experience": 2
  }
}
```

## Scripts

### Extract Resume Data
```bash
npm run extract-resume
```

### View All Candidates
```bash
cd backend
python scripts/view_candidates.py
```

### Batch Process Candidates
```bash
cd backend
python scripts/batch_candidate_processor.py
```

### Complete Candidate Evaluation
```bash
cd backend
python scripts/complete_candidate_evaluation.py
```

## Data Format

### Candidate Profile
```json
{
  "username": "john_doe",
  "resume": { ... },
  "github": { ... },
  "leetcode": { ... },
  "codeforces": { ... },
  "linkedin": { ... },
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Job Posting
```json
{
  "job_id": "job_123",
  "title": "Senior Software Engineer",
  "description": "...",
  "required_skills": ["python", "javascript"],
  "min_education": "Bachelor's",
  "min_experience": 3,
  "embedding": [0.789, -0.012, ...]
}
```

## Configuration

### Adjust Ranking Weights

Edit `backend/services/adaptive_ranker.py`:

```python
weights = ScoringWeights(
    github=0.25,
    leetcode=0.20,
    codeforces=0.15,
    linkedin=0.15,
    resume=0.15,
    company_questions=0.10
)
```

### Customize Confidence Formula

Edit confidence calculation in `adaptive_ranker.py`:

```python
confidence = 0.70 + (0.30 * completeness)
```

## Development

### Run Linter
```bash
npm run lint
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```




