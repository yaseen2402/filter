"""
Test Complete Candidate Evaluation System

Demonstrates the full workflow with existing candidate data.
"""

import os
import json
from resume_parser import ResumeParser
from company_questions import CompanyQuestionsManager, Answer, QuestionType, DifficultyLevel, Question
from candidate_ranker import CandidateRanker, ScoringWeights


def test_resume_parser():
    """Test resume parser with sample text"""
    print("\n" + "="*70)
    print("TEST 1: RESUME PARSER")
    print("="*70)
    
    sample_resume = """
    Mohammed Junaid Adil
    junaid@example.com | +91-9876543210
    
    EDUCATION
    Bachelor of Technology in Computer Science
    Osmania University, 2024
    
    EXPERIENCE
    Software Engineering Intern at Tech Corp (2023-2024)
    - Developed web applications using Python and React
    - Worked with AWS and Docker
    
    SKILLS
    Python, Java, JavaScript, React, Django, SQL, Docker, AWS, Git
    
    PROJECTS
    - E-commerce Platform: Built using Django and React
    - ML Model: Developed predictive model using TensorFlow
    - Chat Application: Real-time chat using WebSockets
    
    CERTIFICATIONS
    - AWS Certified Developer
    - Python Programming Certificate
    """
    
    parser = ResumeParser(job_requirements={
        'required_skills': ['python', 'java', 'sql'],
        'preferred_skills': ['react', 'docker', 'aws'],
        'min_experience': 1
    })
    
    analysis = parser.parse_text(sample_resume, "Mohammed Junaid Adil")
    
    print(f"\n📄 Candidate: {analysis.candidate_name}")
    print(f"📧 Email: {analysis.email}")
    print(f"📱 Phone: {analysis.phone}")
    print(f"\n🎓 Education: {analysis.education_level}")
    print(f"💼 Experience: {analysis.total_experience_years} years")
    print(f"💻 Technical Skills ({len(analysis.technical_skills)}): {', '.join(analysis.technical_skills[:10])}")
    print(f"📜 Certifications: {len(analysis.certifications)}")
    print(f"🚀 Projects: {len(analysis.projects)}")
    print(f"\n📊 Resume Score: {analysis.score:.2f}/100")
    
    # Save to candidate folder
    candidate_folder = "data/candidates/Mohammed_Junaid_Adil"
    if os.path.exists(candidate_folder):
        output_file = os.path.join(candidate_folder, "resume_analysis.json")
        parser.save_analysis(analysis, output_file)
    
    return analysis


def test_company_questions():
    """Test company questions system"""
    print("\n" + "="*70)
    print("TEST 2: COMPANY QUESTIONS")
    print("="*70)
    
    # Create manager
    manager = CompanyQuestionsManager()
    
    # Create sample questions manually
    questions = [
        Question(
            id="q1",
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.EASY,
            question_text="What is the time complexity of binary search?",
            points=10,
            options=["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            correct_answer="O(log n)",
            category="Algorithms"
        ),
        Question(
            id="q2",
            type=QuestionType.CODING,
            difficulty=DifficultyLevel.MEDIUM,
            question_text="Write a function to reverse a linked list",
            points=20,
            category="Data Structures"
        ),
        Question(
            id="q3",
            type=QuestionType.SCENARIO,
            difficulty=DifficultyLevel.HARD,
            question_text="How would you debug a production system with high latency?",
            points=30,
            category="System Design"
        )
    ]
    
    manager.questions_bank = questions
    
    # Create assessment
    from company_questions import Assessment
    assessment = Assessment(
        candidate_name="Mohammed Junaid Adil",
        assessment_id="ASSESS_MJA_001",
        questions=questions,
        answers=[],
        total_points=60
    )
    
    # Simulate answers
    assessment.answers = [
        Answer(
            question_id="q1",
            answer="O(log n)",
            time_taken_seconds=30
        ),
        Answer(
            question_id="q2",
            answer="def reverse(head): ...",
            code_submission="# Code here",
            test_cases_passed=2,
            test_cases_total=2
        ),
        Answer(
            question_id="q3",
            answer="I would start by checking monitoring dashboards, analyze logs, identify bottlenecks...",
            time_taken_seconds=300
        )
    ]
    
    # Evaluate
    assessment = manager.evaluate_assessment(assessment)
    
    print(f"\n👤 Candidate: {assessment.candidate_name}")
    print(f"📝 Questions: {len(assessment.questions)}")
    print(f"💯 Total Points: {assessment.total_points}")
    print(f"✅ Points Earned: {assessment.points_earned:.1f}")
    print(f"📊 Percentage: {assessment.percentage_score:.2f}%")
    print(f"\n🎯 Score for Ranking: {manager.calculate_score(assessment):.2f}/100")
    
    # Save to candidate folder
    candidate_folder = "data/candidates/Mohammed_Junaid_Adil"
    if os.path.exists(candidate_folder):
        output_file = os.path.join(candidate_folder, "company_questions.json")
        manager.save_assessment(assessment, output_file)
    
    return assessment


def test_ranking_with_all_data():
    """Test ranking with complete data"""
    print("\n" + "="*70)
    print("TEST 3: COMPLETE RANKING")
    print("="*70)
    
    # Create ranker
    weights = ScoringWeights(
        codeforces_weight=0.15,
        leetcode_weight=0.20,
        github_weight=0.25,
        linkedin_weight=0.15,
        resume_weight=0.15,
        company_questions_weight=0.10
    )
    
    ranker = CandidateRanker(weights=weights)
    
    # Rank all candidates
    scores = ranker.rank_candidates("data/candidates")
    
    if not scores:
        print("\n❌ No candidates found!")
        return
    
    print(f"\n📊 Total Candidates Evaluated: {len(scores)}")
    print("\n" + "="*70)
    print("RANKING RESULTS")
    print("="*70)
    
    for score in scores:
        print(f"\n🏆 Rank #{score.rank}: {score.candidate_name}")
        print(f"   Total Score: {score.total_score:.2f}/100")
        print(f"   Breakdown:")
        print(f"     • Codeforces: {score.codeforces_score:.1f}/100 (weighted: {score.codeforces_weighted:.1f})")
        print(f"     • LeetCode: {score.leetcode_score:.1f}/100 (weighted: {score.leetcode_weighted:.1f})")
        print(f"     • GitHub: {score.github_score:.1f}/100 (weighted: {score.github_weighted:.1f})")
        print(f"     • LinkedIn: {score.linkedin_score:.1f}/100 (weighted: {score.linkedin_weighted:.1f})")
        print(f"     • Resume: {score.resume_score:.1f}/100 (weighted: {score.resume_weighted:.1f})")
        print(f"     • Questions: {score.company_questions_score:.1f}/100 (weighted: {score.company_questions_weighted:.1f})")
        
        if score.strengths:
            print(f"   💪 Strengths: {', '.join(score.strengths)}")
        if score.weaknesses:
            print(f"   ⚠️  Weaknesses: {', '.join(score.weaknesses)}")
        
        print(f"   📋 {score.recommendation}")
    
    # Generate report
    report_file = "data/ranking_report.json"
    ranker.generate_ranking_report(report_file)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return scores


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPLETE CANDIDATE EVALUATION SYSTEM - TEST SUITE")
    print("="*70)
    print("\nThis test demonstrates:")
    print("  1. Resume parsing and scoring")
    print("  2. Company questions assessment")
    print("  3. Complete ranking with all data sources")
    print()
    
    try:
        # Test 1: Resume Parser
        resume_analysis = test_resume_parser()
        
        # Test 2: Company Questions
        assessment = test_company_questions()
        
        # Test 3: Complete Ranking
        scores = test_ranking_with_all_data()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext Steps:")
        print("  1. Check data/candidates/Mohammed_Junaid_Adil/ for new files")
        print("  2. Review data/ranking_report.json for complete rankings")
        print("  3. Use complete_candidate_evaluation.py for production workflow")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
