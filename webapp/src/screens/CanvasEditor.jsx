import { useState, useEffect, useMemo, useCallback } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import TopBar from '../components/TopBar'
import CanvasFrame from '../components/CanvasFrame'
import GlassCard from '../components/GlassCard'
import { useVoiceAssistantContext } from '../context/VoiceAssistantContext'
import './CanvasEditor.css'

function CanvasEditor() {
  const { projectId } = useParams()
  const location = useLocation()
  const [status, setStatus] = useState('connected')
  const [showHistory, setShowHistory] = useState(false)
  const [commandHistory, setCommandHistory] = useState([])

  const selectedOption = location.state?.selectedOption || projectId?.toUpperCase() || 'A'
  const projectTitle = `Editing: Option ${selectedOption}`

  const voiceBiasPhrases = useMemo(
    () => ['canvas', 'layer', 'export', 'color', 'grid', 'history', 'selection', 'template'],
    []
  )

  const handleFinalSegment = useCallback(text => {
    if (!text) return
    const entry = {
      id: Date.now(),
      text,
      timestamp: new Date().toLocaleTimeString()
    }
    setCommandHistory(prev => [entry, ...prev])
  }, [])

  const handleInterim = useCallback(interim => {
    if (interim) {
      setStatus('listening')
    }
  }, [])

  const handleWakeTriggered = useCallback(transcript => {
    setStatus('wake detected')
    if (transcript) {
      const entry = {
        id: Date.now(),
        text: `[Wake] ${transcript}`,
        timestamp: new Date().toLocaleTimeString()
      }
      setCommandHistory(prev => [entry, ...prev])
    }
  }, [])

  const {
    isListening,
    isWakeActive,
    registerListener,
    setBiasPhrases
  } = useVoiceAssistantContext()

  useEffect(() => {
    const unregister = registerListener({
      onFinal: handleFinalSegment,
      onInterim: handleInterim,
      onWakeTriggered: handleWakeTriggered
    })
    setBiasPhrases(voiceBiasPhrases)
    return () => {
      unregister()
      setBiasPhrases([])
    }
  }, [registerListener, setBiasPhrases, voiceBiasPhrases, handleFinalSegment, handleInterim, handleWakeTriggered])

  // Simulate status changes
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly change status for demo purposes
      const statuses = ['connected', 'updating']
      const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
      if (!isListening && !isWakeActive) {
        setStatus(randomStatus)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [isListening, isWakeActive])

  useEffect(() => {
    if (isListening) {
      setStatus('listening')
    } else if (isWakeActive) {
      setStatus('wake ready')
    }
  }, [isListening, isWakeActive])

  return (
    <div className="canvas-editor">
      <TopBar title={projectTitle} showBack={true}>
        <button className="canvas-editor__btn" onClick={() => setShowHistory(!showHistory)}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M10 6V10L13 13"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          History
        </button>
        <button className="canvas-editor__btn canvas-editor__btn--primary">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M16 10V16C16 16.5304 15.7893 17.0391 15.4142 17.4142C15.0391 17.7893 14.5304 18 14 18H4C3.46957 18 2.96086 17.7893 2.58579 17.4142C2.21071 17.0391 2 16.5304 2 16V6C2 5.46957 2.21071 4.96086 2.58579 4.58579C2.96086 4.21071 3.46957 4 4 4H10"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M15 2L18 5L10 13L7 14L8 11L15 2Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Export
        </button>
      </TopBar>

      <div className="canvas-editor__main">
        <div className="canvas-editor__canvas-container">
          <CanvasFrame
            src="http://localhost:5174"
            status={status}
            title="Canvas — Live Preview"
          />
        </div>

        {/* Optional: Right sidebar with history, layers, actions */}
        {showHistory && (
          <aside className="canvas-editor__sidebar">
            <GlassCard className="canvas-editor__sidebar-card">
              <div className="canvas-editor__sidebar-header">
                <h3>History</h3>
                <button
                  className="canvas-editor__close-btn"
                  onClick={() => setShowHistory(false)}
                  aria-label="Close history"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M12 4L4 12M4 4L12 12"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </button>
              </div>
              <div className="canvas-editor__history-list">
                {commandHistory.length === 0 ? (
                  <p className="canvas-editor__empty-state">
                    No commands yet. Start by using voice control.
                  </p>
                ) : (
                  commandHistory.map(cmd => (
                    <div key={cmd.id} className="canvas-editor__history-item">
                      <span className="canvas-editor__history-text">{cmd.text}</span>
                      <span className="canvas-editor__history-time">{cmd.timestamp}</span>
                    </div>
                  ))
                )}
              </div>
            </GlassCard>
          </aside>
        )}
      </div>

      {/* Optional: Grid overlay toggle (key "G") */}
      <div className="canvas-editor__hint">
        <p>Press <kbd>G</kbd> to toggle grid overlay</p>
      </div>
    </div>
  )
}

export default CanvasEditor

