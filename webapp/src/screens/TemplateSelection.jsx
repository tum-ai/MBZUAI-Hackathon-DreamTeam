import { useState, useEffect } from 'react'
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
    { id: 'A', port: 5173, label: 'Professional' },
    { id: 'B', port: 5174, label: 'Dark' },
    { id: 'C', port: 5175, label: 'Minimal' },
    { id: 'D', port: 5176, label: 'Energetic' }
  ]

  const handleOpenModal = (optionId) => {
    setInspectingOption(optionId)
    setEditMode(false)
  }

  const handleSelectDesign = async () => {
    // Transition from inspection to edit mode
    setEditMode(true)
    setConnectionStatus('updating')
    
    // Find the variation index (0-3) for the selected option
    const selectedIndex = options.findIndex(o => o.id === inspectingOption)
    
    try {
      // Call the compiler API to select this variation as active
      const response = await fetch('http://localhost:8000/select-template-variation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ variation_index: selectedIndex })
      })
      
      if (response.ok) {
        console.log(`Selected variation ${selectedIndex} (${options[selectedIndex].label}) as active`)
        setConnectionStatus('connected')
      } else {
        console.error('Failed to select template variation:', await response.text())
        setConnectionStatus('connected') // Still show connected, just log error
      }
    } catch (error) {
      console.error('Error selecting template variation:', error)
      setConnectionStatus('connected')
    }
  }

  const handleCloseModal = () => {
    setInspectingOption(null)
    setEditMode(false)
    setConnectionStatus('connected')
    setShowGallery(false) // Hide gallery when closing modal
  }

  // Expose close handlers and state globally for voice toolbar
  useEffect(() => {
    if (inspectingOption) {
      window.__closeInspectionModal = handleCloseModal
      window.__closeEnlargedImage = handleCloseEnlargedImage
      window.__hasEnlargedImage = () => !!enlargedImage
      return () => {
        delete window.__closeInspectionModal
        delete window.__closeEnlargedImage
        delete window.__hasEnlargedImage
      }
    }
  }, [inspectingOption, enlargedImage])

  // Expose navigation back handler for template selection screen
  useEffect(() => {
    window.__navigateBackFromTemplates = () => navigate('/')
    return () => {
      delete window.__navigateBackFromTemplates
    }
  }, [navigate])

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
                  src={`http://localhost:${option.port}`}
                  className="template-selection__iframe"
                  title={`Design Option ${option.id} - ${option.label}`}
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
              src={`http://localhost:${options.find(o => o.id === inspectingOption)?.port || 5174}`}
              className="inspection-modal__iframe"
              title={`${editMode ? 'Editing' : 'Inspecting'} Design Option ${inspectingOption} - ${options.find(o => o.id === inspectingOption)?.label}`}
              sandbox="allow-same-origin allow-scripts"
            />

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

