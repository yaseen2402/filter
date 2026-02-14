# Complete Candidate Evaluation System - User Guide

## 🎯 System Overview

End-to-end system for evaluating and ranking job candidates:

1. **Profile Scraping**: Codeforces, LeetCode, LinkedIn, GitHub
2. **Resume Analysis**: Parse and score resumes (PDF, DOCX, TXT)
3. **Company Questions**: Scenario-based and technical assessments
4. **Multi-Criteria Ranking**: Weighted scoring for shortlisting

---

## 📦 Installation

```bash
pip install -r requirements.txt
pip install PyPDF2 python-docx  # For resume parsing
```

Create `.env`:
```
SCRAPINGDOG_API_KEY=699006af21e8dd0abecd41fa
GITHUB_TOKEN=your_token  # Optional
```

---

## 🚀 Quick Start

### Single Candidate

```python
from complete_candidate_evaluation import CompleteCandidateEvaluator

evaluator = CompleteCandidateEvaluator()

evaluator.process_candidate(
    candidate_name="John Doe",
    profile_urls={
        'codeforces': 'https://codeforces.com/profile/johndoe',
        'leetcode': 'https://leetcode.com/u/johndoe/',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'github': 'https://github.com/johndoe'
    },
    resume_file="resumes/john_doe.pdf"
)

top_5 = evaluator.rank_all_candidates(top_n=5)
```

### Batch Processing

```python
evaluator.batch_process_from_csv("candidates.csv", resume_folder="resumes")
evaluator.rank_all_candidates(top_n=5)
```

---

## 📋 Modules

### 1. Resume Parser (`resume_parser.py`)

Extracts: education, experience, skills, certifications, projects
Scores: 0-100 based on education (25%), experience (25%), skills (25%), certs/projects (15%), job match (10%)

### 2. Company Questions (`company_questions.py`)

Question types: Multiple choice, coding, scenario, behavioral
Creates assessments, evaluates answers, calculates scores

### 3. Ranking Algorithm (`candidate_ranker.py`)

Default weights: GitHub 25%, LeetCode 20%, Codeforces 15%, LinkedIn 15%, Resume 15%, Questions 10%

---

## 📁 Data Structure

```
data/candidates/
  ├── John_Doe/
  │   ├── metadata.json
  │   ├── codeforces.json
  │   ├── leetcode.json
  │   ├── linkedin.json
  │   ├── github.json
  │   ├── resume_analysis.json
  │   └── company_questions.json
  └── ranking_report.json
```

---

## 🎛️ Customization

```python
from candidate_ranker import ScoringWeights

weights = ScoringWeights(
    github_weight=0.30,
    leetcode_weight=0.25,
    resume_weight=0.20,
    # ... adjust as needed
)

evaluator = CompleteCandidateEvaluator(
    job_requirements={
        'required_skills': ['python', 'java'],
        'min_experience': 2
    },
    ranking_weights=weights
)
```

---

## 📊 Ranking Categories

- 80-100: Highly Recommended
- 70-79: Recommended
- 60-69: Consider
- 50-59: Marginal
- 0-49: Not Recommended

---

## 🔧 Command Line Tools

```bash
python view_candidates.py          # View candidates
python candidate_ranker.py         # Rank candidates
python complete_candidate_evaluation.py  # Interactive menu
```

---

## 📝 Complete Workflow

1. Collect candidate data (CSV + resumes)
2. Process: `evaluator.batch_process_from_csv()`
3. Conduct assessments (save to company_questions.json)
4. Rank: `evaluator.rank_all_candidates()`
5. Review ranking_report.json and select top candidates
