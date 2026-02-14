import { useState } from 'react'
import './CompanyDashboard.css'

interface Candidate {
  username: string
  similarity_score?: number
  final_score?: number
  confidence?: number
  completeness?: number
  email: string | null
  phone: string | null
  skills: string[]
  linkedin: string | null
  github: string | null
  available_platforms?: string[]
  platform_scores?: Record<string, number>
  adjusted_weights?: Record<string, number>
}

interface Job {
  job_id: string
  jobTitle: string
  company: string
  location: string
  jobType: string
  salary: string
  description: string
  requirements: string
  submittedAt: string
}

function CompanyDashboard() {
  const [jobTitle, setJobTitle] = useState('')
  const [company, setCompany] = useState('')
  const [location, setLocation] = useState('')
  const [jobType, setJobType] = useState('full-time')
  const [description, setDescription] = useState('')
  const [requirements, setRequirements] = useState('')
  const [salary, setSalary] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [lastJobId, setLastJobId] = useState<string | null>(null)
  const [matchedCandidates, setMatchedCandidates] = useState<Candidate[]>([])
  const [isMatching, setIsMatching] = useState(false)
  const [showMatches, setShowMatches] = useState(false)
  const [postedJobs, setPostedJobs] = useState<Job[]>([])
  const [showJobs, setShowJobs] = useState(false)
  const [isLoadingJobs, setIsLoadingJobs] = useState(false)
  const [selectedJobForMatching, setSelectedJobForMatching] = useState<string | null>(null)
  const [rankingMethod, setRankingMethod] = useState<'embedding' | 'formula'>('embedding')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    setIsSaving(true)
    try {
      const jobId = `job_${Date.now()}`
      const jobData = {
        jobTitle,
        company,
        location,
        jobType,
        description,
        requirements,
        salary,
        submittedAt: new Date().toISOString()
      }

      // Send to embedding service
      const response = await fetch('http://localhost:5000/api/embed-job', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: jobId,
          job_data: jobData
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save job')
      }

      const result = await response.json()
      console.log('Saved:', result)
      setLastJobId(jobId)
      alert(`Job posted and embedding saved to data/jobs/${jobId}/\n\nClick "Find Matching Candidates" to see ranked results!`)
      
      // Reset form
      setJobTitle('')
      setCompany('')
      setLocation('')
      setJobType('full-time')
      setDescription('')
      setRequirements('')
      setSalary('')
    } catch (error) {
      console.error('Error saving job:', error)
      alert('Error saving job. Make sure embedding service is running:\ncd embedding-service && python app.py')
    } finally {
      setIsSaving(false)
    }
  }

  const handleFindCandidates = async (jobId?: string) => {
    const targetJobId = jobId || lastJobId
    if (!targetJobId) {
      alert('Please post a job first!')
      return
    }

    setIsMatching(true)
    setShowMatches(false)
    setSelectedJobForMatching(targetJobId)
    
    try {
      const endpoint = rankingMethod === 'embedding' 
        ? 'http://localhost:5000/api/match-candidates'
        : 'http://localhost:5000/api/rank-candidates-formula'
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: targetJobId,
          top_k: 20
        })
      })

      if (!response.ok) {
        throw new Error('Failed to match candidates')
      }

      const result = await response.json()
      console.log('Matched candidates:', result)
      console.log('Ranking method:', rankingMethod)
      console.log('First candidate:', result.matches?.[0] || result.rankings?.[0])
      setMatchedCandidates(result.matches || result.rankings || [])
      setShowMatches(true)
      
      if (!result.matches && !result.rankings || (result.matches?.length === 0 && result.rankings?.length === 0)) {
        alert('No candidates found. Make sure candidates have uploaded their profiles.')
      }
    } catch (error) {
      console.error('Error matching candidates:', error)
      alert('Error finding candidates. Make sure backend is running.')
    } finally {
      setIsMatching(false)
    }
  }

  const handleViewJobs = async () => {
    setIsLoadingJobs(true)
    try {
      const response = await fetch('http://localhost:5000/api/list-jobs')
      
      if (!response.ok) {
        throw new Error('Failed to load jobs')
      }

      const result = await response.json()
      setPostedJobs(result.jobs || [])
      setShowJobs(true)
      
      if (!result.jobs || result.jobs.length === 0) {
        alert('No jobs posted yet. Create your first job posting!')
      }
    } catch (error) {
      console.error('Error loading jobs:', error)
      alert('Error loading jobs. Make sure backend is running.')
    } finally {
      setIsLoadingJobs(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>{showJobs ? 'Posted Jobs' : 'Create Job Posting'}</h2>
        <button 
          onClick={() => {
            if (showJobs) {
              setShowJobs(false)
              setShowMatches(false)
            } else {
              handleViewJobs()
            }
          }} 
          className="view-jobs-btn"
          disabled={isLoadingJobs}
        >
          {isLoadingJobs ? 'Loading...' : showJobs ? 'Post a Job' : 'View Posted Jobs'}
        </button>
      </div>

      {showJobs && postedJobs.length > 0 && (
        <div className="jobs-list">
          <div className="jobs-header">
            <h3>Posted Jobs ({postedJobs.length})</h3>
            <div className="ranking-toggle">
              <label>Ranking Method:</label>
              <select 
                value={rankingMethod} 
                onChange={(e) => setRankingMethod(e.target.value as 'embedding' | 'formula')}
                className="ranking-select"
              >
                <option value="embedding">Embedding Match</option>
                <option value="formula">Formula Ranking</option>
              </select>
            </div>
          </div>
          <div className="jobs-grid">
            {postedJobs.map((job) => (
              <div key={job.job_id} className="job-card">
                <div className="job-header">
                  <h4>{job.jobTitle}</h4>
                  <span className="job-type-badge">{job.jobType}</span>
                </div>
                <p className="job-company">{job.company}</p>
                <p className="job-location">{job.location}</p>
                {job.salary && <p className="job-salary">{job.salary}</p>}
                <p className="job-date">{new Date(job.submittedAt).toLocaleDateString()}</p>
                <button 
                  onClick={() => handleFindCandidates(job.job_id)}
                  className="find-candidates-btn"
                  disabled={isMatching}
                >
                  {isMatching && selectedJobForMatching === job.job_id ? 'Finding...' : 'Find Candidates'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {showMatches && matchedCandidates.length > 0 && (
        <div className="candidates-list">
          <h3>
            Matched Candidates (Ranked by {rankingMethod === 'embedding' ? 'Similarity' : 'Formula Score'})
          </h3>
          <div className="candidates-grid">
            {matchedCandidates.map((candidate, index) => {
              const score = candidate.similarity_score || candidate.final_score || 0
              const scorePercent = rankingMethod === 'embedding' 
                ? (score * 100).toFixed(1)
                : score.toFixed(1)
              
              return (
                <div key={candidate.username} className="candidate-card">
                  <div className="candidate-rank">#{index + 1}</div>
                  <div className="candidate-header">
                    <h4>{candidate.username}</h4>
                    <div className="similarity-badge">
                      {scorePercent}%
                    </div>
                  </div>
                  <div className="candidate-details">
                    <div className="contact-info">
                      {candidate.email && <span>{candidate.email}</span>}
                      {candidate.phone && <span>{candidate.phone}</span>}
                    </div>
                    
                    {candidate.skills && candidate.skills.length > 0 && (
                      <div className="skills-section">
                        <p className="section-label">Skills</p>
                        <div className="skills-tags">
                          {candidate.skills.slice(0, 5).map((skill: string, i: number) => (
                            <span key={i} className="skill-tag">{skill}</span>
                          ))}
                          {candidate.skills.length > 5 && (
                            <span className="skill-tag-more">+{candidate.skills.length - 5}</span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {rankingMethod === 'formula' && candidate.available_platforms && candidate.available_platforms.length > 0 && (
                      <div className="sources-section">
                        <p className="section-label">Data Sources Used for Ranking</p>
                        <div className="platforms-tags">
                          {candidate.available_platforms.map((platform: string, i: number) => (
                            <span key={i} className="platform-tag">{platform}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="candidate-footer">
                      {rankingMethod === 'formula' && candidate.completeness && (
                        <span className="completeness-badge">{candidate.completeness}% complete</span>
                      )}
                      <div className="candidate-links">
                        {candidate.github && (
                          <a href={candidate.github} target="_blank" rel="noopener noreferrer">GitHub</a>
                        )}
                        {candidate.linkedin && (
                          <a href={candidate.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {!showJobs && (
        <>
          <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="jobTitle">Job Title</label>
          <input
            type="text"
            id="jobTitle"
            placeholder="e.g. Senior Software Engineer"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="company">Company Name</label>
          <input
            type="text"
            id="company"
            placeholder="Your company name"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            type="text"
            id="location"
            placeholder="e.g. San Francisco, CA or Remote"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="jobType">Job Type</label>
          <select
            id="jobType"
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
          >
            <option value="full-time">Full-time</option>
            <option value="part-time">Part-time</option>
            <option value="contract">Contract</option>
            <option value="internship">Internship</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="salary">Salary Range</label>
          <input
            type="text"
            id="salary"
            placeholder="e.g. $100k - $150k"
            value={salary}
            onChange={(e) => setSalary(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Job Description</label>
          <textarea
            id="description"
            placeholder="Describe the role and responsibilities..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="requirements">Requirements</label>
          <textarea
            id="requirements"
            placeholder="List required skills and qualifications..."
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            rows={5}
            required
          />
        </div>

        <button type="submit" className="submit-btn" disabled={isSaving}>
          {isSaving ? 'Posting...' : 'Post Job'}
        </button>
      </form>

      {lastJobId && (
        <div className="match-section">
          <button 
            onClick={() => handleFindCandidates()} 
            className="match-btn"
            disabled={isMatching}
          >
            {isMatching ? 'Finding Candidates...' : 'Find Matching Candidates'}
          </button>
        </div>
      )}
        </>
      )}
    </div>
  )
}

export default CompanyDashboard
