"""
Complete Candidate Evaluation System

Integrates:
1. Profile scraping (scraper.py)
2. Resume parsing (resume_parser.py)
3. Company questions (company_questions.py)
4. Candidate ranking (candidate_ranker.py)

Complete workflow for candidate evaluation and shortlisting.
"""

import os
import json
from typing import List, Optional
from datetime import datetime

from scraper import CandidateProfileScraper
from candidate_manager import CandidateProfileManager
from resume_parser import ResumeParser
from company_questions import CompanyQuestionsManager, Answer
from candidate_ranker import CandidateRanker, ScoringWeights


class CompleteCandidateEvaluator:
    """
    End-to-end candidate evaluation system
    """
    
    def __init__(
        self,
        candidates_folder: str = "data/candidates",
        job_requirements: Optional[dict] = None,
        ranking_weights: Optional[ScoringWeights] = None
    ):
        """
        Initialize evaluator
        
        Args:
            candidates_folder: Folder to store candidate data
            job_requirements: Job requirements for resume matching
            ranking_weights: Custom weights for ranking
        """
        self.candidates_folder = candidates_folder
        self.job_requirements = job_requirements or {}
        
        # Initialize components
        self.scraper = CandidateProfileScraper()
        self.profile_manager = CandidateProfileManager(base_folder=candidates_folder)
        self.resume_parser = ResumeParser(job_requirements=job_requirements)
        self.questions_manager = CompanyQuestionsManager()
        self.ranker = CandidateRanker(weights=ranking_weights)
        
        # Ensure folder exists
        os.makedirs(candidates_folder, exist_ok=True)
    
    def process_candidate(
        self,
        candidate_name: str,
        profile_urls: dict,
        resume_file: Optional[str] = None,
        assessment_answers: Optional[List[Answer]] = None,
        additional_info: Optional[dict] = None
    ) -> str:
        """
        Process a single candidate through complete pipeline
        
        Args:
            candidate_name: Candidate's name
            profile_urls: Dict with platform URLs (codeforces, leetcode, linkedin, github)
            resume_file: Path to resume file (PDF, DOCX, TXT)
            assessment_answers: List of Answer objects for company questions
            additional_info: Additional metadata
        
        Returns:
            Path to candidate folder
        """
        print(f"\n{'='*70}")
        print(f"PROCESSING CANDIDATE: {candidate_name}")
        print(f"{'='*70}\n")
        
        # Step 1: Scrape profiles
        print("📡 Step 1: Scraping profiles...")
        profile_data = {}
        
        for platform, url in profile_urls.items():
            if url:
                print(f"  - Scraping {platform}...")
                data = self.scraper.scrape_profile(platform, url)
                profile_data[platform] = data
        
        # Step 2: Create candidate folder and save profile data
        print("\n💾 Step 2: Saving profile data...")
        candidate_folder = self.profile_manager.create_candidate_folder(
            candidate_name=candidate_name,
            profile_urls=profile_urls,
            additional_info=additional_info
        )
        
        for platform, data in profile_data.items():
            self.profile_manager.save_platform_data(candidate_name, platform, data)
        
        # Step 3: Parse resume if provided
        if resume_file and os.path.exists(resume_file):
            print("\n📄 Step 3: Parsing resume...")
            resume_analysis = self.resume_parser.parse_file(resume_file, candidate_name)
            
            # Save resume analysis
            resume_output = os.path.join(candidate_folder, "resume_analysis.json")
            self.resume_parser.save_analysis(resume_analysis, resume_output)
            
            print(f"  ✅ Resume score: {resume_analysis.score:.2f}/100")
        else:
            print("\n⚠️  Step 3: No resume provided, skipping...")
        
        # Step 4: Process company questions if provided
        if assessment_answers:
            print("\n❓ Step 4: Evaluating company questions...")
            
            # Create assessment with provided answers
            assessment = self.questions_manager.create_assessment(
                candidate_name=candidate_name,
                assessment_id=f"ASSESS_{candidate_name.replace(' ', '_')}",
                question_ids=[a.question_id for a in assessment_answers]
            )
            assessment.answers = assessment_answers
            
            # Evaluate
            assessment = self.questions_manager.evaluate_assessment(assessment)
            
            # Save
            questions_output = os.path.join(candidate_folder, "company_questions.json")
            self.questions_manager.save_assessment(assessment, questions_output)
            
            print(f"  ✅ Questions score: {assessment.percentage_score:.2f}%")
        else:
            print("\n⚠️  Step 4: No assessment answers provided, skipping...")
        
        print(f"\n✅ Candidate processing complete!")
        print(f"📁 Data saved to: {candidate_folder}")
        
        return candidate_folder
    
    def rank_all_candidates(self, top_n: int = 5) -> List:
        """
        Rank all candidates and get top N
        
        Args:
            top_n: Number of top candidates to return
        
        Returns:
            List of top CandidateScore objects
        """
        print(f"\n{'='*70}")
        print("RANKING ALL CANDIDATES")
        print(f"{'='*70}\n")
        
        # Rank candidates
        scores = self.ranker.rank_candidates(self.candidates_folder)
        
        if not scores:
            print("❌ No candidates found to rank!")
            return []
        
        # Display results
        print(f"\n{'='*70}")
        print(f"TOP {top_n} CANDIDATES")
        print(f"{'='*70}\n")
        
        top_candidates = self.ranker.get_top_candidates(top_n)
        
        for i, score in enumerate(top_candidates, 1):
            print(f"🏆 Rank #{i}: {score.candidate_name}")
            print(f"   Total Score: {score.total_score:.2f}/100")
            print(f"   Breakdown:")
            print(f"     - Codeforces: {score.codeforces_score:.1f} (weighted: {score.codeforces_weighted:.1f})")
            print(f"     - LeetCode: {score.leetcode_score:.1f} (weighted: {score.leetcode_weighted:.1f})")
            print(f"     - GitHub: {score.github_score:.1f} (weighted: {score.github_weighted:.1f})")
            print(f"     - LinkedIn: {score.linkedin_score:.1f} (weighted: {score.linkedin_weighted:.1f})")
            print(f"     - Resume: {score.resume_score:.1f} (weighted: {score.resume_weighted:.1f})")
            print(f"     - Questions: {score.company_questions_score:.1f} (weighted: {score.company_questions_weighted:.1f})")
            print(f"   Strengths: {', '.join(score.strengths) if score.strengths else 'None'}")
            print(f"   Weaknesses: {', '.join(score.weaknesses) if score.weaknesses else 'None'}")
            print(f"   Recommendation: {score.recommendation}")
            print()
        
        # Generate report
        report_file = os.path.join(self.candidates_folder, "..", "ranking_report.json")
        self.ranker.generate_ranking_report(report_file)
        print(f"📄 Detailed report saved to: {report_file}")
        
        return top_candidates
    
    def batch_process_from_csv(
        self,
        csv_file: str,
        resume_folder: Optional[str] = None
    ):
        """
        Process multiple candidates from CSV file
        
        CSV Format:
        name,codeforces,leetcode,linkedin,github,email,phone,position
        
        Args:
            csv_file: Path to CSV file
            resume_folder: Folder containing resume files (named as {name}.pdf)
        """
        import csv
        
        print(f"\n{'='*70}")
        print("BATCH PROCESSING FROM CSV")
        print(f"{'='*70}\n")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                candidate_name = row.get('name', '').strip()
                if not candidate_name:
                    continue
                
                # Build profile URLs
                profile_urls = {
                    'codeforces': row.get('codeforces', '').strip(),
                    'leetcode': row.get('leetcode', '').strip(),
                    'linkedin': row.get('linkedin', '').strip(),
                    'github': row.get('github', '').strip()
                }
                
                # Additional info
                additional_info = {
                    'email': row.get('email', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'applied_for': row.get('position', '').strip()
                }
                
                # Check for resume
                resume_file = None
                if resume_folder:
                    for ext in ['.pdf', '.docx', '.txt']:
                        potential_file = os.path.join(resume_folder, f"{candidate_name}{ext}")
                        if os.path.exists(potential_file):
                            resume_file = potential_file
                            break
                
                # Process candidate
                try:
                    self.process_candidate(
                        candidate_name=candidate_name,
                        profile_urls=profile_urls,
                        resume_file=resume_file,
                        additional_info=additional_info
                    )
                except Exception as e:
                    print(f"❌ Error processing {candidate_name}: {e}")
                    continue
        
        print(f"\n✅ Batch processing complete!")


def example_single_candidate():
    """Example: Process a single candidate"""
    
    # Define job requirements
    job_requirements = {
        'required_skills': ['python', 'java', 'algorithms'],
        'preferred_skills': ['react', 'docker', 'aws'],
        'min_experience': 1
    }
    
    # Define custom weights
    weights = ScoringWeights(
        codeforces_weight=0.15,
        leetcode_weight=0.20,
        github_weight=0.25,
        linkedin_weight=0.15,
        resume_weight=0.15,
        company_questions_weight=0.10
    )
    
    # Create evaluator
    evaluator = CompleteCandidateEvaluator(
        job_requirements=job_requirements,
        ranking_weights=weights
    )
    
    # Process candidate
    evaluator.process_candidate(
        candidate_name="John Doe",
        profile_urls={
            'codeforces': 'https://codeforces.com/profile/tourist',
            'leetcode': 'https://leetcode.com/u/tourist/',
            'linkedin': 'https://linkedin.com/in/johndoe',
            'github': 'https://github.com/johndoe'
        },
        resume_file="resumes/john_doe.pdf",  # Optional
        additional_info={
            'email': 'john@example.com',
            'phone': '+1-234-567-8900',
            'applied_for': 'Software Engineer'
        }
    )
    
    # Rank all candidates
    evaluator.rank_all_candidates(top_n=5)


def example_batch_processing():
    """Example: Batch process from CSV"""
    
    evaluator = CompleteCandidateEvaluator()
    
    # Process from CSV
    evaluator.batch_process_from_csv(
        csv_file="candidates_template.csv",
        resume_folder="resumes"  # Optional
    )
    
    # Rank all
    evaluator.rank_all_candidates(top_n=5)


def main():
    """Main execution"""
    print("=" * 70)
    print("COMPLETE CANDIDATE EVALUATION SYSTEM")
    print("=" * 70)
    print()
    print("This system integrates:")
    print("  1. Profile scraping (Codeforces, LeetCode, LinkedIn, GitHub)")
    print("  2. Resume parsing and analysis")
    print("  3. Company-specific questions assessment")
    print("  4. Multi-criteria ranking algorithm")
    print()
    print("Choose an option:")
    print("  1. Process single candidate")
    print("  2. Batch process from CSV")
    print("  3. Rank existing candidates")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        example_single_candidate()
    elif choice == "2":
        example_batch_processing()
    elif choice == "3":
        evaluator = CompleteCandidateEvaluator()
        evaluator.rank_all_candidates(top_n=5)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
