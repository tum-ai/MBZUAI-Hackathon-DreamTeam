import { useNavigate } from 'react-router-dom'
import GlassCard from '../components/GlassCard'
import VoiceControl from '../components/VoiceControl'
import './CreateProject.css'

function CreateProject() {
  const navigate = useNavigate()

  const handleCreate = () => {
    navigate('/templates')
  }

  const handleVoiceStart = () => {
    console.log('Voice recording started')
    // TODO: Integrate with Whisper API
  }

  const handleVoiceStop = () => {
    console.log('Voice recording stopped')
    // TODO: Process voice command
  }

  return (
    <div className="create-project">
      <div className="create-project__content">
        <GlassCard className="create-project__card">
          <div className="create-project__card-inner">
            <div className="create-project__icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <path
                  d="M24 12V36M12 24H36"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <h1 className="create-project__title">Create new project</h1>
            <p className="create-project__subtitle">
              Start by describing what you want to build.
            </p>
            <button className="create-project__cta" onClick={handleCreate}>
              Get Started
            </button>
            <div className="create-project__divider">
              <span>or</span>
            </div>
            <VoiceControl
              onStart={handleVoiceStart}
              onStop={handleVoiceStop}
              label="Say: create a new project"
            />
          </div>
        </GlassCard>

        {/* Optional: Placeholder for recent projects */}
        <div className="create-project__recent">
          <p className="create-project__recent-title">Recent Projects</p>
          <div className="create-project__recent-grid">
            {/* Empty state for now - will be populated with thumbnails later */}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateProject

