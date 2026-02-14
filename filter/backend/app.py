from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import json
import os
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from services.scraper import SocialProfileScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load BGE model once at startup
logger.info("=" * 60)
logger.info("Starting Embedding Service")
logger.info("Loading BGE-small-en-v1.5 model...")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
logger.info("✓ Model loaded successfully!")
logger.info("=" * 60)

# Initialize scraper
linkedin_api_key = os.environ.get('LINKEDIN_API_KEY')
github_token = os.environ.get('GITHUB_TOKEN')
logger.info(f"LinkedIn API Key: {'✓ Configured' if linkedin_api_key else '✗ Not set'}")
logger.info(f"GitHub Token: {'✓ Configured' if github_token else '✗ Not set (rate limited)'}")

scraper = SocialProfileScraper(
    linkedin_api_key=linkedin_api_key,
    github_token=github_token
)

DATA_DIR = Path(__file__).parent.parent / 'data'

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check requested")
    return jsonify({"status": "ok", "model": "bge-small-en-v1.5"})

@app.route('/api/embed', methods=['POST'])
def embed_text():
    """Generate embedding for arbitrary text"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            logger.warning("Embed request received with empty text")
            return jsonify({"error": "Text is required"}), 400
        
        logger.info(f"Generating embedding for text (length: {len(text)} chars)")
        
        # Generate embedding
        embedding = model.encode(text, normalize_embeddings=True)
        
        logger.info(f"✓ Embedding generated (dimension: {len(embedding)})")
        
        return jsonify({
            "embedding": embedding.tolist(),
            "dimension": len(embedding)
        })
    
    except Exception as e:
        logger.error(f"Error in embed_text: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/embed-resume', methods=['POST'])
def embed_resume():
    """Generate and save embedding for candidate resume"""
    try:
        data = request.json
        username = data.get('username')
        resume_data = data.get('resume_data')
        
        if not username or not resume_data:
            logger.warning("Resume embed request missing username or resume_data")
            return jsonify({"error": "Username and resume_data are required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Processing resume for candidate: {username}")
        
        # Combine resume fields into single text
        text_parts = [
            resume_data.get('extractedText', ''),
            ' '.join(resume_data.get('skills', [])),
            ' '.join(resume_data.get('education', [])),
            ' '.join(resume_data.get('experience', []))
        ]
        combined_text = ' '.join(filter(None, text_parts))
        logger.info(f"  - Combined text length: {len(combined_text)} chars")
        logger.info(f"  - Skills detected: {len(resume_data.get('skills', []))}")
        
        # Generate embedding
        logger.info("  - Generating embedding...")
        embedding = model.encode(combined_text, normalize_embeddings=True)
        logger.info(f"  ✓ Embedding generated (dimension: {len(embedding)})")
        
        # Save to file
        candidate_dir = DATA_DIR / 'candidates' / username
        candidate_dir.mkdir(parents=True, exist_ok=True)
        
        embedding_data = {
            "username": username,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "model": "bge-small-en-v1.5",
            "created_at": resume_data.get('extractedAt')
        }
        
        embedding_path = candidate_dir / 'embedding.json'
        with open(embedding_path, 'w') as f:
            json.dump(embedding_data, f, indent=2)
        logger.info(f"  ✓ Saved embedding: {embedding_path}")
        
        # Also save resume data
        resume_path = candidate_dir / 'resume.json'
        with open(resume_path, 'w') as f:
            json.dump(resume_data, f, indent=2)
        logger.info(f"  ✓ Saved resume data: {resume_path}")
        logger.info("=" * 60)
        
        return jsonify({
            "success": True,
            "message": f"Embedding saved for {username}",
            "dimension": len(embedding)
        })
    
    except Exception as e:
        logger.error(f"Error in embed_resume: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/embed-job', methods=['POST'])
def embed_job():
    """Generate and save embedding for job posting"""
    try:
        data = request.json
        job_id = data.get('job_id')
        job_data = data.get('job_data')
        
        if not job_id or not job_data:
            logger.warning("Job embed request missing job_id or job_data")
            return jsonify({"error": "job_id and job_data are required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Processing job posting: {job_id}")
        logger.info(f"  - Title: {job_data.get('jobTitle')}")
        logger.info(f"  - Company: {job_data.get('company')}")
        
        # Combine job fields into single text
        text_parts = [
            job_data.get('jobTitle', ''),
            job_data.get('description', ''),
            job_data.get('requirements', ''),
            job_data.get('location', ''),
            job_data.get('jobType', '')
        ]
        combined_text = ' '.join(filter(None, text_parts))
        logger.info(f"  - Combined text length: {len(combined_text)} chars")
        
        # Generate embedding
        logger.info("  - Generating embedding...")
        embedding = model.encode(combined_text, normalize_embeddings=True)
        logger.info(f"  ✓ Embedding generated (dimension: {len(embedding)})")
        
        # Save to file
        job_dir = DATA_DIR / 'jobs' / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        embedding_data = {
            "job_id": job_id,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "model": "bge-small-en-v1.5",
            "created_at": job_data.get('submittedAt')
        }
        
        embedding_path = job_dir / 'embedding.json'
        with open(embedding_path, 'w') as f:
            json.dump(embedding_data, f, indent=2)
        logger.info(f"  ✓ Saved embedding: {embedding_path}")
        
        # Also save job data
        job_path = job_dir / 'job.json'
        with open(job_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        logger.info(f"  ✓ Saved job data: {job_path}")
        logger.info("=" * 60)
        
        return jsonify({
            "success": True,
            "message": f"Embedding saved for job {job_id}",
            "dimension": len(embedding)
        })
    
    except Exception as e:
        logger.error(f"Error in embed_job: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/match-candidates', methods=['POST'])
def match_candidates():
    """Find best matching candidates for a job"""
    try:
        data = request.json
        job_id = data.get('job_id')
        top_k = data.get('top_k', 10)
        
        if not job_id:
            logger.warning("Match candidates request missing job_id")
            return jsonify({"error": "job_id is required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Matching candidates for job: {job_id}")
        
        job_embedding_path = DATA_DIR / 'jobs' / job_id / 'embedding.json'
        if not job_embedding_path.exists():
            logger.error(f"Job {job_id} not found")
            return jsonify({"error": f"Job {job_id} not found"}), 404
        
        with open(job_embedding_path) as f:
            job_data = json.load(f)
            job_embedding = np.array(job_data['embedding'])
        logger.info(f"  ✓ Loaded job embedding")
        
        candidates_dir = DATA_DIR / 'candidates'
        if not candidates_dir.exists():
            logger.warning("No candidates directory found")
            return jsonify({"matches": []})
        
        logger.info(f"  - Scanning candidates...")
        matches = []
        for candidate_dir in candidates_dir.iterdir():
            if not candidate_dir.is_dir():
                continue
            
            embedding_path = candidate_dir / 'embedding.json'
            resume_path = candidate_dir / 'resume.json'
            
            if not embedding_path.exists() or not resume_path.exists():
                continue
            
            with open(embedding_path) as f:
                candidate_data = json.load(f)
                candidate_embedding = np.array(candidate_data['embedding'])
            
            similarity = float(np.dot(job_embedding, candidate_embedding))
            
            with open(resume_path) as f:
                resume_data = json.load(f)
            
            matches.append({
                "username": candidate_data['username'],
                "similarity_score": round(similarity, 4),
                "email": resume_data.get('email'),
                "phone": resume_data.get('phone'),
                "skills": resume_data.get('skills', []),
                "linkedin": resume_data.get('linkedinUrl'),
                "github": resume_data.get('githubUrl')
            })
        
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"  ✓ Found {len(matches)} candidates")
        logger.info(f"  - Returning top {min(top_k, len(matches))} matches")
        if matches:
            logger.info(f"  - Best match: {matches[0]['username']} (score: {matches[0]['similarity_score']})")
        logger.info("=" * 60)
        
        return jsonify({
            "job_id": job_id,
            "total_candidates": len(matches),
            "matches": matches[:top_k]
        })
    
    except Exception as e:
        logger.error(f"Error in match_candidates: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/list-jobs', methods=['GET'])
def list_jobs():
    """List all posted jobs"""
    try:
        logger.info("Listing all posted jobs")
        
        jobs_dir = DATA_DIR / 'jobs'
        if not jobs_dir.exists():
            logger.warning("No jobs directory found")
            return jsonify({"jobs": []})
        
        jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            job_path = job_dir / 'job.json'
            if not job_path.exists():
                continue
            
            with open(job_path) as f:
                job_data = json.load(f)
                job_data['job_id'] = job_dir.name
                jobs.append(job_data)
        
        # Sort by submission date (newest first)
        jobs.sort(key=lambda x: x.get('submittedAt', ''), reverse=True)
        
        logger.info(f"  ✓ Found {len(jobs)} posted jobs")
        
        return jsonify({
            "total_jobs": len(jobs),
            "jobs": jobs
        })
    
    except Exception as e:
        logger.error(f"Error in list_jobs: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/rank-candidates-formula', methods=['POST'])
def rank_candidates_formula():
    """Rank candidates using multi-criteria formula (GitHub, LeetCode, Codeforces, LinkedIn, Resume)"""
    try:
        data = request.json
        job_id = data.get('job_id')
        top_k = data.get('top_k', 10)
        
        if not job_id:
            logger.warning("Rank candidates request missing job_id")
            return jsonify({"error": "job_id is required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Ranking candidates using formula for job: {job_id}")
        
        candidates_dir = DATA_DIR / 'candidates'
        if not candidates_dir.exists():
            logger.warning("No candidates directory found")
            return jsonify({"rankings": []})
        
        # Weights for different platforms
        weights = {
            'github': 0.25,
            'leetcode': 0.20,
            'codeforces': 0.15,
            'linkedin': 0.15,
            'resume': 0.25
        }
        
        logger.info(f"  - Using weights: {weights}")
        logger.info(f"  - Scanning candidates...")
        
        rankings = []
        for candidate_dir in candidates_dir.iterdir():
            if not candidate_dir.is_dir():
                continue
            
            username = candidate_dir.name
            resume_path = candidate_dir / 'resume.json'
            
            if not resume_path.exists():
                continue
            
            # Load resume data
            with open(resume_path) as f:
                resume_data = json.load(f)
            
            # Calculate platform scores
            platform_scores = {}
            available_platforms = []
            
            # GitHub score
            github_path = candidate_dir / 'github.json'
            if github_path.exists():
                with open(github_path) as f:
                    github_data = json.load(f)
                    if 'error' not in github_data:
                        # Score based on repos, stars, followers
                        repos = github_data.get('public_repos', 0)
                        stars = github_data.get('total_stars_earned', 0)
                        followers = github_data.get('followers', 0)
                        
                        github_score = min(100, (repos * 2) + (stars * 0.5) + (followers * 0.3))
                        platform_scores['github'] = github_score
                        available_platforms.append('github')
            
            # LeetCode score
            leetcode_path = candidate_dir / 'leetcode.json'
            if leetcode_path.exists():
                with open(leetcode_path) as f:
                    leetcode_data = json.load(f)
                    if 'error' not in leetcode_data:
                        total_solved = leetcode_data.get('total_solved', 0)
                        easy = leetcode_data.get('easy_solved', 0)
                        medium = leetcode_data.get('medium_solved', 0)
                        hard = leetcode_data.get('hard_solved', 0)
                        
                        # Weighted score: easy=1, medium=2, hard=3
                        leetcode_score = min(100, (easy * 0.2) + (medium * 0.5) + (hard * 1.0))
                        platform_scores['leetcode'] = leetcode_score
                        available_platforms.append('leetcode')
            
            # Codeforces score
            codeforces_path = candidate_dir / 'codeforces.json'
            if codeforces_path.exists():
                with open(codeforces_path) as f:
                    cf_data = json.load(f)
                    if 'error' not in cf_data:
                        rating = cf_data.get('rating', 0)
                        max_rating = cf_data.get('max_rating', 0)
                        contests = cf_data.get('contests_participated', 0)
                        
                        # Score based on rating (0-3000 scale)
                        codeforces_score = min(100, (max_rating / 30) + (contests * 0.5))
                        platform_scores['codeforces'] = codeforces_score
                        available_platforms.append('codeforces')
            
            # LinkedIn score (basic - just presence)
            linkedin_path = candidate_dir / 'linkedin.json'
            if linkedin_path.exists():
                with open(linkedin_path) as f:
                    linkedin_data = json.load(f)
                    if 'error' not in linkedin_data:
                        # Score based on profile completeness
                        linkedin_score = 70  # Base score for having LinkedIn
                        if linkedin_data.get('experiences'):
                            linkedin_score += 15
                        if linkedin_data.get('education'):
                            linkedin_score += 15
                        platform_scores['linkedin'] = min(100, linkedin_score)
                        available_platforms.append('linkedin')
            
            # Resume score
            skills_count = len(resume_data.get('skills', []))
            education_count = len(resume_data.get('education', []))
            experience_count = len(resume_data.get('experience', []))
            
            resume_score = min(100, (skills_count * 3) + (education_count * 10) + (experience_count * 5))
            platform_scores['resume'] = resume_score
            available_platforms.append('resume')
            
            # Calculate weighted score with adaptive weights
            if not available_platforms:
                continue
            
            # Redistribute weights for missing platforms
            total_available_weight = sum(weights[p] for p in available_platforms if p in weights)
            adjusted_weights = {
                p: weights[p] / total_available_weight
                for p in available_platforms if p in weights
            }
            
            # Calculate final score
            final_score = sum(
                platform_scores[p] * adjusted_weights[p]
                for p in available_platforms if p in adjusted_weights
            )
            
            # Calculate confidence based on data completeness
            completeness = len(available_platforms) / 5
            confidence = 0.70 + (0.30 * completeness)
            
            rankings.append({
                "username": username,
                "final_score": round(final_score, 2),
                "confidence": round(confidence, 2),
                "completeness": round(completeness * 100, 1),
                "email": resume_data.get('email'),
                "phone": resume_data.get('phone'),
                "skills": resume_data.get('skills', []),
                "linkedin": resume_data.get('linkedinUrl'),
                "github": resume_data.get('githubUrl'),
                "platform_scores": {k: round(v, 2) for k, v in platform_scores.items()},
                "available_platforms": available_platforms,
                "adjusted_weights": {k: round(v, 3) for k, v in adjusted_weights.items()}
            })
        
        # Sort by final score (descending)
        rankings.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"  ✓ Ranked {len(rankings)} candidates")
        if rankings:
            logger.info(f"  - Top candidate: {rankings[0]['username']} (score: {rankings[0]['final_score']})")
        logger.info("=" * 60)
        
        return jsonify({
            "job_id": job_id,
            "total_candidates": len(rankings),
            "ranking_method": "multi-criteria-formula",
            "weights_used": weights,
            "rankings": rankings[:top_k]
        })
    
    except Exception as e:
        logger.error(f"Error in rank_candidates_formula: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    """Find best matching jobs for a candidate"""
    try:
        data = request.json
        username = data.get('username')
        top_k = data.get('top_k', 10)
        
        if not username:
            logger.warning("Match jobs request missing username")
            return jsonify({"error": "username is required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Matching jobs for candidate: {username}")
        
        candidate_embedding_path = DATA_DIR / 'candidates' / username / 'embedding.json'
        if not candidate_embedding_path.exists():
            logger.error(f"Candidate {username} not found")
            return jsonify({"error": f"Candidate {username} not found"}), 404
        
        with open(candidate_embedding_path) as f:
            candidate_data = json.load(f)
            candidate_embedding = np.array(candidate_data['embedding'])
        logger.info(f"  ✓ Loaded candidate embedding")
        
        jobs_dir = DATA_DIR / 'jobs'
        if not jobs_dir.exists():
            logger.warning("No jobs directory found")
            return jsonify({"matches": []})
        
        logger.info(f"  - Scanning jobs...")
        matches = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            embedding_path = job_dir / 'embedding.json'
            job_path = job_dir / 'job.json'
            
            if not embedding_path.exists() or not job_path.exists():
                continue
            
            with open(embedding_path) as f:
                job_data = json.load(f)
                job_embedding = np.array(job_data['embedding'])
            
            similarity = float(np.dot(candidate_embedding, job_embedding))
            
            with open(job_path) as f:
                job_info = json.load(f)
            
            matches.append({
                "job_id": job_data['job_id'],
                "similarity_score": round(similarity, 4),
                "job_title": job_info.get('jobTitle'),
                "company": job_info.get('company'),
                "location": job_info.get('location'),
                "job_type": job_info.get('jobType'),
                "salary": job_info.get('salary')
            })
        
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"  ✓ Found {len(matches)} jobs")
        logger.info(f"  - Returning top {min(top_k, len(matches))} matches")
        if matches:
            logger.info(f"  - Best match: {matches[0]['job_title']} at {matches[0]['company']} (score: {matches[0]['similarity_score']})")
        logger.info("=" * 60)
        
        return jsonify({
            "username": username,
            "total_jobs": len(matches),
            "matches": matches[:top_k]
        })
    
    except Exception as e:
        logger.error(f"Error in match_jobs: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetch-profile-data', methods=['POST'])
def fetch_profile_data():
    """Fetch data from LinkedIn, GitHub, LeetCode, Codeforces URLs using scraper"""
    try:
        data = request.json
        username = data.get('username')
        urls = data.get('urls', {})
        
        if not username:
            logger.warning("Fetch profile request missing username")
            return jsonify({"error": "username is required"}), 400
        
        logger.info("=" * 60)
        logger.info(f"Fetching profile data for: {username}")
        
        profile_data = scraper.scrape_all(urls)
        
        candidate_dir = DATA_DIR / 'candidates' / username
        candidate_dir.mkdir(parents=True, exist_ok=True)
        
        for platform, platform_data in profile_data.items():
            if platform_data and 'error' not in platform_data:
                platform_file = candidate_dir / f'{platform}.json'
                with open(platform_file, 'w') as f:
                    json.dump(platform_data, f, indent=2)
                logger.info(f"  ✓ Saved {platform} data")
            else:
                logger.warning(f"  ⚠ {platform}: {platform_data.get('error', 'Unknown error')}")
        
        metadata = {
            "username": username,
            "profile_urls": urls,
            "fetched_at": datetime.now().isoformat(),
            "platforms_fetched": [p for p, d in profile_data.items() if 'error' not in d]
        }
        metadata_file = candidate_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("=" * 60)
        
        return jsonify({
            "success": True,
            "message": f"Profile data fetched for {username}",
            "platforms_fetched": metadata["platforms_fetched"],
            "results": profile_data
        })
    
    except Exception as e:
        logger.error(f"Error fetching profile data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create data directories
    (DATA_DIR / 'candidates').mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'jobs').mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info("Server starting on http://0.0.0.0:5000")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
