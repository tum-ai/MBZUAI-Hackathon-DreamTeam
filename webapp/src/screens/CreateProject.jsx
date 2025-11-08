import { useNavigate } from 'react-router-dom'
import TopBar from '../components/TopBar'
import ColorBends from '../components/ColorBends'
import './CreateProject.css'

function CreateProject() {
  const navigate = useNavigate()

  const handleCreate = () => {
    navigate('/templates')
  }

  return (
    <div className="create-project">
      <ColorBends
                colors={['#ff5c7a', '#8a5cff', '#00ffd1']}
                rotation={0}
                speed={0.3}
                scale={1.2}
                frequency={1.4}
                warpStrength={1}
                mouseInfluence={0.8}
                parallax={0.6}
                noise={0.05}
                transparent
        
      />
      <TopBar title="Voice-First Platform" />
      
      <div className="create-project__content">
        <div className="create-project__center">
          <h1 className="create-project__title">Create new project</h1>
          <p className="create-project__subtitle">
            Start by describing what you want to build.
          </p>
          <button className="create-project__cta" onClick={handleCreate} data-nav-id="create-project-cta">
            Get Started
          </button>
        </div>
      </div>
    </div>
  )
}

export default CreateProject

