import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TopBar from '../components/TopBar'
import GlassCard from '../components/GlassCard'
import CircularGallery from '../components/CircularGallery'
import './TemplateSelection.css'

function TemplateSelection() {
  const navigate = useNavigate()
  const [selectedOption, setSelectedOption] = useState(null)
  const [isAnimating, setIsAnimating] = useState(false)
  const [inspectingOption, setInspectingOption] = useState(null)
  const [editMode, setEditMode] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const [showGallery, setShowGallery] = useState(false)
  const [enlargedImage, setEnlargedImage] = useState(null)

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
    setShowGallery(false) // Hide gallery when closing modal
  }

  const handleModalMouseMove = (e) => {
    // Only trigger gallery in edit mode
    if (!editMode) return
    
    // If viewing enlarged image, keep gallery visible
    if (enlargedImage) return
    
    const modalContent = e.currentTarget
    const rect = modalContent.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const width = rect.width
    
    // Show gallery when mouse is in right 20% of the modal
    const threshold = width * 0.8
    setShowGallery(mouseX > threshold)
  }

  const handleImageClick = (imageData) => {
    setEnlargedImage(imageData)
    setShowGallery(true) // Keep gallery visible when viewing enlarged image
  }

  const handleCloseEnlargedImage = () => {
    setEnlargedImage(null)
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
              data-nav-id={`template-option-${option.id.toLowerCase()}`}
              onClick={() => handleOpenModal(option.id)}
              style={{ cursor: 'pointer', borderRadius: '16px' }}
              role="button"
              tabIndex={0}
              aria-label={`Inspect design option ${option.id}`}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleOpenModal(option.id);
                }
              }}
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
                  style={{ pointerEvents: 'none' }}
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
          <div 
            className="inspection-modal__content"
            onMouseMove={handleModalMouseMove}
          >
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
              data-nav-id="template-modal-close"
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

            {/* Invisible button to toggle gallery for voice navigation */}
            {editMode && (
              <button
                data-nav-id="toggle-gallery"
                onClick={() => setShowGallery(!showGallery)}
                style={{
                  position: 'absolute',
                  top: '-9999px',
                  left: '-9999px',
                  opacity: 0,
                  pointerEvents: 'none'
                }}
                aria-label="Toggle image gallery"
              >
                Toggle Gallery
              </button>
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
                  data-nav-id="template-select-design"
                >
                  Select This Design
                </button>
              </div>
            )}

            {/* Circular Gallery - only in edit mode */}
            {editMode && showGallery && (
              <div 
                className="inspection-modal__gallery-container"
                style={{ pointerEvents: enlargedImage ? 'none' : 'auto' }}
              >
                <CircularGallery
                  bend={5}
                  textColor="#E8EDF3"
                  borderRadius={0.08}
                  font="bold 24px Inter"
                  scrollSpeed={2}
                  scrollEase={0.05}
                  onImageClick={handleImageClick}
                />
              </div>
            )}

            {/* Enlarged Image View */}
            {editMode && enlargedImage && (
              <div className="enlarged-image-overlay">
                <div className="enlarged-image-container">
                  <img 
                    src={enlargedImage.image}
                    alt={enlargedImage.text}
                    className="enlarged-image"
                  />
                  <button 
                    className="enlarged-image__close"
                    onClick={handleCloseEnlargedImage}
                    aria-label="Close enlarged view"
                    data-nav-id="gallery-close-enlarged"
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
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateSelection

