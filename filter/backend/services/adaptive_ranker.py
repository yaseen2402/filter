"""
Adaptive Candidate Ranking System

Handles incomplete data fairly using:
1. Dynamic weight redistribution
2. Confidence-based scoring
3. Compensatory mechanisms
4. Minimum data requirements
"""

import json
import os
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from candidate_ranker import (
    CandidateRanker, JobRequirements, ScoringWeights, CandidateScore
)


@dataclass
class AdaptiveScore:
    """Enhanced score with confidence and adjustments"""
    candidate_name: str
    final_score: float
    base_score: float
    confidence: float
    confidence_level: str
    
    # Platform availability
    available_platforms: List[str]
    missing_platforms: List[str]
    completeness: float
    
    # Individual scores
    platform_scores: Dict[str, float]
    adjusted_weights: Dict[str, float]
    
    # Adjustments
    confidence_adjustment: float
    bonus_adjustments: float
    penalty_adjustments: float
    compensatory_adjustments: float
    
    # Metadata
    rank: int = 0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendation: str = ""
    confidence_interval: Tuple[float, float] = (0, 0)
    warnings: List[str] = field(default_factory=list)


class AdaptiveRanker(CandidateRanker):
    """
    Enhanced ranker that handles incomplete data fairly
    """
    
    # Platform categories
    CRITICAL_PLATFORMS = ['resume', 'github']
    CODING_PLATFORMS = ['codeforces', 'leetcode', 'github']
    PROFESSIONAL_PLATFORMS = ['linkedin', 'resume']
    ASSESSMENT_PLATFORMS = ['company_questions']
    
    # Confidence parameters
    MIN_CONFIDENCE = 0.70
    MAX_CONFIDENCE = 1.00
    CONFIDENCE_RANGE = MAX_CONFIDENCE - MIN_CONFIDENCE
    
    # Minimum requirements
    MIN_PLATFORMS_REQUIRED = 1
    MIN_PLATFORMS_RECOMMENDED = 2
    
    def __init__(
        self,
        weights: Optional[ScoringWeights] = None,
        job_requirements: Optional[JobRequirements] = None,
        use_adaptive_scoring: bool = True
    ):
        super().__init__(weights, job_requirements)
        self.use_adaptive_scoring = use_adaptive_scoring
        self.adaptive_scores = []
    
    def get_available_platforms(self, candidate_data: Dict) -> List[str]:
        """Identify which platforms have data"""
        available = []
        
        platforms_to_check = {
            'codeforces': 'codeforces',
            'leetcode': 'leetcode',
            'github': 'github',
            'linkedin': 'linkedin',
            'resume': 'resume',
            'company_questions': 'company_questions'
        }
        
        for key, platform in platforms_to_check.items():
            data = candidate_data.get(key, {})
            
            # Check if platform has meaningful data
            if data and not data.get('error'):
                # For resume and questions, check if file exists
                if key in ['resume', 'company_questions']:
                    if data.get('score') is not None or data.get('education_level'):
                        available.append(platform)
                else:
                    # For social platforms, check if has data
                    if isinstance(data, dict) and len(data) > 1:
                        available.append(platform)
        
        return available
    
    def check_minimum_requirements(self, available: List[str]) -> Tuple[bool, str]:
        """Check if candidate has minimum required data"""
        
        # Must have at least one platform
        if len(available) < self.MIN_PLATFORMS_REQUIRED:
            return False, "No data available"
        
        # Must have at least one critical platform
        has_critical = any(p in available for p in self.CRITICAL_PLATFORMS)
        if not has_critical:
            return False, f"Need at least one of: {', '.join(self.CRITICAL_PLATFORMS)}"
        
        return True, "OK"
    
    def calculate_adaptive_weights(
        self,
        available: List[str],
        original_weights: ScoringWeights
    ) -> Dict[str, float]:
        """Redistribute weights based on available platforms"""
        
        weight_map = {
            'codeforces': original_weights.codeforces_weight,
            'leetcode': original_weights.leetcode_weight,
            'github': original_weights.github_weight,
            'linkedin': original_weights.linkedin_weight,
            'resume': original_weights.resume_weight,
            'company_questions': original_weights.company_questions_weight
        }
        
        # Calculate total available weight
        total_available = sum(weight_map[p] for p in available if p in weight_map)
        
        if total_available == 0:
            return {}
        
        # Redistribute proportionally
        adjusted = {
            p: weight_map[p] / total_available
            for p in available if p in weight_map
        }
        
        return adjusted
    
    def calculate_confidence(self, available: List[str]) -> Tuple[float, str]:
        """Calculate confidence level based on data completeness"""
        
        total_platforms = 6  # Total possible platforms
        completeness = len(available) / total_platforms
        
        # Confidence formula: 0.70 + (0.30 × completeness)
        confidence = self.MIN_CONFIDENCE + (self.CONFIDENCE_RANGE * completeness)
        
        # Determine confidence level
        if len(available) >= 5:
            level = "High"
        elif len(available) >= 3:
            level = "Good"
        elif len(available) >= 2:
            level = "Moderate"
        else:
            level = "Low"
        
        return confidence, level
    
    def calculate_confidence_interval(
        self,
        score: float,
        confidence_level: str
    ) -> Tuple[float, float]:
        """Calculate confidence interval for score"""
        
        margins = {
            "High": 3,
            "Good": 5,
            "Moderate": 8,
            "Low": 12
        }
        
        margin = margins.get(confidence_level, 10)
        
        lower = max(0, score - margin)
        upper = min(100, score + margin)
        
        return (lower, upper)
    
    def calculate_bonuses(
        self,
        available: List[str],
        platform_scores: Dict[str, float]
    ) -> Tuple[float, List[str]]:
        """Calculate bonus adjustments"""
        
        bonus = 0.0
        explanations = []
        
        # Bonus for having resume (critical)
        if 'resume' in available:
            bonus += 5
            explanations.append("+5 for having resume")
        
        # Bonus for good platform combination
        has_github = 'github' in available
        has_coding = any(p in available for p in ['leetcode', 'codeforces'])
        
        if has_github and has_coding:
            bonus += 3
            explanations.append("+3 for GitHub + coding platform")
        
        # Bonus for complete professional profile
        if 'resume' in available and 'linkedin' in available:
            bonus += 2
            explanations.append("+2 for complete professional profile")
        
        return bonus, explanations
    
    def calculate_compensatory_bonuses(
        self,
        available: List[str],
        missing: List[str],
        platform_scores: Dict[str, float]
    ) -> Tuple[float, List[str]]:
        """Calculate compensatory bonuses (strengths offsetting weaknesses)"""
        
        bonus = 0.0
        explanations = []
        
        # Strong GitHub compensates for weak/missing coding platforms
        github_score = platform_scores.get('github', 0)
        if github_score > 70:
            if 'leetcode' in missing or platform_scores.get('leetcode', 0) < 50:
                bonus += 5
                explanations.append("+5 strong GitHub compensates for LeetCode")
            
            if 'codeforces' in missing or platform_scores.get('codeforces', 0) < 50:
                bonus += 3
                explanations.append("+3 strong GitHub compensates for Codeforces")
        
        # Strong resume compensates for missing LinkedIn
        resume_score = platform_scores.get('resume', 0)
        if resume_score > 70 and 'linkedin' in missing:
            bonus += 3
            explanations.append("+3 strong resume compensates for LinkedIn")
        
        # Strong coding platforms compensate for weak GitHub
        coding_scores = [
            platform_scores.get('leetcode', 0),
            platform_scores.get('codeforces', 0)
        ]
        avg_coding = sum(coding_scores) / len([s for s in coding_scores if s > 0]) if any(coding_scores) else 0
        
        if avg_coding > 70 and platform_scores.get('github', 0) < 50:
            bonus += 4
            explanations.append("+4 strong coding platforms compensate for GitHub")
        
        return bonus, explanations
    
    def calculate_penalties(
        self,
        available: List[str],
        missing: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate penalty adjustments"""
        
        penalty = 0.0
        explanations = []
        
        # Penalty for very incomplete data
        if len(available) < self.MIN_PLATFORMS_RECOMMENDED:
            penalty += 10
            explanations.append(f"-10 for having only {len(available)} platform(s)")
        
        # Warning for missing critical platforms
        if 'resume' in missing and 'github' in missing:
            penalty += 5
            explanations.append("-5 for missing both resume and GitHub")
        
        return penalty, explanations
    
    def generate_warnings(
        self,
        available: List[str],
        missing: List[str],
        confidence_level: str
    ) -> List[str]:
        """Generate warnings about data quality"""
        
        warnings = []
        
        if confidence_level == "Low":
            warnings.append(f"Low confidence: Only {len(available)} platform(s) available")
        
        if 'resume' in missing:
            warnings.append("Missing resume - critical for evaluation")
        
        if all(p in missing for p in self.CODING_PLATFORMS):
            warnings.append("No coding platforms - cannot assess technical skills")
        
        if all(p in missing for p in self.PROFESSIONAL_PLATFORMS):
            warnings.append("No professional profile - limited background info")
        
        if len(available) < 3:
            warnings.append("Limited data - consider requesting more information")
        
        return warnings
    
    def calculate_adaptive_candidate_score(
        self,
        candidate_data: Dict
    ) -> AdaptiveScore:
        """Calculate comprehensive adaptive score"""
        
        candidate_name = candidate_data.get("name", "Unknown")
        
        # Step 1: Identify available platforms
        available = self.get_available_platforms(candidate_data)
        all_platforms = ['codeforces', 'leetcode', 'github', 'linkedin', 'resume', 'company_questions']
        missing = [p for p in all_platforms if p not in available]
        
        # Step 2: Check minimum requirements
        meets_min, reason = self.check_minimum_requirements(available)
        if not meets_min:
            return AdaptiveScore(
                candidate_name=candidate_name,
                final_score=0,
                base_score=0,
                confidence=0,
                confidence_level="Insufficient",
                available_platforms=available,
                missing_platforms=missing,
                completeness=0,
                platform_scores={},
                adjusted_weights={},
                confidence_adjustment=0,
                bonus_adjustments=0,
                penalty_adjustments=0,
                compensatory_adjustments=0,
                warnings=[f"Insufficient data: {reason}"]
            )
        
        # Step 3: Calculate individual platform scores
        platform_scores = {}
        if 'codeforces' in available:
            platform_scores['codeforces'] = self.score_codeforces(candidate_data.get('codeforces', {}))
        if 'leetcode' in available:
            platform_scores['leetcode'] = self.score_leetcode(candidate_data.get('leetcode', {}))
        if 'github' in available:
            platform_scores['github'] = self.score_github(candidate_data.get('github', {}))
        if 'linkedin' in available:
            platform_scores['linkedin'] = self.score_linkedin(candidate_data.get('linkedin', {}))
        if 'resume' in available:
            platform_scores['resume'] = self.score_resume(candidate_data.get('resume', {}))
        if 'company_questions' in available:
            platform_scores['company_questions'] = self.score_company_questions(candidate_data.get('company_questions', {}))
        
        # Step 4: Calculate adaptive weights
        adjusted_weights = self.calculate_adaptive_weights(available, self.weights)
        
        # Step 5: Calculate base score
        base_score = sum(
            platform_scores[p] * adjusted_weights[p]
            for p in available if p in adjusted_weights
        )
        
        # Step 6: Calculate confidence
        confidence, confidence_level = self.calculate_confidence(available)
        completeness = len(available) / 6
        
        # Step 7: Apply confidence adjustment
        confidence_adjusted = base_score * confidence
        confidence_adjustment = confidence_adjusted - base_score
        
        # Step 8: Calculate bonuses
        bonus, bonus_explanations = self.calculate_bonuses(available, platform_scores)
        
        # Step 9: Calculate compensatory bonuses
        comp_bonus, comp_explanations = self.calculate_compensatory_bonuses(
            available, missing, platform_scores
        )
        
        # Step 10: Calculate penalties
        penalty, penalty_explanations = self.calculate_penalties(available, missing)
        
        # Step 11: Calculate final score
        final_score = confidence_adjusted + bonus + comp_bonus - penalty
        final_score = min(100, max(0, final_score))
        
        # Step 12: Calculate confidence interval
        conf_interval = self.calculate_confidence_interval(final_score, confidence_level)
        
        # Step 13: Identify strengths and weaknesses
        strengths = [p.title() for p, s in platform_scores.items() if s >= 70]
        weaknesses = [p.title() for p, s in platform_scores.items() if s < 50]
        
        # Step 14: Generate recommendation
        if final_score >= 80:
            recommendation = "Highly Recommended - Strong candidate"
        elif final_score >= 70:
            recommendation = "Recommended - Good candidate"
        elif final_score >= 60:
            recommendation = "Consider - Decent candidate"
        elif final_score >= 50:
            recommendation = "Marginal - Significant gaps"
        else:
            recommendation = "Not Recommended - Does not meet criteria"
        
        if confidence_level in ["Low", "Moderate"]:
            recommendation += f" ({confidence_level} confidence - limited data)"
        
        # Step 15: Generate warnings
        warnings = self.generate_warnings(available, missing, confidence_level)
        
        return AdaptiveScore(
            candidate_name=candidate_name,
            final_score=final_score,
            base_score=base_score,
            confidence=confidence,
            confidence_level=confidence_level,
            available_platforms=available,
            missing_platforms=missing,
            completeness=completeness,
            platform_scores=platform_scores,
            adjusted_weights=adjusted_weights,
            confidence_adjustment=confidence_adjustment,
            bonus_adjustments=bonus,
            penalty_adjustments=penalty,
            compensatory_adjustments=comp_bonus,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            confidence_interval=conf_interval,
            warnings=warnings
        )
    
    def rank_candidates_adaptive(
        self,
        candidates_folder: str = "data/candidates"
    ) -> List[AdaptiveScore]:
        """Rank all candidates using adaptive scoring"""
        
        self.adaptive_scores = []
        
        if not os.path.exists(candidates_folder):
            print(f"❌ Candidates folder not found: {candidates_folder}")
            return []
        
        # Load all candidates
        for candidate_name in os.listdir(candidates_folder):
            candidate_folder = os.path.join(candidates_folder, candidate_name)
            if os.path.isdir(candidate_folder):
                print(f"📊 Scoring: {candidate_name}")
                candidate_data = self.load_candidate_data(candidate_folder)
                score = self.calculate_adaptive_candidate_score(candidate_data)
                self.adaptive_scores.append(score)
        
        # Sort by final score (descending)
        self.adaptive_scores.sort(key=lambda x: x.final_score, reverse=True)
        
        # Assign ranks
        for i, score in enumerate(self.adaptive_scores, 1):
            score.rank = i
        
        return self.adaptive_scores
    
    def generate_adaptive_report(self, output_file: str = "adaptive_ranking_report.json"):
        """Generate detailed adaptive ranking report"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_candidates": len(self.adaptive_scores),
            "scoring_method": "Adaptive with Confidence Adjustment",
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
        
        for score in self.adaptive_scores:
            report["rankings"].append({
                "rank": score.rank,
                "name": score.candidate_name,
                "final_score": round(score.final_score, 2),
                "base_score": round(score.base_score, 2),
                "confidence": round(score.confidence, 2),
                "confidence_level": score.confidence_level,
                "confidence_interval": [round(score.confidence_interval[0], 1), round(score.confidence_interval[1], 1)],
                "completeness": round(score.completeness * 100, 1),
                "available_platforms": score.available_platforms,
                "missing_platforms": score.missing_platforms,
                "platform_scores": {k: round(v, 2) for k, v in score.platform_scores.items()},
                "adjusted_weights": {k: round(v, 3) for k, v in score.adjusted_weights.items()},
                "adjustments": {
                    "confidence": round(score.confidence_adjustment, 2),
                    "bonuses": round(score.bonus_adjustments, 2),
                    "compensatory": round(score.compensatory_adjustments, 2),
                    "penalties": round(score.penalty_adjustments, 2)
                },
                "strengths": score.strengths,
                "weaknesses": score.weaknesses,
                "recommendation": score.recommendation,
                "warnings": score.warnings
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


def main():
    """Example usage"""
    
    print("=" * 70)
    print("ADAPTIVE CANDIDATE RANKING SYSTEM")
    print("=" * 70)
    print()
    print("Features:")
    print("  • Handles incomplete data fairly")
    print("  • Dynamic weight redistribution")
    print("  • Confidence-based scoring")
    print("  • Compensatory mechanisms")
    print("  • Detailed explanations")
    print()
    
    # Create adaptive ranker
    job_reqs = JobRequirements(
        required_skills=['python', 'java'],
        domain_keywords=['machine learning', 'ai'],
        min_education="Bachelor's",
        min_experience_years=2
    )
    
    weights = ScoringWeights(
        github_weight=0.25,
        leetcode_weight=0.20,
        codeforces_weight=0.15,
        linkedin_weight=0.15,
        resume_weight=0.15,
        company_questions_weight=0.10
    )
    
    ranker = AdaptiveRanker(weights=weights, job_requirements=job_reqs)
    
    # Rank candidates
    scores = ranker.rank_candidates_adaptive("data/candidates")
    
    print("=" * 70)
    print("ADAPTIVE RANKING RESULTS")
    print("=" * 70)
    print()
    
    for score in scores:
        print(f"🏆 Rank #{score.rank}: {score.candidate_name}")
        print(f"   📊 Final Score: {score.final_score:.2f}/100")
        print(f"   📈 Base Score: {score.base_score:.2f}")
        print(f"   🎯 Confidence: {score.confidence:.0%} ({score.confidence_level})")
        print(f"   📉 Confidence Interval: [{score.confidence_interval[0]:.1f}, {score.confidence_interval[1]:.1f}]")
        print(f"   📁 Data Completeness: {score.completeness:.0%} ({len(score.available_platforms)}/6 platforms)")
        print(f"   ✅ Available: {', '.join(score.available_platforms)}")
        if score.missing_platforms:
            print(f"   ❌ Missing: {', '.join(score.missing_platforms)}")
        print(f"   🔧 Adjustments:")
        print(f"      • Confidence: {score.confidence_adjustment:+.2f}")
        print(f"      • Bonuses: {score.bonus_adjustments:+.2f}")
        print(f"      • Compensatory: {score.compensatory_adjustments:+.2f}")
        print(f"      • Penalties: {-score.penalty_adjustments:+.2f}")
        if score.strengths:
            print(f"   💪 Strengths: {', '.join(score.strengths)}")
        if score.weaknesses:
            print(f"   ⚠️  Weaknesses: {', '.join(score.weaknesses)}")
        if score.warnings:
            print(f"   ⚡ Warnings:")
            for warning in score.warnings:
                print(f"      - {warning}")
        print(f"   📋 {score.recommendation}")
        print()
    
    # Generate report
    ranker.generate_adaptive_report("data/adaptive_ranking_report.json")
    print(f"📄 Detailed report saved to: data/adaptive_ranking_report.json")
    print()


if __name__ == "__main__":
    main()
