import { useEffect, useRef, useState } from 'react';
import VoiceControl from './VoiceControl';
import { useVoiceAssistantContext } from '../context/VoiceAssistantContext';
import { setAudioVisualizerContainer } from '../lib/voice/audioVisualizer';
import './VoiceAssistantOverlay.css';

function VoiceAssistantOverlay() {
  const {
    isSupported,
    isListening,
    isWakeActive,
    interimText,
    startListening,
    stopListening,
    error,
    speakText,
    isSpeaking,
    ttsError,
    clearTtsError,
  } = useVoiceAssistantContext();

  const [ttsInput, setTtsInput] = useState('');
  const orbRef = useRef(null);

  useEffect(() => {
    const node = orbRef.current;
    if (!node) return undefined;
    setAudioVisualizerContainer(node);
    return () => {
      if (orbRef.current === node) {
        setAudioVisualizerContainer(null);
      }
    };
  }, []);

  useEffect(() => {
    if (ttsInput) {
      clearTtsError?.();
    }
  }, [ttsInput, clearTtsError]);

  const disabled = !isSupported || !!error;

  const handleSpeak = () => {
    if (!ttsInput.trim()) return;
    speakText(ttsInput);
  };

  const handleKeyDown = event => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleSpeak();
    }
  };

  return (
    <div className="voice-assistant-overlay">
      <div className="voice-assistant-overlay__panel">
        <div className="voice-assistant-overlay__header">
          <div className="voice-assistant-overlay__mic">
            <VoiceControl
              onStart={() => startListening({ autoRestart: true })}
              onStop={stopListening}
              isRecording={isListening}
              wakeActive={isWakeActive}
              interimText={interimText}
              disabled={disabled}
            />
          </div>
          <div
            ref={orbRef}
            className={`voice-assistant-overlay__orb ${
              isSpeaking ? 'voice-assistant-overlay__orb--active' : ''
            }`}
            aria-hidden="true"
          />
        </div>

        <div className="voice-assistant-overlay__tts-controls">
          <input
            type="text"
            className="voice-assistant-overlay__tts-input"
            placeholder="Enter text to speak"
            value={ttsInput}
            onChange={event => setTtsInput(event.target.value)}
            onKeyDown={handleKeyDown}
            data-nav-id="voice-tts-input"
          />
          <button
            className="voice-assistant-overlay__tts-button"
            onClick={handleSpeak}
            disabled={!ttsInput.trim() || isSpeaking}
            type="button"
            data-nav-id="voice-tts-speak"
          >
            Speak
          </button>
        </div>

        {error && (
          <div className="voice-assistant-overlay__error" role="status">
            Voice control unavailable
          </div>
        )}
        {ttsError && (
          <div className="voice-assistant-overlay__tts-error" role="alert">
            {ttsError.message || 'TTS failed'}
          </div>
        )}
      </div>
    </div>
  );
}

export default VoiceAssistantOverlay;

