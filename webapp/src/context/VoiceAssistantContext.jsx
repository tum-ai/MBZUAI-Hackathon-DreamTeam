import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';
import { speakText as playTTS } from '../lib/voice/tts';

const VoiceAssistantContext = createContext(null);

const BASE_BIAS_PHRASES = [
  'canvas',
  'layer',
  'export',
  'color',
  'grid',
  'history',
  'selection',
  'template',
  'undo',
  'redo',
  'zoom',
];

export function VoiceAssistantProvider({ children }) {
  const listenersRef = useRef(new Set());
  const [customBiasPhrases, setCustomBiasPhrases] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsError, setTtsError] = useState(null);
  const clearTtsErrorFn = useCallback(() => setTtsError(null), []);

  const combinedBiasPhrases = useMemo(() => {
    const merged = [...BASE_BIAS_PHRASES, ...customBiasPhrases];
    return Array.from(new Set(merged));
  }, [customBiasPhrases]);

  const notifyListeners = useCallback((eventName, ...args) => {
    listenersRef.current.forEach(listener => {
      const handler = listener[eventName];
      if (typeof handler === 'function') {
        handler(...args);
      }
    });
  }, []);

  const voice = useVoiceAssistant({
    autoRestart: true,
    wakeWordEnabled: true,
    biasPhrases: combinedBiasPhrases,
    onFinalSegment: (joined, segments) => {
      notifyListeners('onFinal', joined, segments);
    },
    onInterim: interim => {
      notifyListeners('onInterim', interim);
    },
    onWakeTriggered: transcript => {
      notifyListeners('onWakeTriggered', transcript);
    },
  });

  const registerListener = useCallback(listener => {
    if (!listener) return () => {};
    listenersRef.current.add(listener);
    return () => {
      listenersRef.current.delete(listener);
    };
  }, []);

  useEffect(() => {
    if (!voice.isSupported || typeof document === 'undefined') {
      return undefined;
    }

    let primed = false;

    const handleFirstInteract = () => {
      if (primed) return;
      primed = true;

      voice.armWakeWord?.();

      document.removeEventListener('click', handleFirstInteract);
      document.removeEventListener('keydown', handleFirstInteract);
    };

    document.addEventListener('click', handleFirstInteract);
    document.addEventListener('keydown', handleFirstInteract);

    return () => {
      document.removeEventListener('click', handleFirstInteract);
      document.removeEventListener('keydown', handleFirstInteract);
    };
  }, [voice]);

  const triggerTTS = useCallback(
    async text => {
      if (!text || isSpeaking) return;
      await playTTS(text, {
        isListening: voice.isListening,
        stopListening: voice.stopListening,
        startListening: voice.startListening,
        disarmWakeWord: voice.disarmWakeWord,
        armWakeWord: voice.armWakeWord,
        setSpeaking: value => setIsSpeaking(value),
        setError: err => setTtsError(err),
      });
    },
    [
      isSpeaking,
      voice.isListening,
      voice.stopListening,
      voice.startListening,
      voice.disarmWakeWord,
      voice.armWakeWord,
    ],
  );

  const contextValue = useMemo(
    () => ({
      ...voice,
      isSpeaking,
      ttsError,
      clearTtsError: clearTtsErrorFn,
      speakText: triggerTTS,
      registerListener,
      setBiasPhrases: phrases => {
        setCustomBiasPhrases(Array.isArray(phrases) ? phrases : []);
      },
    }),
    [voice, isSpeaking, ttsError, triggerTTS, registerListener, clearTtsErrorFn],
  );

  // Expose speakText globally for testing
  useEffect(() => {
    if (import.meta.env.DEV) {
      window.__speakText = triggerTTS;
      return () => {
        delete window.__speakText;
      };
    }
  }, [triggerTTS]);

  return (
    <VoiceAssistantContext.Provider value={contextValue}>
      {children}
    </VoiceAssistantContext.Provider>
  );
}

export function useVoiceAssistantContext() {
  const ctx = useContext(VoiceAssistantContext);
  if (!ctx) {
    throw new Error('useVoiceAssistantContext must be used within a VoiceAssistantProvider');
  }
  return ctx;
}


