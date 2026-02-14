import { useState } from 'react'
import './JobSeekerDashboard.css'
import { extractResumeData, type ResumeData } from '../utils/pdfParser'

function JobSeekerDashboard() {
  const [username, setUsername] = useState('')
  const [resume, setResume] = useState<File | null>(null)
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [leetcodeUrl, setLeetcodeUrl] = useState('')
  const [codeforcesUrl, setCodeforcesUrl] = useState('')
  const [extractedData, setExtractedData] = useState<ResumeData | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setResume(file)
      
      // Auto-parse the PDF
      setIsProcessing(true)
      try {
        console.log('Starting PDF parsing for:', file.name)
        const data = await extractResumeData(file)
        console.log('Extracted resume data:', data)
        setExtractedData(data)
        alert('Resume parsed successfully! Check console for extracted data.')
      } catch (error) {
        console.error('Error parsing resume:', error)
        console.error('Error details:', {
          name: error instanceof Error ? error.name : 'Unknown',
          message: error instanceof Error ? error.message : String(error),
          stack: error instanceof Error ? error.stack : undefined
        })
        alert(`Error parsing PDF: ${error instanceof Error ? error.message : 'Unknown error'}. Check console for details.`)
      } finally {
        setIsProcessing(false)
      }
    }
  }

  const handleSaveToServer = async () => {
    if (!username.trim()) {
      alert('Please enter your username')
      return
    }
    
    if (!extractedData) {
      alert('Please upload a resume first')
      return
    }

    setIsSaving(true)
    try {
      const cleanUsername = username.trim().replace(/\s+/g, '_')
      const profileData = {
        ...extractedData,
        username: cleanUsername,
        linkedinUrl,
        githubUrl,
        leetcodeUrl,
        codeforcesUrl,
        submittedAt: new Date().toISOString()
      }

      // Step 1: Save resume data and generate embedding
      const embedResponse = await fetch('http://localhost:5000/api/embed-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: cleanUsername,
          resume_data: profileData
        })
      })

      if (!embedResponse.ok) {
        throw new Error('Failed to save profile')
      }

      // Step 2: Fetch data from platform URLs
      if (linkedinUrl || githubUrl || leetcodeUrl || codeforcesUrl) {
        const urls: any = {}
        if (linkedinUrl) urls.linkedin = linkedinUrl
        if (githubUrl) urls.github = githubUrl
        if (leetcodeUrl) urls.leetcode = leetcodeUrl
        if (codeforcesUrl) urls.codeforces = codeforcesUrl

        const fetchResponse = await fetch('http://localhost:5000/api/fetch-profile-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: cleanUsername,
            urls
          })
        })

        if (!fetchResponse.ok) {
          console.warn('Failed to fetch some platform data')
        } else {
          const fetchResult = await fetchResponse.json()
          console.log('Platform data fetched:', fetchResult)
        }
      }

      const result = await embedResponse.json()
      console.log('Saved:', result)
      alert(`✓ Profile saved successfully!\n\nData stored in: data/candidates/${cleanUsername}/\n- resume.json\n- embedding.json\n- Platform data (if URLs provided)`)
    } catch (error) {
      console.error('Error saving profile:', error)
      alert('Error saving. Make sure backend is running:\ncd backend && python app.py')
    } finally {
      setIsSaving(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSaveToServer()
  }

  return (
    <div className="dashboard">
      <h2>Upload Your Profile</h2>
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="username">Username *</label>
          <input
            type="text"
            id="username"
            placeholder="e.g. john_doe"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <span style={{fontSize: '0.85em', opacity: 0.7}}>This will be your folder name</span>
        </div>

        <div className="form-group">
          <label htmlFor="resume">Resume (PDF)</label>
          <input
            type="file"
            id="resume"
            accept=".pdf"
            onChange={handleFileChange}
            required
            disabled={isProcessing}
          />
          {isProcessing && <span className="processing">Processing PDF...</span>}
          {resume && !isProcessing && <span className="file-name">✓ {resume.name}</span>}
          {extractedData && (
            <div className="extracted-preview">
              <p>📧 {extractedData.email || 'No email found'}</p>
              <p>📱 {extractedData.phone || 'No phone found'}</p>
              <p>💼 {extractedData.skills.length} skills detected</p>
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="linkedin">LinkedIn URL</label>
          <input
            type="url"
            id="linkedin"
            placeholder="https://linkedin.com/in/yourprofile"
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="github">GitHub URL</label>
          <input
            type="url"
            id="github"
            placeholder="https://github.com/yourusername"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="leetcode">LeetCode URL</label>
          <input
            type="url"
            id="leetcode"
            placeholder="https://leetcode.com/yourusername"
            value={leetcodeUrl}
            onChange={(e) => setLeetcodeUrl(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="codeforces">Codeforces URL</label>
          <input
            type="url"
            id="codeforces"
            placeholder="https://codeforces.com/profile/yourusername"
            value={codeforcesUrl}
            onChange={(e) => setCodeforcesUrl(e.target.value)}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={!username.trim() || !extractedData || isSaving}>
          {isSaving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}

export default JobSeekerDashboard
