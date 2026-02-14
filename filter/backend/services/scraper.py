import requests
import json
from typing import Dict, Optional
from urllib.parse import urlparse

class SocialProfileScraper:
    """Scraper for Codeforces, LeetCode, and LinkedIn profiles"""
    
    def __init__(self, linkedin_api_key: Optional[str] = None, linkedin_provider: str = "scrapingdog", github_token: Optional[str] = None):
        self.codeforces_api = "https://codeforces.com/api"
        self.leetcode_api = "https://leetcode-stats-api.herokuapp.com"
        self.linkedin_api_key = linkedin_api_key
        self.linkedin_provider = linkedin_provider  # "scrapingdog" or "brightdata"
        self.github_token = github_token
        self.github_api = "https://api.github.com"
    
    def extract_username_from_url(self, url: str, platform: str) -> Optional[str]:
        """Extract username from profile URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if platform == "codeforces":
                # URL format: https://codeforces.com/profile/{username}
                if 'profile' in path_parts:
                    idx = path_parts.index('profile')
                    return path_parts[idx + 1] if idx + 1 < len(path_parts) else None
            
            elif platform == "leetcode":
                # URL format: https://leetcode.com/{username} or https://leetcode.com/u/{username}
                if path_parts:
                    return path_parts[-1] if path_parts[-1] != 'u' else path_parts[-2] if len(path_parts) > 1 else None
            
            elif platform == "linkedin":
                # URL format: https://linkedin.com/in/{username}
                if 'in' in path_parts:
                    idx = path_parts.index('in')
                    return path_parts[idx + 1] if idx + 1 < len(path_parts) else None
            
            elif platform == "github":
                # URL format: https://github.com/{username}
                if path_parts:
                    # Filter out common GitHub paths that aren't usernames
                    username = path_parts[0] if path_parts else None
                    if username and username not in ['orgs', 'topics', 'collections', 'events', 'marketplace', 'explore']:
                        return username
            
            return None
        except Exception as e:
            print(f"Error extracting username: {e}")
            return None
    
    def scrape_codeforces(self, url: str) -> Dict:
        """Scrape Codeforces profile data"""
        username = self.extract_username_from_url(url, "codeforces")
        
        if not username:
            return {"error": "Invalid Codeforces URL", "platform": "codeforces"}
        
        try:
            # Get user info
            user_response = requests.get(f"{self.codeforces_api}/user.info?handles={username}")
            user_data = user_response.json()
            
            if user_data.get("status") != "OK":
                return {"error": "User not found", "platform": "codeforces", "username": username}
            
            user = user_data["result"][0]
            
            # Get user rating history
            rating_response = requests.get(f"{self.codeforces_api}/user.rating?handle={username}")
            rating_data = rating_response.json()
            
            contests_participated = len(rating_data.get("result", [])) if rating_data.get("status") == "OK" else 0
            
            return {
                "platform": "codeforces",
                "username": user.get("handle"),
                "rating": user.get("rating"),
                "max_rating": user.get("maxRating"),
                "rank": user.get("rank"),
                "max_rank": user.get("maxRank"),
                "contribution": user.get("contribution"),
                "contests_participated": contests_participated,
                "friend_count": user.get("friendOfCount"),
                "profile_url": url
            }
        
        except Exception as e:
            return {"error": str(e), "platform": "codeforces", "username": username}

    def scrape_leetcode(self, url: str) -> Dict:
        """Scrape LeetCode profile data using community API"""
        username = self.extract_username_from_url(url, "leetcode")
        
        if not username:
            return {"error": "Invalid LeetCode URL", "platform": "leetcode"}
        
        try:
            # Using leetcode-stats-api (more reliable for stats)
            api_url = f"https://leetcode-stats-api.herokuapp.com/{username}"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code != 200:
                return {"error": "User not found or API unavailable", "platform": "leetcode", "username": username}
            
            data = response.json()
            
            # Check if the API returned an error
            if data.get("status") == "error":
                return {"error": data.get("message", "Unknown error"), "platform": "leetcode", "username": username}
            
            return {
                "platform": "leetcode",
                "username": username,
                "ranking": data.get("ranking"),
                "reputation": data.get("reputation"),
                "total_solved": data.get("totalSolved"),
                "total_questions": data.get("totalQuestions"),
                "easy_solved": data.get("easySolved"),
                "total_easy": data.get("totalEasy"),
                "medium_solved": data.get("mediumSolved"),
                "total_medium": data.get("totalMedium"),
                "hard_solved": data.get("hardSolved"),
                "total_hard": data.get("totalHard"),
                "acceptance_rate": data.get("acceptanceRate"),
                "contribution_points": data.get("contributionPoints"),
                "profile_url": url
            }
        
        except Exception as e:
            return {"error": str(e), "platform": "leetcode", "username": username}
    
    def scrape_linkedin(self, url: str) -> Dict:
        """Scrape LinkedIn profile data using ScrapingDog or Bright Data API"""
        
        if not self.linkedin_api_key:
            return {
                "platform": "linkedin",
                "error": "No API key provided",
                "url": url,
                "note": "Set LINKEDIN_API_KEY environment variable. Providers: ScrapingDog (1000 free calls) or Bright Data (free trial)"
            }
        
        try:
            if self.linkedin_provider == "scrapingdog":
                return self._scrape_linkedin_scrapingdog(url)
            elif self.linkedin_provider == "brightdata":
                return self._scrape_linkedin_brightdata(url)
            else:
                return {
                    "platform": "linkedin",
                    "error": f"Unknown provider: {self.linkedin_provider}",
                    "url": url,
                    "note": "Supported providers: 'scrapingdog' or 'brightdata'"
                }
        
        except Exception as e:
            return {"error": str(e), "platform": "linkedin", "url": url}
    
    def _scrape_linkedin_scrapingdog(self, url: str) -> Dict:
        """Scrape LinkedIn using ScrapingDog API"""
        try:
            # Extract profile ID from URL (e.g., "williamhgates" from linkedin.com/in/williamhgates)
            profile_id = self.extract_username_from_url(url, "linkedin")
            
            print(f"  - Extracted LinkedIn profile ID: {profile_id} from URL: {url}")
            
            if not profile_id:
                return {
                    "platform": "linkedin",
                    "error": "Could not extract profile ID from URL",
                    "url": url,
                    "provider": "scrapingdog"
                }
            
            # ScrapingDog uses /profile endpoint with just the ID
            api_url = "https://api.scrapingdog.com/profile/"
            params = {
                "api_key": self.linkedin_api_key,
                "type": "profile",
                "id": profile_id
                # Note: "premium" parameter removed - it may require paid plan
                # Add "premium": "true" if you have a paid ScrapingDog plan
            }
            
            print(f"  - Calling ScrapingDog API with profile_id: {profile_id}")
            response = requests.get(api_url, params=params, timeout=45)
            
            if response.status_code != 200:
                # Try to parse error message from response
                try:
                    error_data = response.json()
                    api_message = error_data.get('message', '')
                except:
                    api_message = response.text[:300]
                
                error_msg = f"API returned status {response.status_code}"
                if response.status_code == 403:
                    error_msg += " - API key may be invalid, expired, or out of credits."
                elif response.status_code == 401:
                    error_msg += " - Unauthorized. Check your API key."
                elif response.status_code == 400:
                    if "Free pack allows" in api_message:
                        error_msg = "Free plan limit reached. " + api_message
                    else:
                        error_msg += " - Bad request. The profile ID may be invalid or the profile doesn't exist/isn't public."
                
                print(f"  - LinkedIn API error: {error_msg}")
                
                return {
                    "platform": "linkedin",
                    "error": error_msg,
                    "message": api_message,
                    "url": url,
                    "profile_id": profile_id,
                    "provider": "scrapingdog",
                    "note": "LinkedIn scraping is optional. System works with resume + GitHub + LeetCode + Codeforces data."
                }
            
            data = response.json()
            
            # ScrapingDog returns a list with one profile object
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            elif not isinstance(data, dict):
                return {
                    "platform": "linkedin",
                    "error": "Unexpected response format from API",
                    "url": url,
                    "provider": "scrapingdog"
                }
            
            # Extract profile data from ScrapingDog response
            return {
                "platform": "linkedin",
                "full_name": data.get("fullName") or data.get("full_name") or data.get("name"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "headline": data.get("headline"),
                "summary": data.get("summary") or data.get("about"),
                "location": data.get("location") or data.get("city"),
                "connections": data.get("connections") or data.get("connectionsCount"),
                "follower_count": data.get("followers") or data.get("followersCount") or data.get("follower_count"),
                "profile_pic_url": data.get("profile_photo") or data.get("profile_picture") or data.get("avatar") or data.get("profilePicture"),
                "background_image_url": data.get("background_cover_image_url"),
                
                # Description (often contains education/work info)
                "description": data.get("description"),
                
                # Experience
                "experiences": [
                    {
                        "title": exp.get("position") or exp.get("title"),
                        "company": exp.get("company_name") or exp.get("company") or exp.get("companyName"),
                        "company_url": exp.get("company_url"),
                        "company_image": exp.get("company_image"),
                        "location": exp.get("location"),
                        "start_date": exp.get("starts_at") or exp.get("start_date") or exp.get("startDate"),
                        "end_date": exp.get("ends_at") or exp.get("end_date") or exp.get("endDate"),
                        "duration": exp.get("duration"),
                        "description": exp.get("summary") or exp.get("description")
                    }
                    for exp in (data.get("experience", []) or data.get("experiences", []))
                ],
                
                # Education
                "education": [
                    {
                        "school": edu.get("school_name") or edu.get("school") or edu.get("institution") or edu.get("schoolName"),
                        "school_url": edu.get("school_url"),
                        "degree": edu.get("degree_name") or edu.get("degree") or edu.get("degreeName"),
                        "field_of_study": edu.get("field_of_study") or edu.get("fieldOfStudy"),
                        "start_date": edu.get("starts_at") or edu.get("start_date") or edu.get("startDate"),
                        "end_date": edu.get("ends_at") or edu.get("end_date") or edu.get("endDate"),
                        "grade": edu.get("grade"),
                        "activities": edu.get("activities"),
                        "description": edu.get("description")
                    }
                    for edu in (data.get("education", []) or data.get("educations", []))
                ] if data.get("education") or data.get("educations") else [],
                
                # Publications
                "publications": [
                    {
                        "title": pub.get("title") or pub.get("name"),
                        "publisher": pub.get("publisher"),
                        "published_date": pub.get("published_on") or pub.get("date"),
                        "description": pub.get("description"),
                        "url": pub.get("url")
                    }
                    for pub in (data.get("publications", []) or [])
                ] if data.get("publications") else [],
                
                # Projects
                "projects": [
                    {
                        "title": proj.get("title") or proj.get("name"),
                        "description": proj.get("description"),
                        "start_date": proj.get("starts_at") or proj.get("start_date"),
                        "end_date": proj.get("ends_at") or proj.get("end_date"),
                        "url": proj.get("url")
                    }
                    for proj in (data.get("projects", []) or [])
                ] if data.get("projects") else [],
                
                # Certifications
                "certifications": [
                    {
                        "name": cert.get("name") or cert.get("title"),
                        "authority": cert.get("authority") or cert.get("issuer"),
                        "license_number": cert.get("license_number"),
                        "start_date": cert.get("starts_at") or cert.get("start_date"),
                        "end_date": cert.get("ends_at") or cert.get("end_date"),
                        "url": cert.get("url")
                    }
                    for cert in (data.get("certification", []) or data.get("certifications", []) or [])
                ] if data.get("certification") or data.get("certifications") else [],
                
                # Courses
                "courses": [
                    {
                        "name": course.get("name") or course.get("title"),
                        "number": course.get("number")
                    }
                    for course in (data.get("courses", []) or [])
                ] if data.get("courses") else [],
                
                # Languages
                "languages": [
                    {
                        "name": lang.get("name"),
                        "proficiency": lang.get("proficiency")
                    }
                    for lang in (data.get("languages", []) or [])
                ] if data.get("languages") else [],
                
                # Volunteer Experience
                "volunteering": [
                    {
                        "role": vol.get("role") or vol.get("title"),
                        "organization": vol.get("organization") or vol.get("company"),
                        "cause": vol.get("cause"),
                        "start_date": vol.get("starts_at") or vol.get("start_date"),
                        "end_date": vol.get("ends_at") or vol.get("end_date"),
                        "description": vol.get("description")
                    }
                    for vol in (data.get("volunteering", []) or data.get("volunteer", []) or [])
                ] if data.get("volunteering") or data.get("volunteer") else [],
                
                # Awards & Honors
                "awards": [
                    {
                        "title": award.get("title") or award.get("name"),
                        "issuer": award.get("issuer"),
                        "date": award.get("issued_on") or award.get("date"),
                        "description": award.get("description")
                    }
                    for award in (data.get("awards", []) or data.get("honors", []) or [])
                ] if data.get("awards") or data.get("honors") else [],
                
                # Organizations
                "organizations": [
                    {
                        "name": org.get("name"),
                        "position": org.get("position"),
                        "start_date": org.get("starts_at") or org.get("start_date"),
                        "end_date": org.get("ends_at") or org.get("end_date")
                    }
                    for org in (data.get("organizations", []) or [])
                ] if data.get("organizations") else [],
                
                # Skills (top 10)
                "skills": (data.get("skills", []) or data.get("skillsList", []))[:10],
                
                # Activities (recent posts/likes)
                "recent_activities": [
                    {
                        "title": act.get("title"),
                        "link": act.get("link"),
                        "activity_type": act.get("activity")
                    }
                    for act in (data.get("activities", []) or [])[:5]  # Get top 5 activities
                ] if data.get("activities") else [],
                
                "profile_url": url,
                "profile_id": profile_id,
                "provider": "scrapingdog"
            }
        
        except Exception as e:
            return {"error": str(e), "platform": "linkedin", "url": url, "provider": "scrapingdog"}
    
    def _scrape_linkedin_brightdata(self, url: str) -> Dict:
        """Scrape LinkedIn using Bright Data API"""
        try:
            api_url = "https://api.brightdata.com/datasets/v3/trigger"
            headers = {
                "Authorization": f"Bearer {self.linkedin_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "dataset_id": "gd_l7q7dkf244hwjntr0",  # LinkedIn profiles dataset
                "endpoint": "linkedin_profile",
                "url": url
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return {
                    "platform": "linkedin",
                    "error": f"API returned status {response.status_code}",
                    "message": response.text[:200],
                    "url": url
                }
            
            data = response.json()
            
            # Extract profile data from Bright Data response
            return {
                "platform": "linkedin",
                "full_name": data.get("name") or data.get("full_name"),
                "headline": data.get("headline"),
                "summary": data.get("summary") or data.get("about"),
                "location": data.get("location") or data.get("city"),
                "country": data.get("country"),
                "connections": data.get("connections"),
                "follower_count": data.get("followers") or data.get("follower_count"),
                "profile_pic_url": data.get("profile_pic_url") or data.get("avatar"),
                "experiences": [
                    {
                        "title": exp.get("title"),
                        "company": exp.get("company"),
                        "location": exp.get("location"),
                        "start_date": exp.get("start_date"),
                        "end_date": exp.get("end_date"),
                        "description": exp.get("description")
                    }
                    for exp in data.get("experience", [])[:3]
                ],
                "education": [
                    {
                        "school": edu.get("school"),
                        "degree": edu.get("degree"),
                        "field_of_study": edu.get("field_of_study"),
                        "start_date": edu.get("start_date"),
                        "end_date": edu.get("end_date")
                    }
                    for edu in data.get("education", [])[:2]
                ],
                "skills": data.get("skills", [])[:10],
                "profile_url": url,
                "provider": "brightdata"
            }
        
        except Exception as e:
            return {"error": str(e), "platform": "linkedin", "url": url, "provider": "brightdata"}
    
    def scrape_github(self, url: str) -> Dict:
        """Scrape GitHub profile data using GitHub REST API"""
        username = self.extract_username_from_url(url, "github")
        
        if not username:
            return {"error": "Invalid GitHub URL", "platform": "github"}
        
        try:
            # Set up headers with optional authentication
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Social-Profile-Scraper"
            }
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            # Get user profile
            user_response = requests.get(
                f"{self.github_api}/users/{username}",
                headers=headers,
                timeout=15
            )
            
            if user_response.status_code != 200:
                return {
                    "error": f"User not found or API error (status {user_response.status_code})",
                    "platform": "github",
                    "username": username
                }
            
            user_data = user_response.json()
            
            # Get user's repositories
            repos_response = requests.get(
                f"{self.github_api}/users/{username}/repos?sort=updated&per_page=100",
                headers=headers,
                timeout=15
            )
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            
            # Calculate repository statistics
            total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
            total_forks = sum(repo.get("forks_count", 0) for repo in repos_data)
            
            # Get language statistics
            languages = {}
            for repo in repos_data:
                lang = repo.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            # Sort languages by frequency
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get top repositories (by stars)
            top_repos = sorted(
                [r for r in repos_data if not r.get("fork", False)],
                key=lambda x: x.get("stargazers_count", 0),
                reverse=True
            )[:5]
            
            # Try to get contribution stats (requires scraping or GraphQL)
            # For now, we'll use available data from REST API
            
            return {
                "platform": "github",
                "username": user_data.get("login"),
                "name": user_data.get("name"),
                "bio": user_data.get("bio"),
                "company": user_data.get("company"),
                "location": user_data.get("location"),
                "email": user_data.get("email"),
                "blog": user_data.get("blog"),
                "twitter_username": user_data.get("twitter_username"),
                "public_repos": user_data.get("public_repos"),
                "public_gists": user_data.get("public_gists"),
                "followers": user_data.get("followers"),
                "following": user_data.get("following"),
                "created_at": user_data.get("created_at"),
                "updated_at": user_data.get("updated_at"),
                "total_stars_earned": total_stars,
                "total_forks_earned": total_forks,
                "top_languages": [{"language": lang, "repo_count": count} for lang, count in top_languages],
                "top_repositories": [
                    {
                        "name": repo.get("name"),
                        "description": repo.get("description"),
                        "stars": repo.get("stargazers_count"),
                        "forks": repo.get("forks_count"),
                        "language": repo.get("language"),
                        "url": repo.get("html_url"),
                        "topics": repo.get("topics", [])
                    }
                    for repo in top_repos
                ],
                "profile_url": url,
                "avatar_url": user_data.get("avatar_url")
            }
        
        except Exception as e:
            return {"error": str(e), "platform": "github", "username": username}
    
    def scrape_all(self, urls: Dict[str, str]) -> Dict:
        """Scrape all provided social profiles"""
        results = {}
        
        if "codeforces" in urls:
            print(f"Scraping Codeforces: {urls['codeforces']}")
            results["codeforces"] = self.scrape_codeforces(urls["codeforces"])
        
        if "leetcode" in urls:
            print(f"Scraping LeetCode: {urls['leetcode']}")
            results["leetcode"] = self.scrape_leetcode(urls["leetcode"])
        
        if "linkedin" in urls:
            print(f"Scraping LinkedIn: {urls['linkedin']}")
            results["linkedin"] = self.scrape_linkedin(urls["linkedin"])
        
        if "github" in urls:
            print(f"Scraping GitHub: {urls['github']}")
            results["github"] = self.scrape_github(urls["github"])
        
        return results


def main():
    """Example usage"""
    import os
    
    # Get API keys from environment variables
    linkedin_api_key = os.environ.get('LINKEDIN_API_KEY')
    linkedin_provider = os.environ.get('LINKEDIN_PROVIDER', 'scrapingdog')
    github_token = os.environ.get('GITHUB_TOKEN')  # Optional but recommended
    
    scraper = SocialProfileScraper(
        linkedin_api_key=linkedin_api_key,
        linkedin_provider=linkedin_provider,
        github_token=github_token
    )
    
    # Example URLs - replace with actual profile URLs
    urls = {
        "codeforces": "https://codeforces.com/profile/tourist",
        "leetcode": "https://leetcode.com/problemsolver",
        "github": "https://github.com/torvalds"
    }
    
    # Add LinkedIn if API key is available
    if linkedin_api_key:
        urls["linkedin"] = "https://www.linkedin.com/in/williamhgates"
    
    # Scrape all profiles
    results = scraper.scrape_all(urls)
    
    # Save to JSON file
    with open("profile_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Data extracted successfully!")
    print(f"\nResults saved to: profile_data.json")
    print(f"\nPreview:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
