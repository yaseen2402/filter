"""
Candidate Ranking & Shortlisting Algorithm

Uses multi-criteria decision making with weighted scoring across:
- Technical Skills (Coding Platforms)
- Professional Profile (LinkedIn)
- Project Quality (GitHub)
- Resume Analysis
- Company-Specific Questions

Implements TOPSIS-like approach with normalization and weighted scoring.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class JobRequirements:
    """Job requirements for context-aware scoring"""
    # Required skills/keywords (higher priority)
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    
    # Education requirements
    min_education: str = "Bachelor's"  # "High School", "Bachelor's", "Master's", "PhD"
    
    # Experience requirements
    min_experience_years: float = 0.0
    
    # Domain/specialization
    domain_keywords: List[str] = None  # e.g., ["machine learning", "generative ai", "gan"]
    
    # Platform importance
    coding_platforms_important: bool = True
    github_important: bool = True
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.domain_keywords is None:
            self.domain_keywords = []


@dataclass
class ScoringWeights:
    """Configurable weights for different criteria"""
    # Platform weights (total should be 1.0)
    codeforces_weight: float = 0.15
    leetcode_weight: float = 0.20
    github_weight: float = 0.25
    linkedin_weight: float = 0.15
    resume_weight: float = 0.15
    company_questions_weight: float = 0.10
    
    def validate(self):
        """Ensure weights sum to 1.0"""
        total = (self.codeforces_weight + self.leetcode_weight + 
                self.github_weight + self.linkedin_weight + 
                self.resume_weight + self.company_questions_weight)
        if not math.isclose(total, 1.0, rel_tol=1e-5):
            raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class CandidateScore:
    """Complete scoring breakdown for a candidate"""
    candidate_name: str
    total_score: float
    
    # Individual platform scores (0-100)
    codeforces_score: float
    leetcode_score: float
    github_score: float
    linkedin_score: float
    resume_score: float
    company_questions_score: float
    
    # Weighted contributions
    codeforces_weighted: float
    leetcode_weighted: float
    github_weighted: float
    linkedin_weighted: float
    resume_weighted: float
    company_questions_weighted: float
    
    # Metadata
    rank: int = 0
    strengths: List[str] = None
    weaknesses: List[str] = None
    recommendation: str = ""
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.weaknesses is None:
            self.weaknesses = []


class CandidateRanker:
    """
    Comprehensive candidate ranking system with context-aware scoring
    """
    
    def __init__(
        self, 
        weights: Optional[ScoringWeights] = None,
        job_requirements: Optional[JobRequirements] = None
    ):
        self.weights = weights or ScoringWeights()
        self.weights.validate()
        self.job_requirements = job_requirements or JobRequirements()
        self.candidates_data = []
        self.scores = []
    
    def load_candidate_data(self, candidate_folder: str) -> Dict:
        """Load all data for a candidate"""
        data = {
            "name": os.path.basename(candidate_folder),
            "folder": candidate_folder
        }
        
        # Load metadata
        metadata_file = os.path.join(candidate_folder, "metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data["metadata"] = json.load(f)
        
        # Load platform data
        platforms = ["codeforces", "leetcode", "github", "linkedin"]
        for platform in platforms:
            platform_file = os.path.join(candidate_folder, f"{platform}.json")
            if os.path.exists(platform_file):
                with open(platform_file, 'r', encoding='utf-8') as f:
                    data[platform] = json.load(f)
        
        # Load resume data if exists
        resume_file = os.path.join(candidate_folder, "resume_analysis.json")
        if os.path.exists(resume_file):
            with open(resume_file, 'r', encoding='utf-8') as f:
                data["resume"] = json.load(f)
        
        # Load company questions if exists
        questions_file = os.path.join(candidate_folder, "company_questions.json")
        if os.path.exists(questions_file):
            with open(questions_file, 'r', encoding='utf-8') as f:
                data["company_questions"] = json.load(f)
        
        return data
    
    def score_codeforces(self, cf_data: Dict) -> float:
        """
        Score Codeforces profile (0-100)
        
        Criteria:
        - Rating (0-4000) -> 40 points
        - Contests participated -> 30 points
        - Rank tier -> 20 points
        - Contribution -> 10 points
        """
        if "error" in cf_data:
            return 0.0
        
        score = 0.0
        
        # Rating score (0-40 points)
        rating = cf_data.get("rating") or 0
        max_rating = 3500  # Legendary Grandmaster threshold
        score += min(40, (rating / max_rating) * 40)
        
        # Contest participation (0-30 points)
        contests = cf_data.get("contests_participated", 0)
        score += min(30, (contests / 100) * 30)  # 100 contests = max points
        
        # Rank tier (0-20 points)
        rank = cf_data.get("rank") or ""
        rank = rank.lower() if rank else ""
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
        score += rank_scores.get(rank, 0)
        
        # Contribution (0-10 points)
        contribution = cf_data.get("contribution", 0)
        score += min(10, max(0, contribution / 10))  # 100 contribution = max
        
        return min(100, score)
    
    def score_leetcode(self, lc_data: Dict) -> float:
        """
        Score LeetCode profile (0-100)
        
        Criteria:
        - Problems solved -> 50 points
        - Difficulty distribution -> 30 points
        - Acceptance rate -> 10 points
        - Ranking -> 10 points
        """
        if "error" in lc_data:
            return 0.0
        
        score = 0.0
        
        # Total problems solved (0-50 points)
        total_solved = lc_data.get("total_solved", 0)
        score += min(50, (total_solved / 500) * 50)  # 500 problems = max
        
        # Difficulty distribution (0-30 points)
        easy = lc_data.get("easy_solved", 0)
        medium = lc_data.get("medium_solved", 0)
        hard = lc_data.get("hard_solved", 0)
        
        # Weighted by difficulty
        difficulty_score = (easy * 1 + medium * 2 + hard * 3) / 6
        score += min(30, (difficulty_score / 200) * 30)
        
        # Acceptance rate (0-10 points)
        acceptance = lc_data.get("acceptance_rate", 0)
        score += min(10, (acceptance / 100) * 10)
        
        # Ranking (0-10 points) - lower is better
        ranking = lc_data.get("ranking", 5000000)
        if ranking < 100000:
            score += 10
        elif ranking < 500000:
            score += 7
        elif ranking < 1000000:
            score += 5
        elif ranking < 2000000:
            score += 3
        
        return min(100, score)
    
    def score_github(self, gh_data: Dict) -> float:
        """
        Score GitHub profile (0-100) with context-aware scoring
        
        Criteria:
        - Repository count -> 15 points
        - Stars earned -> 25 points
        - Followers -> 10 points
        - Language/tech match -> 20 points
        - Project quality -> 15 points
        - Domain relevance -> 15 points
        """
        if "error" in gh_data:
            return 0.0
        
        score = 0.0
        
        # Repository count (0-15 points)
        repos = gh_data.get("public_repos", 0)
        score += min(15, (repos / 50) * 15)
        
        # Stars earned (0-25 points)
        stars = gh_data.get("total_stars_earned", 0)
        if stars >= 1000:
            score += 25
        elif stars >= 500:
            score += 22
        elif stars >= 100:
            score += 18
        elif stars >= 50:
            score += 14
        elif stars >= 10:
            score += 10
        elif stars >= 1:
            score += 5
        
        # Followers (0-10 points)
        followers = gh_data.get("followers", 0)
        score += min(10, (followers / 100) * 10)
        
        # Language/Technology match (0-20 points)
        languages = gh_data.get("top_languages", [])
        # Handle both list of strings and list of dicts
        if languages and isinstance(languages[0], dict):
            lang_lower = [lang.get('name', '').lower() for lang in languages]
        else:
            lang_lower = [str(lang).lower() for lang in languages]
        
        # Base diversity score (0-10 points)
        score += min(10, (len(languages) / 5) * 10)
        
        # Required skills match (0-10 points)
        if self.job_requirements.required_skills:
            matches = sum(1 for skill in self.job_requirements.required_skills 
                         if skill.lower() in lang_lower)
            score += min(10, (matches / max(1, len(self.job_requirements.required_skills))) * 10)
        
        # Project quality (0-15 points)
        top_repos = gh_data.get("top_repositories", [])
        if top_repos:
            quality_repos = sum(1 for repo in top_repos 
                              if repo.get("description") and 
                              (repo.get("stars", 0) > 0 or repo.get("topics")))
            score += min(15, (quality_repos / len(top_repos)) * 15)
        
        # Domain relevance (0-15 points) - Check repo names, descriptions, topics
        if self.job_requirements.domain_keywords and top_repos:
            domain_score = 0
            for repo in top_repos:
                repo_text = f"{repo.get('name', '')} {repo.get('description', '')} {' '.join(repo.get('topics', []))}".lower()
                matches = sum(1 for keyword in self.job_requirements.domain_keywords 
                            if keyword.lower() in repo_text)
                if matches > 0:
                    domain_score += min(5, matches * 2)  # Up to 5 points per relevant repo
            
            score += min(15, domain_score)
        
        return min(100, score)
    
    def score_linkedin(self, li_data: Dict) -> float:
        """
        Score LinkedIn profile (0-100) with context-aware scoring
        
        Criteria:
        - Profile completeness -> 25 points
        - Experience -> 20 points
        - Education -> 25 points (with degree level bonus)
        - Network size -> 10 points
        - Skills & domain match -> 20 points
        """
        if "error" in li_data:
            return 0.0
        
        score = 0.0
        
        # Profile completeness (0-25 points)
        completeness = 0
        if li_data.get("full_name"):
            completeness += 4
        if li_data.get("headline"):
            completeness += 5
        if li_data.get("summary"):
            completeness += 5
        if li_data.get("location"):
            completeness += 3
        if li_data.get("profile_pic_url"):
            completeness += 3
        if li_data.get("experiences"):
            completeness += 5
        score += completeness
        
        # Experience (0-20 points)
        experiences = li_data.get("experiences", [])
        if experiences:
            valid_exp = sum(1 for exp in experiences 
                          if exp.get("company") and exp.get("title"))
            score += min(20, (valid_exp / 3) * 20)
            
            # Bonus for domain-relevant experience
            if self.job_requirements.domain_keywords:
                exp_text = " ".join([
                    f"{exp.get('title', '')} {exp.get('description', '')}".lower()
                    for exp in experiences
                ])
                domain_matches = sum(1 for keyword in self.job_requirements.domain_keywords 
                                   if keyword.lower() in exp_text)
                if domain_matches > 0:
                    score += min(5, domain_matches * 2)  # Up to 5 bonus points
        
        # Education (0-25 points) - Enhanced with degree level
        education = li_data.get("education", [])
        if education:
            # Base score for having education
            valid_edu = sum(1 for edu in education if edu.get("school"))
            base_edu_score = min(15, (valid_edu / 2) * 15)
            
            # Degree level bonus (0-10 points)
            degree_bonus = 0
            edu_text = " ".join([
                f"{edu.get('degree', '')} {edu.get('field_of_study', '')}".lower()
                for edu in education
            ])
            
            if any(keyword in edu_text for keyword in ['phd', 'ph.d', 'doctorate']):
                degree_bonus = 10
            elif any(keyword in edu_text for keyword in ['master', 'msc', 'm.sc', 'ms', 'm.s', 'mtech', 'mba']):
                degree_bonus = 7
            elif any(keyword in edu_text for keyword in ['bachelor', 'bsc', 'b.sc', 'bs', 'btech', 'be', 'b.e']):
                degree_bonus = 4
            
            score += base_edu_score + degree_bonus
        
        # Network size (0-10 points)
        connections_str = li_data.get("connections", "0")
        try:
            connections = int(''.join(filter(str.isdigit, connections_str)))
            if connections >= 500:
                score += 10
            elif connections >= 200:
                score += 8
            elif connections >= 100:
                score += 6
            elif connections >= 50:
                score += 4
            else:
                score += 2
        except:
            pass
        
        # Skills & domain match (0-20 points)
        skills = li_data.get("skills", [])
        skills_lower = [s.lower() for s in skills]
        
        # Base skills score (0-10 points)
        score += min(10, (len(skills) / 10) * 10)
        
        # Domain/required skills match (0-10 points)
        if self.job_requirements.required_skills or self.job_requirements.domain_keywords:
            all_required = self.job_requirements.required_skills + self.job_requirements.domain_keywords
            matches = sum(1 for req in all_required if req.lower() in skills_lower)
            score += min(10, (matches / max(1, len(all_required))) * 10)
        
        return min(100, score)
    
    def score_resume(self, resume_data: Optional[Dict]) -> float:
        """
        Score resume analysis (0-100) with context-aware scoring
        
        Enhanced scoring based on job requirements
        """
        if not resume_data:
            return 50.0  # Neutral score if no resume
        
        # If resume was analyzed by ResumeParser with job requirements, use that score
        if "score" in resume_data and self.job_requirements.required_skills:
            # Resume parser already considered job requirements
            return resume_data["score"]
        
        # Calculate context-aware score
        score = 0.0
        
        # Education level (0-30 points) - Enhanced weightage
        education = resume_data.get("education_level", "Unknown")
        education_scores = {
            'PhD': 30,           # Highest degree
            "Master's": 22,      # Advanced degree
            "Bachelor's": 15,    # Standard degree
            'High School': 5,    # Basic education
            'Unknown': 0
        }
        score += education_scores.get(education, 0)
        
        # Check if meets minimum education requirement
        education_levels = ['High School', "Bachelor's", "Master's", 'PhD']
        try:
            candidate_level = education_levels.index(education)
            required_level = education_levels.index(self.job_requirements.min_education)
            if candidate_level < required_level:
                score -= 10  # Penalty for not meeting minimum
        except:
            pass
        
        # Experience (0-25 points)
        exp_years = resume_data.get("total_experience_years", 0)
        if exp_years >= self.job_requirements.min_experience_years:
            # Meets or exceeds requirement
            if exp_years >= 10:
                score += 25
            elif exp_years >= 5:
                score += 22
            elif exp_years >= 3:
                score += 18
            elif exp_years >= 1:
                score += 15
            else:
                score += 12
        else:
            # Below requirement
            score += min(10, exp_years * 3)
        
        # Technical Skills (0-25 points)
        skills = resume_data.get("technical_skills", [])
        skills_lower = [s.lower() for s in skills]
        
        # Base skills count (0-10 points)
        score += min(10, (len(skills) / 10) * 10)
        
        # Required skills match (0-15 points) - Critical
        if self.job_requirements.required_skills:
            required_matches = sum(1 for req in self.job_requirements.required_skills 
                                  if req.lower() in skills_lower)
            match_ratio = required_matches / len(self.job_requirements.required_skills)
            score += match_ratio * 15
        else:
            score += 7.5  # Neutral if no requirements
        
        # Domain keywords match (0-10 points)
        if self.job_requirements.domain_keywords:
            # Check skills, projects, certifications for domain keywords
            all_text = " ".join([
                " ".join(skills),
                " ".join(resume_data.get("projects", [])),
                " ".join(resume_data.get("certifications", []))
            ]).lower()
            
            domain_matches = sum(1 for keyword in self.job_requirements.domain_keywords 
                               if keyword.lower() in all_text)
            score += min(10, (domain_matches / max(1, len(self.job_requirements.domain_keywords))) * 10)
        else:
            score += 5  # Neutral
        
        # Certifications & Projects (0-10 points)
        certs = len(resume_data.get("certifications", []))
        projects = len(resume_data.get("projects", []))
        score += min(5, certs * 1.5)
        score += min(5, projects * 1)
        
        return min(100, max(0, score))
    
    def score_company_questions(self, questions_data: Optional[Dict]) -> float:
        """
        Score company-specific questions (0-100)
        
        Uses CompanyQuestionsManager assessment if available
        """
        if not questions_data:
            return 50.0  # Neutral score if no questions
        
        # If assessment was evaluated, it has percentage_score or score
        if "percentage_score" in questions_data:
            return questions_data["percentage_score"]
        
        if "score" in questions_data:
            return questions_data["score"]
        
        # Fallback: calculate from points
        if "points_earned" in questions_data and "total_points" in questions_data:
            total = questions_data["total_points"]
            earned = questions_data["points_earned"]
            return (earned / total * 100) if total > 0 else 50.0
        
        return 50.0
    
    def calculate_candidate_score(self, candidate_data: Dict) -> CandidateScore:
        """Calculate comprehensive score for a candidate"""
        
        # Calculate individual platform scores
        cf_score = self.score_codeforces(candidate_data.get("codeforces", {}))
        lc_score = self.score_leetcode(candidate_data.get("leetcode", {}))
        gh_score = self.score_github(candidate_data.get("github", {}))
        li_score = self.score_linkedin(candidate_data.get("linkedin", {}))
        resume_score = self.score_resume(candidate_data.get("resume"))
        questions_score = self.score_company_questions(candidate_data.get("company_questions"))
        
        # Calculate weighted contributions
        cf_weighted = cf_score * self.weights.codeforces_weight
        lc_weighted = lc_score * self.weights.leetcode_weight
        gh_weighted = gh_score * self.weights.github_weight
        li_weighted = li_score * self.weights.linkedin_weight
        resume_weighted = resume_score * self.weights.resume_weight
        questions_weighted = questions_score * self.weights.company_questions_weight
        
        # Total score
        total_score = (cf_weighted + lc_weighted + gh_weighted + 
                      li_weighted + resume_weighted + questions_weighted)
        
        # Identify strengths and weaknesses
        scores_dict = {
            "Codeforces": cf_score,
            "LeetCode": lc_score,
            "GitHub": gh_score,
            "LinkedIn": li_score,
            "Resume": resume_score,
            "Company Questions": questions_score
        }
        
        strengths = [k for k, v in scores_dict.items() if v >= 70]
        weaknesses = [k for k, v in scores_dict.items() if v < 50]
        
        # Generate recommendation
        if total_score >= 80:
            recommendation = "Highly Recommended - Strong candidate across all criteria"
        elif total_score >= 70:
            recommendation = "Recommended - Good candidate with minor gaps"
        elif total_score >= 60:
            recommendation = "Consider - Decent candidate, needs evaluation"
        elif total_score >= 50:
            recommendation = "Marginal - Significant gaps in key areas"
        else:
            recommendation = "Not Recommended - Does not meet minimum criteria"
        
        return CandidateScore(
            candidate_name=candidate_data.get("name", "Unknown"),
            total_score=total_score,
            codeforces_score=cf_score,
            leetcode_score=lc_score,
            github_score=gh_score,
            linkedin_score=li_score,
            resume_score=resume_score,
            company_questions_score=questions_score,
            codeforces_weighted=cf_weighted,
            leetcode_weighted=lc_weighted,
            github_weighted=gh_weighted,
            linkedin_weighted=li_weighted,
            resume_weighted=resume_weighted,
            company_questions_weighted=questions_weighted,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation
        )
    
    def rank_candidates(self, candidates_folder: str = "data/candidates") -> List[CandidateScore]:
        """
        Rank all candidates in the folder
        
        Returns sorted list of CandidateScore objects
        """
        self.scores = []
        
        if not os.path.exists(candidates_folder):
            print(f"❌ Candidates folder not found: {candidates_folder}")
            return []
        
        # Load all candidates
        for candidate_name in os.listdir(candidates_folder):
            candidate_folder = os.path.join(candidates_folder, candidate_name)
            if os.path.isdir(candidate_folder):
                print(f"📊 Scoring: {candidate_name}")
                candidate_data = self.load_candidate_data(candidate_folder)
                score = self.calculate_candidate_score(candidate_data)
                self.scores.append(score)
        
        # Sort by total score (descending)
        self.scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # Assign ranks
        for i, score in enumerate(self.scores, 1):
            score.rank = i
        
        return self.scores
    
    def get_top_candidates(self, n: int = 5) -> List[CandidateScore]:
        """Get top N candidates"""
        return self.scores[:n]
    
    def generate_ranking_report(self, output_file: str = "ranking_report.json"):
        """Generate detailed ranking report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_candidates": len(self.scores),
            "weights_used": {
                "codeforces": self.weights.codeforces_weight,
                "leetcode": self.weights.leetcode_weight,
                "github": self.weights.github_weight,
                "linkedin": self.weights.linkedin_weight,
                "resume": self.weights.resume_weight,
                "company_questions": self.weights.company_questions_weight
            },
            "rankings": []
        }
        
        for score in self.scores:
            report["rankings"].append({
                "rank": score.rank,
                "name": score.candidate_name,
                "total_score": round(score.total_score, 2),
                "scores": {
                    "codeforces": round(score.codeforces_score, 2),
                    "leetcode": round(score.leetcode_score, 2),
                    "github": round(score.github_score, 2),
                    "linkedin": round(score.linkedin_score, 2),
                    "resume": round(score.resume_score, 2),
                    "company_questions": round(score.company_questions_score, 2)
                },
                "weighted_contributions": {
                    "codeforces": round(score.codeforces_weighted, 2),
                    "leetcode": round(score.leetcode_weighted, 2),
                    "github": round(score.github_weighted, 2),
                    "linkedin": round(score.linkedin_weighted, 2),
                    "resume": round(score.resume_weighted, 2),
                    "company_questions": round(score.company_questions_weighted, 2)
                },
                "strengths": score.strengths,
                "weaknesses": score.weaknesses,
                "recommendation": score.recommendation
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


def main():
    """Example usage with job requirements"""
    
    # Define job requirements for a Generative AI role
    job_reqs = JobRequirements(
        required_skills=['python', 'tensorflow', 'pytorch', 'machine learning'],
        preferred_skills=['transformers', 'huggingface', 'langchain'],
        min_education="Bachelor's",
        min_experience_years=2,
        domain_keywords=['generative ai', 'gan', 'gpt', 'llm', 'diffusion', 'stable diffusion', 'transformer']
    )
    
    # Create ranker with custom weights for AI/ML role
    weights = ScoringWeights(
        codeforces_weight=0.10,      # Less important for AI role
        leetcode_weight=0.15,        # Moderate importance
        github_weight=0.30,          # Very important - need to see projects
        linkedin_weight=0.15,        # Important for experience
        resume_weight=0.20,          # Important for education/skills
        company_questions_weight=0.10
    )
    
    ranker = CandidateRanker(weights=weights, job_requirements=job_reqs)
    
    print("=" * 70)
    print("CONTEXT-AWARE CANDIDATE RANKING SYSTEM")
    print("=" * 70)
    print()
    print("Job Requirements:")
    print(f"  • Required Skills: {', '.join(job_reqs.required_skills)}")
    print(f"  • Domain: {', '.join(job_reqs.domain_keywords[:5])}...")
    print(f"  • Min Education: {job_reqs.min_education}")
    print(f"  • Min Experience: {job_reqs.min_experience_years} years")
    print()
    
    # Rank all candidates
    scores = ranker.rank_candidates("data/candidates")
    
    print()
    print("=" * 70)
    print("RANKING RESULTS")
    print("=" * 70)
    print()
    
    # Display top 5
    top_5 = ranker.get_top_candidates(5)
    
    for score in top_5:
        print(f"🏆 Rank #{score.rank}: {score.candidate_name}")
        print(f"   Total Score: {score.total_score:.2f}/100")
        print(f"   Recommendation: {score.recommendation}")
        print(f"   Strengths: {', '.join(score.strengths) if score.strengths else 'None identified'}")
        print(f"   Weaknesses: {', '.join(score.weaknesses) if score.weaknesses else 'None identified'}")
        print()
    
    # Generate report
    report = ranker.generate_ranking_report("data/ranking_report.json")
    print(f"📄 Detailed report saved to: data/ranking_report.json")
    print()


if __name__ == "__main__":
    main()
