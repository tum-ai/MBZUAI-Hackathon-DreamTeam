import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TopBar from '../components/TopBar'
import GlassCard from '../components/GlassCard'
import './TemplateSelection.css'

function TemplateSelection() {
  const navigate = useNavigate()
  const [selectedOption, setSelectedOption] = useState(null)
  const [isAnimating, setIsAnimating] = useState(false)
  const [inspectingOption, setInspectingOption] = useState(null)

  const options = [
    { id: 'A' },
    { id: 'B' },
    { id: 'C' },
    { id: 'D' }
  ]

  const handleInspect = (optionId) => {
    setInspectingOption(optionId)
  }

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

  const handleCloseInspection = () => {
    setInspectingOption(null)
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
              >
                <iframe
                  src="http://localhost:5174"
                  className="template-selection__iframe"
                  title={`Design Option ${option.id}`}
                  sandbox="allow-same-origin allow-scripts"
                />
                <div 
                  className="template-selection__overlay-left"
                  onClick={() => handleInspect(option.id)}
                  aria-label={`Inspect design option ${option.id}`}
                />
                <div 
                  className="template-selection__overlay-right"
                  onClick={() => handleSelect(option.id)}
                  aria-label={`Select design option ${option.id}`}
                />
              </GlassCard>
            </div>
          ))}
        </div>
      </div>

      {/* Inspection Modal */}
      {inspectingOption && (
        <div className="inspection-modal">
          <div className="inspection-modal__backdrop" onClick={handleCloseInspection} />
          <div className="inspection-modal__content">
            <iframe
              src="http://localhost:5174"
              className="inspection-modal__iframe"
              title={`Inspect Design Option ${inspectingOption}`}
              sandbox="allow-same-origin allow-scripts"
            />
            
            {/* Floating close button */}
            <button 
              className="inspection-modal__close"
              onClick={handleCloseInspection}
              aria-label="Close inspection"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M15 5L5 15M5 5L15 15"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </button>

            {/* Floating footer buttons */}
            <div className="inspection-modal__footer">
              <button 
                className="inspection-modal__btn inspection-modal__btn--secondary"
                onClick={handleCloseInspection}
              >
                Back to Options
              </button>
              <button 
                className="inspection-modal__btn inspection-modal__btn--primary"
                onClick={() => {
                  handleCloseInspection()
                  handleSelect(inspectingOption)
                }}
              >
                Select This Design
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateSelection

