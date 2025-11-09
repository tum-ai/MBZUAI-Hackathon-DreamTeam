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
    isSpeaking,
  } = useVoiceAssistantContext();

  const orbRef = useRef(null);
  const disabled = !isSupported || !!error;

  // Check if we're on template selection screen or modal is open - MUST be declared before useEffects
  const [shouldShowToolbar, setShouldShowToolbar] = useState(false);

  const handleStart = () => {
    startListening({ autoRestart: true });
  };

  // Set up audio visualizer container when toolbar becomes visible
  useEffect(() => {
    if (!shouldShowToolbar) {
      console.log('[VoiceAssistant] Toolbar hidden, skipping orb setup');
      return undefined;
    }
    
    const node = orbRef.current;
    if (!node) {
      console.warn('[VoiceAssistant] Orb container ref is null');
      return undefined;
    }
    console.log('[VoiceAssistant] Setting up audio visualizer container', {
      node,
      dimensions: { width: node.offsetWidth, height: node.offsetHeight },
      computed: window.getComputedStyle(node)
    });
    setAudioVisualizerContainer(node);
    return () => {
      console.log('[VoiceAssistant] Cleaning up audio visualizer container');
      setAudioVisualizerContainer(null);
    };
  }, [shouldShowToolbar]);

  // Debug: log when isSpeaking changes
  useEffect(() => {
    console.log('[VoiceAssistant] isSpeaking changed:', isSpeaking);
  }, [isSpeaking]);

  useEffect(() => {
    const checkVisibility = () => {
      const modal = document.querySelector('.inspection-modal__content');
      const templateSelection = document.querySelector('.template-selection');
      setShouldShowToolbar(!!(modal || templateSelection));
    };

    // Initial check
    checkVisibility();

    // Watch for changes
    const observer = new MutationObserver(checkVisibility);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => observer.disconnect();
  }, []);

  const handleClose = () => {
    // Hierarchical closing: enlarged image → modal → template selection
    if (window.__hasEnlargedImage && window.__hasEnlargedImage()) {
      // Level 1: If an image is enlarged, close it first
      window.__closeEnlargedImage?.();
    } else if (window.__closeInspectionModal) {
      // Level 2: Close the modal (if open)
      window.__closeInspectionModal();
    } else if (window.__navigateBackFromTemplates) {
      // Level 3: Navigate back from template selection to create project
      window.__navigateBackFromTemplates();
    }
  };

  return (
    <>
      {/* Toolbar - only show on template selection or when modal is open */}
      {shouldShowToolbar && (
        <div className="voice-assistant-toolbar">
          {/* Button column */}
          <div className="voice-assistant-toolbar__buttons">
            {/* Close button */}
            <button 
              className="voice-toolbar-button voice-toolbar-button--close"
              onClick={handleClose}
              aria-label="Close modal"
              data-nav-id="toolbar-close-btn"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M18 6L6 18M6 6L18 18"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </button>

            {/* Mic button */}
            <VoiceControl
              onStart={handleStart}
              onStop={stopListening}
              isRecording={isListening}
              wakeActive={isWakeActive}
              interimText={interimText}
              disabled={disabled}
            />
          </div>

          {/* Audio visualization orb - shows when TTS is speaking */}
          <div
            ref={orbRef}
            className={`voice-assistant-toolbar__orb ${isSpeaking ? 'voice-assistant-toolbar__orb--active' : ''}`}
            aria-hidden="true"
          />
        </div>
      )}
    </>
  );
}

export default VoiceAssistantOverlay;

