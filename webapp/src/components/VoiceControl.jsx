import './VoiceControl.css'

function VoiceControl({
  onStart,
  onStop,
  isRecording = false,
  wakeActive = false,
  interimText = '',
  disabled = false
}) {
  const handleClick = () => {
    if (disabled) return
    if (isRecording) {
      onStop?.()
    } else {
      onStart?.()
    }
  }

  const ariaLabel = isRecording ? 'Stop recording' : 'Start recording'

  return (
    <div className={`voice-control ${wakeActive ? 'voice-control--wake-armed' : ''}`}>
      <button
        className={`voice-control__button ${
          isRecording ? 'voice-control__button--recording' : ''
        }`}
        onClick={handleClick}
        aria-label={ariaLabel}
        disabled={disabled}
        data-nav-id="voice-control-mic"
      >
        <svg
          className="voice-control__icon"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 15C14 15 15.5 13.5 15.5 11.5V7.5C15.5 5.5 14 4 12 4C10 4 8.5 5.5 8.5 7.5V11.5C8.5 13.5 10 15 12 15Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M19 11.5V12C19 15.866 15.866 19 12 19C8.134 19 5 15.866 5 12V11.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M12 19V21"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
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

