# Setup Guide

## Prerequisites
- Node.js 22.11+
- Python 3.8+

## Installation

### 1. Frontend Setup
```bash
npm install
```

### 2. Embedding Service Setup
```bash
cd embedding-service
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application

You need to run TWO services:

### Terminal 1 - Frontend (Vite)
```bash
npm run dev
```
Runs at: http://localhost:5173

### Terminal 2 - Embedding Service (Python)
```bash
cd embedding-service
venv\Scripts\activate
python app.py
```
Runs at: http://localhost:5000

## How It Works

### Job Seeker Flow:
1. Upload PDF resume
2. Auto-parses and extracts data
3. Click "Save Profile & Generate Embedding"
4. Saves to data/candidates/username/

### Company Flow:
1. Fill job posting form
2. Click "Post Job"
3. Saves to data/jobs/job_id/

## Data Structure
```
data/
  candidates/
    username/
      resume.json
      embedding.json
  jobs/
    job_id/
      job.json
      embedding.json
```
