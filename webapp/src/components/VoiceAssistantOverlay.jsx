import VoiceControl from './VoiceControl';
import { useVoiceAssistantContext } from '../context/VoiceAssistantContext';
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
  } = useVoiceAssistantContext();

  const label = isSupported
    ? isListening
      ? 'Listening...'
      : 'Say "Hey K2"'
    : 'Voice unsupported';
  const disabled = !isSupported || !!error;

  return (
    <div className="voice-assistant-overlay">
      <VoiceControl
        onStart={() => startListening({ autoRestart: true })}
        onStop={stopListening}
        isRecording={isListening}
        label={label}
        wakeActive={isWakeActive}
        interimText={interimText}
        disabled={disabled}
      />
      {error && (
        <div className="voice-assistant-overlay__error" role="status">
          Voice control unavailable
        </div>
      )}
    </div>
  );
}

export default VoiceAssistantOverlay;


