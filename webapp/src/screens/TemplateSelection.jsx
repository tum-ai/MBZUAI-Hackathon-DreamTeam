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
  const [editMode, setEditMode] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('connected')

  const options = [
    { id: 'A' },
    { id: 'B' },
    { id: 'C' },
    { id: 'D' }
  ]

  const handleOpenModal = (optionId) => {
    setInspectingOption(optionId)
    setEditMode(false)
  }

  const handleSelectDesign = () => {
    // Transition from inspection to edit mode
    setEditMode(true)
    // Simulate connection status changes for demo
    setTimeout(() => setConnectionStatus('updating'), 2000)
    setTimeout(() => setConnectionStatus('connected'), 4000)
  }

  const handleCloseModal = () => {
    setInspectingOption(null)
    setEditMode(false)
    setConnectionStatus('connected')
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
                  onClick={() => handleOpenModal(option.id)}
                  aria-label={`Open design option ${option.id}`}
                />
                <div 
                  className="template-selection__overlay-right"
                  onClick={() => handleOpenModal(option.id)}
                  aria-label={`Open design option ${option.id}`}
                />
              </GlassCard>
            </div>
          ))}
        </div>
      </div>

      {/* Inspection/Edit Modal */}
      {inspectingOption && (
        <div className="inspection-modal">
          <div 
            className="inspection-modal__backdrop" 
            onClick={editMode ? null : handleCloseModal}
            style={{ cursor: editMode ? 'default' : 'pointer' }}
          />
          <div className="inspection-modal__content">
            <iframe
              src="http://localhost:5174"
              className="inspection-modal__iframe"
              title={`${editMode ? 'Editing' : 'Inspecting'} Design Option ${inspectingOption}`}
              sandbox="allow-same-origin allow-scripts"
            />
            
            {/* Floating close button */}
            <button 
              className="inspection-modal__close"
              onClick={handleCloseModal}
              aria-label={editMode ? 'Close editor' : 'Close inspection'}
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

            {/* Status indicator - only in edit mode */}
            {editMode && (
              <div className="inspection-modal__status">
                <div className={`status-dot status-dot--${connectionStatus}`} />
                <span className="status-label">
                  {connectionStatus === 'connected' ? 'Connected' : 'Updating'}
                </span>
              </div>
            )}

            {/* Floating footer buttons - only in inspection mode */}
            {!editMode && (
              <div className="inspection-modal__footer">
                <button 
                  className="inspection-modal__btn inspection-modal__btn--secondary"
                  onClick={handleCloseModal}
                >
                  Back to Options
                </button>
                <button 
                  className="inspection-modal__btn inspection-modal__btn--primary"
                  onClick={handleSelectDesign}
                >
                  Select This Design
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateSelection

