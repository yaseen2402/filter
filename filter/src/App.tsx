import { useState } from 'react'
import './App.css'
import JobSeekerDashboard from './components/JobSeekerDashboard'
import CompanyDashboard from './components/CompanyDashboard'

function App() {
  const [isJobSeeker, setIsJobSeeker] = useState(true)

  return (
    <div className="app">
      <header className="header">
        <h1>{isJobSeeker ? 'Job Seeker Dashboard' : 'Company Dashboard'}</h1>
        <div className="toggle-container">
          <span className={isJobSeeker ? 'active' : ''}>Job Seeker</span>
          <label className="toggle-switch">
            <input 
              type="checkbox" 
              checked={!isJobSeeker}
              onChange={() => setIsJobSeeker(!isJobSeeker)}
            />
            <span className="slider"></span>
          </label>
          <span className={!isJobSeeker ? 'active' : ''}>Company</span>
        </div>
      </header>
      
      <main className="main-content">
        {isJobSeeker ? <JobSeekerDashboard /> : <CompanyDashboard />}
      </main>
    </div>
  )
}

export default App
