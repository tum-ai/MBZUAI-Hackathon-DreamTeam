import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TopBar from '../components/TopBar'
import GlassCard from '../components/GlassCard'
import VoiceControl from '../components/VoiceControl'
import './TemplateSelection.css'

function TemplateSelection() {
  const navigate = useNavigate()
  const [selectedOption, setSelectedOption] = useState(null)
  const [isAnimating, setIsAnimating] = useState(false)

  const options = [
    { id: 'A', label: 'Option A' },
    { id: 'B', label: 'Option B' },
    { id: 'C', label: 'Option C' },
    { id: 'D', label: 'Option D' }
  ]

  const handleSelect = (optionId) => {
    setSelectedOption(optionId)
    setIsAnimating(true)
    
    // Animate and navigate to editor
    setTimeout(() => {
      navigate(`/editor/${optionId.toLowerCase()}`, { 
        state: { selectedOption: optionId }
      })
    }, 400)
  }

  const handleVoiceStart = () => {
    console.log('Voice recording started')
    // TODO: Integrate voice command parsing (e.g., "select the one in the middle")
  }

  const handleVoiceStop = () => {
    console.log('Voice recording stopped')
  }

  return (
    <div className="template-selection">
      <TopBar title="Choose a Design" showBack={true} />
      
      <div className="template-selection__content">
        <div className="template-selection__header">
          <h2 className="template-selection__title">
            Select your starting point
          </h2>
          <p className="template-selection__subtitle">
            We've generated four initial designs based on your input
          </p>
        </div>

        <div className={`template-selection__grid ${isAnimating ? 'template-selection__grid--animating' : ''}`}>
          {options.map((option) => (
            <div
              key={option.id}
              className={`template-selection__option ${
                selectedOption === option.id ? 'template-selection__option--selected' : ''
              }`}
            >
              <GlassCard
                hoverable={true}
                className="template-selection__card"
                onClick={() => handleSelect(option.id)}
              >
                <div className="template-selection__iframe-wrapper">
                  <iframe
                    src="http://localhost:5174"
                    className="template-selection__iframe"
                    title={option.label}
                    sandbox="allow-same-origin allow-scripts"
                  />
                </div>
                <div className="template-selection__card-footer">
                  <span className="template-selection__card-label">
                    {option.label}
                  </span>
                  <button 
                    className="template-selection__select-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSelect(option.id)
                    }}
                  >
                    Select
                  </button>
                </div>
              </GlassCard>
            </div>
          ))}
        </div>

        <div className="template-selection__voice-hint">
          <p className="template-selection__hint-text">
            Say: "select the one in the middle" or "choose option B"
          </p>
          <VoiceControl
            onStart={handleVoiceStart}
            onStop={handleVoiceStop}
            label="Voice Control"
          />
        </div>
      </div>
    </div>
  )
}

export default TemplateSelection

