# Context-Aware Ranking Algorithm Guide

## 🎯 Overview

The enhanced ranking algorithm is **context-aware** and adapts scoring based on job requirements. It gives appropriate weightage to important factors like education level, domain expertise, and required skills.

---

## ✨ Key Features

### 1. Education Level Weighting

The algorithm now properly weights education levels:

**LinkedIn Scoring (Education Component - 25 points)**:
- PhD: 10 bonus points
- Master's: 7 bonus points
- Bachelor's: 4 bonus points
- High School: 0 bonus points

**Resume Scoring (Education Component - 30 points)**:
- PhD: 30 points
- Master's: 22 points
- Bachelor's: 15 points
- High School: 5 points

**Example**: A candidate with Master's degree gets significantly more points than one with Bachelor's.

---

### 2. Domain Keyword Matching

The algorithm searches for domain-specific keywords across all platforms:

**GitHub (15 points for domain relevance)**:
- Searches repository names, descriptions, and topics
- Example: For "Generative AI" role, looks for: `gan`, `gpt`, `llm`, `transformer`, `diffusion`
- Bonus points for each relevant repository

**LinkedIn (Bonus up to 5 points)**:
- Searches experience descriptions and titles
- Matches domain keywords in work history

**Resume (10 points for domain match)**:
- Searches skills, projects, and certifications
- Calculates match percentage with domain keywords

**Example**: For a Generative AI role, a resume mentioning "GAN", "GPT", "Stable Diffusion" gets higher scores.

---

### 3. Required Skills Matching

**GitHub (10 points)**:
- Matches programming languages with required skills
- Example: If job requires Python, TensorFlow → checks if candidate uses them

**LinkedIn (10 points)**:
- Matches listed skills with required skills
- Combines required_skills + domain_keywords for matching

**Resume (15 points)**:
- Critical component - matches technical skills
- Penalty if doesn't meet minimum requirements

---

### 4. Experience Requirements

**Resume Scoring**:
- Checks if candidate meets minimum experience years
- Bonus points for exceeding requirements
- Penalty for falling short

**LinkedIn Scoring**:
- Validates work experience entries
- Bonus for domain-relevant experience

---

## 📊 Scoring Breakdown (All 0-100)

### GitHub Score (Enhanced)
```
Total: 100 points
├── Repository count: 15 points
├── Stars earned: 25 points
├── Followers: 10 points
├── Language/tech match: 20 points
│   ├── Base diversity: 10 points
│   └── Required skills match: 10 points
├── Project quality: 15 points
└── Domain relevance: 15 points ✨ NEW
    └── Searches repos for domain keywords
```

### LinkedIn Score (Enhanced)
```
Total: 100 points
├── Profile completeness: 25 points
├── Experience: 20 points
│   └── + Bonus for domain-relevant experience ✨ NEW
├── Education: 25 points ✨ ENHANCED
│   ├── Base score: 15 points
│   └── Degree level bonus: 10 points
│       ├── PhD: 10 points
│       ├── Master's: 7 points
│       └── Bachelor's: 4 points
├── Network size: 10 points
└── Skills & domain match: 20 points ✨ ENHANCED
    ├── Base skills: 10 points
    └── Required/domain match: 10 points
```

### Resume Score (Enhanced)
```
Total: 100 points
├── Education level: 30 points ✨ ENHANCED
│   ├── PhD: 30 points
│   ├── Master's: 22 points
│   ├── Bachelor's: 15 points
│   └── Penalty if below minimum
├── Experience: 25 points ✨ ENHANCED
│   └── Checks against min_experience_years
├── Technical skills: 25 points
│   ├── Base count: 10 points
│   └── Required match: 15 points ✨ NEW
├── Domain keywords: 10 points ✨ NEW
│   └── Searches skills, projects, certs
└── Certs & Projects: 10 points
```

---

## 🎛️ Job Requirements Configuration

### JobRequirements Class

```python
from candidate_ranker import JobRequirements

job_reqs = JobRequirements(
    # Required skills (critical for role)
    required_skills=['python', 'tensorflow', 'pytorch'],
    
    # Preferred skills (nice to have)
    preferred_skills=['transformers', 'huggingface'],
    
    # Minimum education level
    min_education="Master's",  # Options: "High School", "Bachelor's", "Master's", "PhD"
    
    # Minimum experience in years
    min_experience_years=2.0,
    
    # Domain-specific keywords
    domain_keywords=['generative ai', 'gan', 'gpt', 'llm', 'diffusion']
)
```

---

## 💼 Role-Specific Examples

### Example 1: Generative AI Engineer

```python
from candidate_ranker import CandidateRanker, ScoringWeights, JobRequirements

# Define requirements
job_reqs = JobRequirements(
    required_skills=['python', 'tensorflow', 'pytorch', 'machine learning'],
    preferred_skills=['transformers', 'huggingface', 'langchain'],
    min_education="Master's",  # AI roles often need advanced degrees
    min_experience_years=2,
    domain_keywords=[
        'generative ai', 'gan', 'gpt', 'llm', 
        'diffusion', 'stable diffusion', 'transformer'
    ]
)

# Weights emphasizing GitHub and Resume
weights = ScoringWeights(
    github_weight=0.35,      # Need to see AI projects
    resume_weight=0.25,      # Education & skills critical
    linkedin_weight=0.15,
    leetcode_weight=0.10,
    company_questions_weight=0.10,
    codeforces_weight=0.05   # Less relevant for AI
)

ranker = CandidateRanker(weights=weights, job_requirements=job_reqs)
scores = ranker.rank_candidates("data/candidates")
```

**What happens**:
- Candidates with Master's/PhD get 7-10 bonus points on LinkedIn
- Candidates with Master's/PhD get 22-30 points on Resume (vs 15 for Bachelor's)
- GitHub repos mentioning "GAN", "GPT", "Stable Diffusion" get up to 15 bonus points
- Resumes with "generative AI" keywords get up to 10 bonus points
- LinkedIn profiles with AI experience get up to 5 bonus points

### Example 2: Backend Engineer

```python
job_reqs = JobRequirements(
    required_skills=['python', 'java', 'sql', 'rest api', 'microservices'],
    preferred_skills=['docker', 'kubernetes', 'aws', 'redis'],
    min_education="Bachelor's",  # Bachelor's sufficient
    min_experience_years=3,
    domain_keywords=['backend', 'api', 'database', 'distributed systems']
)

weights = ScoringWeights(
    leetcode_weight=0.25,    # Algorithms important
    github_weight=0.30,      # Code quality matters
    linkedin_weight=0.15,
    resume_weight=0.15,
    codeforces_weight=0.10,
    company_questions_weight=0.05
)

ranker = CandidateRanker(weights=weights, job_requirements=job_reqs)
```

### Example 3: Fresh Graduate Role

```python
job_reqs = JobRequirements(
    required_skills=['python', 'java', 'data structures'],
    preferred_skills=['react', 'node.js'],
    min_education="Bachelor's",
    min_experience_years=0,  # No experience required
    domain_keywords=['web development', 'full stack']
)

weights = ScoringWeights(
    leetcode_weight=0.30,    # Problem-solving critical
    github_weight=0.25,      # Projects important
    codeforces_weight=0.15,
    resume_weight=0.15,
    linkedin_weight=0.10,
    company_questions_weight=0.05
)
```

---

## 📈 Impact Examples

### Scenario 1: Master's vs Bachelor's

**Candidate A** (Master's in AI):
- LinkedIn Education: 15 (base) + 7 (Master's) = 22/25
- Resume Education: 22/30
- **Total Education Advantage**: ~12 points

**Candidate B** (Bachelor's in CS):
- LinkedIn Education: 15 (base) + 4 (Bachelor's) = 19/25
- Resume Education: 15/30
- **Total**: ~7 points less than Candidate A

### Scenario 2: Domain Expertise

**Job**: Generative AI Engineer

**Candidate A** (Has GAN projects):
- GitHub: +15 points (domain relevance)
- Resume: +10 points (domain keywords)
- LinkedIn: +5 points (AI experience)
- **Total Bonus**: ~30 points

**Candidate B** (No AI experience):
- GitHub: +0 points
- Resume: +0 points
- LinkedIn: +0 points
- **Total**: 30 points behind

### Scenario 3: Required Skills Match

**Job Requires**: Python, TensorFlow, PyTorch

**Candidate A** (Has all 3):
- GitHub: +10 points (language match)
- LinkedIn: +10 points (skills match)
- Resume: +15 points (required skills)
- **Total Bonus**: ~35 points

**Candidate B** (Has only Python):
- GitHub: +3 points (partial match)
- LinkedIn: +3 points (partial match)
- Resume: +5 points (partial match)
- **Total**: 24 points behind

---

## 🎯 Best Practices

### 1. Define Clear Job Requirements

```python
# ✅ Good - Specific and relevant
job_reqs = JobRequirements(
    required_skills=['python', 'tensorflow', 'nlp'],
    domain_keywords=['generative ai', 'llm', 'transformer']
)

# ❌ Bad - Too vague
job_reqs = JobRequirements(
    required_skills=['programming'],
    domain_keywords=['ai']
)
```

### 2. Adjust Weights for Role Type

```python
# For Research/AI roles - emphasize education and projects
weights = ScoringWeights(
    github_weight=0.35,
    resume_weight=0.25,  # Education matters
    ...
)

# For Engineering roles - emphasize coding skills
weights = ScoringWeights(
    leetcode_weight=0.30,
    github_weight=0.30,
    ...
)
```

### 3. Set Realistic Minimums

```python
# For senior roles
job_reqs = JobRequirements(
    min_education="Master's",
    min_experience_years=5
)

# For junior roles
job_reqs = JobRequirements(
    min_education="Bachelor's",
    min_experience_years=0
)
```

---

## 🔍 How to Use

### Step 1: Define Job Requirements

```python
job_reqs = JobRequirements(
    required_skills=['python', 'machine learning'],
    domain_keywords=['computer vision', 'opencv', 'yolo'],
    min_education="Bachelor's",
    min_experience_years=2
)
```

### Step 2: Set Weights

```python
weights = ScoringWeights(
    github_weight=0.30,
    resume_weight=0.20,
    # ... other weights
)
```

### Step 3: Create Ranker

```python
ranker = CandidateRanker(
    weights=weights,
    job_requirements=job_reqs
)
```

### Step 4: Rank Candidates

```python
scores = ranker.rank_candidates("data/candidates")
top_5 = ranker.get_top_candidates(5)
```

---

## 📊 Output Format

Each candidate gets:
- **Total Score**: 0-100 (weighted sum of all platforms)
- **Individual Scores**: 0-100 per platform
- **Weighted Contributions**: How much each platform contributed
- **Strengths**: Platforms scored ≥70
- **Weaknesses**: Platforms scored <50
- **Recommendation**: Based on total score

---

## ✅ Summary

The enhanced algorithm:

1. ✅ **Properly weights education** (PhD > Master's > Bachelor's)
2. ✅ **Matches domain keywords** across GitHub, LinkedIn, Resume
3. ✅ **Validates required skills** with bonus/penalty system
4. ✅ **Checks experience requirements**
5. ✅ **All scores normalized to 0-100**
6. ✅ **Customizable per role type**
7. ✅ **Context-aware and adaptive**

**Result**: More accurate, fair, and relevant candidate rankings based on actual job requirements.
