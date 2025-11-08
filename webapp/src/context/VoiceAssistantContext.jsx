import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';

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

  const contextValue = useMemo(
    () => ({
      ...voice,
      registerListener,
      setBiasPhrases: phrases => {
        setCustomBiasPhrases(Array.isArray(phrases) ? phrases : []);
      },
    }),
    [voice, registerListener],
  );

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


