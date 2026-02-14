# Complete Algorithm Explanation

## 🎯 Overview

This is a **two-level adaptive ranking algorithm** that evaluates candidates across multiple platforms and handles incomplete data fairly.

---

## 📐 The Complete Formula

### Level 1: Attribute-Level Scoring (Within Each Platform)

Each platform score is calculated from multiple weighted attributes:

```
Platform_Score = Σ (Attribute_Value × Attribute_Weight)

Example - GitHub Score (0-100):
  = (Repos × 0.15) + (Stars × 0.25) + (Followers × 0.10) + 
    (Languages × 0.10) + (Skills_Match × 0.10) + 
    (Quality × 0.15) + (Domain_Relevance × 0.15)
```

### Level 2: Platform-Level Scoring (Combining All Platforms)

```
Base_Score = Σ (Platform_Score × Platform_Weight)

Example with all 6 platforms:
  = (GitHub × 0.25) + (LeetCode × 0.20) + (Codeforces × 0.15) + 
    (LinkedIn × 0.15) + (Resume × 0.15) + (Questions × 0.10)
```

### Level 3: Adaptive Adjustments (For Incomplete Data)

```
Step 1: Identify Available Platforms
  available = [platforms with data]
  missing = [platforms without data]

Step 2: Redistribute Weights Dynamically
  total_available_weight = Σ original_weight[i] for i in available
  
  for each available platform i:
    adjusted_weight[i] = original_weight[i] / total_available_weight

Step 3: Calculate Confidence
  completeness = len(available) / 6
  confidence = 0.70 + (0.30 × completeness)
  
  Examples:
    1/6 platforms: 0.70 + 0.30×(1/6) = 0.75 (75%)
    3/6 platforms: 0.70 + 0.30×(3/6) = 0.85 (85%)
    6/6 platforms: 0.70 + 0.30×(6/6) = 1.00 (100%)

Step 4: Apply Confidence Adjustment
  confidence_adjusted_score = base_score × confidence

Step 5: Apply Bonuses
  bonus = 0
  if has_resume: bonus += 5
  if has_github AND has_coding_platform: bonus += 3
  if has_resume AND has_linkedin: bonus += 2

Step 6: Apply Compensatory Bonuses
  comp_bonus = 0
  
  if github_score > 70:
    if leetcode missing OR leetcode_score < 50: comp_bonus += 5
    if codeforces missing OR codeforces_score < 50: comp_bonus += 3
  
  if resume_score > 70 AND linkedin missing: comp_bonus += 3
  
  if avg_coding_score > 70 AND github_score < 50: comp_bonus += 4

Step 7: Apply Penalties
  penalty = 0
  if len(available) < 2: penalty += 10
  if resume missing AND github missing: penalty += 5

Step 8: Calculate Final Score
  final_score = confidence_adjusted_score + bonus + comp_bonus - penalty
  final_score = min(100, max(0, final_score))

Step 9: Calculate Confidence Interval
  margin = {High: ±3, Good: ±5, Moderate: ±8, Low: ±12}
  interval = [final_score - margin, final_score + margin]
```

---

## 🔢 Detailed Attribute Scoring

### 1. GitHub Score (0-100)

**7 Attributes:**

```python
# 1. Repository Count (0-15 points)
repos_score = min(15, (repos / 50) × 15)
# 50 repos = max points

# 2. Stars Earned (0-25 points) - Tiered
if stars >= 1000: stars_score = 25
elif stars >= 500: stars_score = 22
elif stars >= 100: stars_score = 18
elif stars >= 50: stars_score = 14
elif stars >= 10: stars_score = 10
elif stars >= 1: stars_score = 5
else: stars_score = 0

# 3. Followers (0-10 points)
followers_score = min(10, (followers / 100) × 10)
# 100 followers = max points

# 4. Language Diversity (0-10 points)
languages_score = min(10, (num_languages / 5) × 10)
# 5 languages = max points

# 5. Required Skills Match (0-10 points)
skills_match_score = (matched_skills / required_skills) × 10
# Example: 2/2 skills matched = 10 points

# 6. Project Quality (0-15 points)
quality_score = (quality_repos / total_repos) × 15
# Quality = has description AND (stars > 0 OR topics)

# 7. Domain Relevance (0-15 points)
domain_score = 0
for repo in top_repos:
    if domain_keywords in (repo.name OR repo.description OR repo.topics):
        domain_score += min(5, matches × 2)  # Up to 5 per repo
domain_score = min(15, domain_score)

# Total GitHub Score
github_score = repos_score + stars_score + followers_score + 
               languages_score + skills_match_score + 
               quality_score + domain_score
```

### 2. LeetCode Score (0-100)

**4 Attributes:**

```python
# 1. Total Problems Solved (0-50 points)
solved_score = min(50, (total_solved / 500) × 50)
# 500 problems = max points

# 2. Difficulty Distribution (0-30 points)
weighted_difficulty = (easy×1 + medium×2 + hard×3) / 6
difficulty_score = min(30, (weighted_difficulty / 200) × 30)
# Rewards harder problems more

# 3. Acceptance Rate (0-10 points)
acceptance_score = (acceptance_rate / 100) × 10

# 4. Ranking (0-10 points) - Tiered
if ranking < 100000: ranking_score = 10
elif ranking < 500000: ranking_score = 7
elif ranking < 1000000: ranking_score = 5
elif ranking < 2000000: ranking_score = 3
else: ranking_score = 0

# Total LeetCode Score
leetcode_score = solved_score + difficulty_score + 
                 acceptance_score + ranking_score
```

### 3. Codeforces Score (0-100)

**4 Attributes:**

```python
# 1. Current Rating (0-40 points)
rating_score = min(40, (rating / 3500) × 40)
# 3500 = Legendary Grandmaster threshold

# 2. Contests Participated (0-30 points)
contests_score = min(30, (contests / 100) × 30)
# 100 contests = max points

# 3. Rank Tier (0-20 points) - Tiered
rank_scores = {
    "legendary grandmaster": 20,
    "international grandmaster": 18,
    "grandmaster": 16,
    "international master": 14,
    "master": 12,
    "candidate master": 10,
    "expert": 8,
    "specialist": 6,
    "pupil": 4,
    "newbie": 2
}
rank_score = rank_scores.get(rank.lower(), 0)

# 4. Contribution (0-10 points)
contribution_score = min(10, max(0, contribution / 10))

# Total Codeforces Score
codeforces_score = rating_score + contests_score + 
                   rank_score + contribution_score
```

### 4. LinkedIn Score (0-100)

**5 Attributes:**

```python
# 1. Profile Completeness (0-25 points)
completeness = 0
if has_name: completeness += 4
if has_headline: completeness += 5
if has_summary: completeness += 5
if has_location: completeness += 3
if has_photo: completeness += 3
if has_experience: completeness += 5

# 2. Experience (0-20 points + 5 bonus)
base_exp_score = min(20, (valid_experiences / 3) × 20)
# 3 experiences = max base points

# Domain bonus (0-5 points)
domain_bonus = 0
if domain_keywords in experience_descriptions:
    domain_bonus = min(5, matches × 2)

experience_score = base_exp_score + domain_bonus

# 3. Education (0-25 points)
base_edu_score = min(15, (valid_education / 2) × 15)
# 2 education entries = max base

# Degree level bonus (0-10 points)
if "phd" in education_text: degree_bonus = 10
elif "master" in education_text: degree_bonus = 7
elif "bachelor" in education_text: degree_bonus = 4
else: degree_bonus = 0

education_score = base_edu_score + degree_bonus

# 4. Network Size (0-10 points) - Tiered
if connections >= 500: network_score = 10
elif connections >= 200: network_score = 8
elif connections >= 100: network_score = 6
elif connections >= 50: network_score = 4
else: network_score = 2

# 5. Skills & Domain Match (0-20 points)
base_skills_score = min(10, (skill_count / 10) × 10)
# 10 skills = max base

# Required/domain match (0-10 points)
match_score = (matched_skills / total_required) × 10

skills_score = base_skills_score + match_score

# Total LinkedIn Score
linkedin_score = completeness + experience_score + 
                 education_score + network_score + skills_score
```

### 5. Resume Score (0-100)

**6 Attributes:**

```python
# 1. Education Level (0-30 points) - Tiered
education_scores = {
    "PhD": 30,
    "Master's": 22,
    "Bachelor's": 15,
    "High School": 5,
    "Unknown": 0
}
education_score = education_scores.get(education_level, 0)

# Check minimum requirement
if candidate_education < required_education:
    education_score -= 10  # Penalty

# 2. Experience Years (0-25 points)
if experience >= min_required:
    if experience >= 10: exp_score = 25
    elif experience >= 5: exp_score = 22
    elif experience >= 3: exp_score = 18
    elif experience >= 1: exp_score = 15
    else: exp_score = 12
else:
    exp_score = min(10, experience × 3)  # Below requirement

# 3. Technical Skills Count (0-10 points)
skills_count_score = min(10, (skill_count / 10) × 10)

# 4. Required Skills Match (0-15 points) - Critical
required_match_score = (matched_skills / required_skills) × 15

# 5. Domain Keywords (0-10 points)
# Searches skills, projects, certifications
domain_match_score = (matched_keywords / total_keywords) × 10

# 6. Certifications & Projects (0-10 points)
certs_score = min(5, cert_count × 1.5)
projects_score = min(5, project_count × 1)
extras_score = certs_score + projects_score

# Total Resume Score
resume_score = education_score + exp_score + 
               skills_count_score + required_match_score + 
               domain_match_score + extras_score
```

### 6. Company Questions Score (0-100)

**1 Attribute:**

```python
# Assessment Score (0-100 points)
questions_score = (points_earned / total_points) × 100

# Different question types:
# - Multiple Choice: Auto-graded (exact match)
# - Coding: Test cases (pass_rate × points)
# - Scenario/Behavioral: Manual evaluation (default 50%)
```

---

## 🎯 Complete Example Calculation

### Candidate Profile

```
GitHub:
  - Repos: 30
  - Stars: 150
  - Followers: 50
  - Languages: 3 (Python, JavaScript, TypeScript)
  - Required skills: 2/2 matched (Python, JavaScript)
  - Quality repos: 20/30
  - Domain repos: 2 with ML keywords

LeetCode:
  - Solved: 250
  - Easy: 100, Medium: 80, Hard: 70
  - Acceptance: 75%
  - Ranking: 50,000

Resume:
  - Education: Master's
  - Experience: 3 years
  - Skills: 8 total, 3/3 required matched
  - Domain: 2/3 keywords matched
  - Certs: 2, Projects: 3

Only 3/6 platforms available (GitHub, LeetCode, Resume)
```

### Step-by-Step Calculation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Calculate Attribute Scores
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GitHub (100 pts total):
  ├─ Repos: (30/50) × 15 = 9.0
  ├─ Stars: 18.0 (100-499 tier)
  ├─ Followers: (50/100) × 10 = 5.0
  ├─ Languages: (3/5) × 10 = 6.0
  ├─ Skills Match: (2/2) × 10 = 10.0
  ├─ Quality: (20/30) × 15 = 10.0
  └─ Domain: 2 repos × 5 = 10.0
  TOTAL: 68.0/100

LeetCode (100 pts total):
  ├─ Solved: (250/500) × 50 = 25.0
  ├─ Difficulty: (100 + 160 + 210)/6/200 × 30 = 11.75
  ├─ Acceptance: (75/100) × 10 = 7.5
  └─ Ranking: 10.0 (<100K)
  TOTAL: 54.25/100

Resume (100 pts total):
  ├─ Education: 22.0 (Master's)
  ├─ Experience: 18.0 (3 years, meets requirement)
  ├─ Skills Count: (8/10) × 10 = 8.0
  ├─ Required Match: (3/3) × 15 = 15.0
  ├─ Domain: (2/3) × 10 = 6.67
  └─ Certs/Projects: 3.0 + 3.0 = 6.0
  TOTAL: 75.67/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: Redistribute Weights (Only 3/6 platforms available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Original Weights:
  GitHub: 0.25
  LeetCode: 0.20
  Resume: 0.15
  (Missing: Codeforces, LinkedIn, Questions)

Total Available Weight: 0.25 + 0.20 + 0.15 = 0.60

Adjusted Weights:
  GitHub: 0.25 / 0.60 = 0.417 (41.7%)
  LeetCode: 0.20 / 0.60 = 0.333 (33.3%)
  Resume: 0.15 / 0.60 = 0.250 (25.0%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Calculate Base Score
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Base Score = Σ (Platform_Score × Adjusted_Weight)

  = (68.0 × 0.417) + (54.25 × 0.333) + (75.67 × 0.250)
  = 28.36 + 18.07 + 18.92
  = 65.35/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4: Calculate Confidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Completeness = 3/6 = 0.50 (50%)

Confidence = 0.70 + (0.30 × 0.50) = 0.85 (85%)

Confidence Level: "Good" (3-4 platforms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5: Apply Confidence Adjustment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confidence Adjusted Score = Base Score × Confidence
                          = 65.35 × 0.85
                          = 55.55/100

Confidence Adjustment = 55.55 - 65.35 = -9.80

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6: Apply Bonuses
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bonuses:
  ✅ Has resume: +5
  ✅ Has GitHub + coding platform (LeetCode): +3
  ❌ Has resume + LinkedIn: 0 (LinkedIn missing)

Total Bonuses: +8

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7: Apply Compensatory Bonuses
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compensatory Bonuses:
  ❌ GitHub score (68) not > 70: 0
  ❌ Resume score (75.67) > 70 but LinkedIn not missing: 0
  ❌ Coding average not > 70: 0

Total Compensatory: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 8: Apply Penalties
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Penalties:
  ❌ Has 3 platforms (≥2): 0
  ❌ Has resume: 0

Total Penalties: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 9: Calculate Final Score
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Final Score = Confidence Adjusted + Bonuses + Compensatory - Penalties
            = 55.55 + 8 + 0 - 0
            = 63.55/100

Capped: min(100, max(0, 63.55)) = 63.55/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 10: Calculate Confidence Interval
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confidence Level: "Good" → Margin: ±5 points

Confidence Interval: [63.55 - 5, 63.55 + 5]
                    = [58.55, 68.55]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Score: 63.55 ± 5 (Good Confidence)
Recommendation: "Consider - Decent candidate"
Strengths: Resume
Weaknesses: None
Warnings: Missing 3 platforms - consider requesting more information
```

---

## 🎯 Key Algorithm Features

### 1. Two-Level Weighting
- **Level 1**: Attributes within each platform (29 total attributes)
- **Level 2**: Platforms in final score (6 platforms)

### 2. Dynamic Weight Redistribution
- Missing platform weights redistributed proportionally
- Ensures fair scoring regardless of data availability

### 3. Confidence-Based Scoring
- Acknowledges uncertainty with fewer data points
- Formula: `0.70 + (0.30 × completeness)`
- Range: 70% (1 platform) to 100% (6 platforms)

### 4. Compensatory Mechanisms
- Strengths can offset weaknesses
- Strong GitHub compensates for weak LeetCode
- Strong Resume compensates for missing LinkedIn

### 5. Bonus/Penalty System
- Rewards good platform combinations
- Penalizes insufficient data
- Ensures minimum standards

### 6. Confidence Intervals
- Shows uncertainty range
- Wider intervals for less data
- Transparent about score reliability

---

## 📊 Algorithm Advantages

1. **Fair**: Doesn't penalize incomplete data unfairly
2. **Transparent**: Clear calculation steps, explainable
3. **Flexible**: Handles 1-6 platforms
4. **Confidence-Aware**: Reports uncertainty
5. **Compensatory**: Allows trade-offs
6. **Customizable**: Adjustable weights
7. **Comprehensive**: 29 attributes considered
8. **Balanced**: No single attribute dominates

---

## ✅ Summary

The algorithm uses:
- **29 individual attributes** across 6 platforms
- **Two-level weighting** (attribute × platform)
- **Dynamic weight redistribution** for missing data
- **Confidence multipliers** (70%-100%)
- **Compensatory bonuses** (up to +12 points)
- **Confidence intervals** (±3 to ±12 points)

**Result**: Fair, transparent, and adaptive candidate ranking that handles incomplete data intelligently.
