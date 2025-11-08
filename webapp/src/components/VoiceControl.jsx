import { useEffect, useRef } from 'react'
import { setAudioVisualizerContainer } from '../lib/voice/audioVisualizer'
import './VoiceControl.css'

function VoiceControl({
  onStart,
  onStop,
  isRecording = false,
  label,
  wakeActive = false,
  interimText = '',
  disabled = false
}) {
  const visualizerRef = useRef(null)
  const defaultLabel = isRecording
    ? 'Listening...'
    : wakeActive
    ? 'Say "Hey K2"'
    : 'Voice Control'

  useEffect(() => {
    const node = visualizerRef.current
    setAudioVisualizerContainer(node)
    return () => {
      if (visualizerRef.current === node) {
        setAudioVisualizerContainer(null)
      }
    }
  }, [])

  const handleClick = () => {
    if (disabled) return
    if (isRecording) {
      onStop?.()
    } else {
      onStart?.()
    }
  }

  return (
    <div className={`voice-control ${wakeActive ? 'voice-control--wake-armed' : ''}`}>
      <div
        ref={visualizerRef}
        className="voice-control__visualizer"
        aria-hidden="true"
      />
      <button
        className={`voice-control__button ${
          isRecording ? 'voice-control__button--recording' : ''
        }`}
        onClick={handleClick}
        aria-label={isRecording ? 'Stop recording' : 'Start recording'}
        disabled={disabled}
      >
        <svg
          className="voice-control__icon"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M10 13C11.933 13 13.5 11.433 13.5 9.5V5.5C13.5 3.567 11.933 2 10 2C8.067 2 6.5 3.567 6.5 5.5V9.5C6.5 11.433 8.067 13 10 13Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M16 9.5V10C16 13.314 13.314 16 10 16C6.686 16 4 13.314 4 10V9.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M10 16V18"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="voice-control__label">{label || defaultLabel}</span>
      </button>
      {isRecording && (
        <div className="voice-control__pulse" aria-hidden="true" />
      )}
      {isRecording && interimText && (
        <div className="voice-control__interim" aria-live="polite">
          {interimText}
        </div>
      )}
    </div>
  )
}

export default VoiceControl

