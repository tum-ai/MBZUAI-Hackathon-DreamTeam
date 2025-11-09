import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';
import { speakText as playTTS } from '../lib/voice/tts';
import { captureCombinedDOMSnapshot } from '../utils/domSnapshot';
import { queryAgent, validateAction } from '../services/llmAgent';
import { routeAndExecuteAction } from '../services/actionRouter';

const VoiceAssistantContext = createContext(null);
const SESSION_STORAGE_KEY = 'voice-assistant-session-id';

const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
};

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
  const [lastBackendPrompt, setLastBackendPrompt] = useState(null);
  const [sessionId, setSessionId] = useState(() => {
    if (typeof window === 'undefined') return null;
    try {
      const stored = window.localStorage.getItem(SESSION_STORAGE_KEY);
      return stored || null;
    } catch {
      return null;
    }
  });
  const sessionIdRef = useRef(sessionId);
  const [lastActionResult, setLastActionResult] = useState(null);
  const [submissionError, setSubmissionError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const pendingClarifierStepRef = useRef(null);
  const lastSubmittedKeyRef = useRef(null);
  const clearTtsErrorFn = useCallback(() => setTtsError(null), []);

  const combinedBiasPhrases = useMemo(() => {
    const merged = [...BASE_BIAS_PHRASES, ...customBiasPhrases];
    return Array.from(new Set(merged));
  }, [customBiasPhrases]);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  useEffect(() => {
    if (sessionId !== null) {
      return;
    }
    const generated = generateId();
    sessionIdRef.current = generated;
    setSessionId(generated);
  }, [sessionId]);

  useEffect(() => {
    if (typeof window === 'undefined' || !sessionId) {
      return;
    }
    try {
      window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    } catch {
      /* noop */
    }
  }, [sessionId]);

  const notifyListeners = useCallback((eventName, ...args) => {
    listenersRef.current.forEach(listener => {
      const handler = listener[eventName];
      if (typeof handler === 'function') {
        handler(...args);
      }
    });
  }, []);

  const ensureSessionId = useCallback(() => {
    if (sessionIdRef.current) return sessionIdRef.current;
    const generated = generateId();
    sessionIdRef.current = generated;
    setSessionId(generated);
    return generated;
  }, []);

  const submitUtterance = useCallback(
    async (text, { stepId: incomingStepId } = {}) => {
      const trimmed = text?.trim();
      if (!trimmed) return null;

      const sid = ensureSessionId();
      const stepId = incomingStepId || generateId();

      setSubmissionError(null);
      setIsSubmitting(true);

      try {
        console.log('[VoiceAssistant] Capturing DOM snapshot for utterance execution');
        const domSnapshot = await captureCombinedDOMSnapshot();

        console.log('[VoiceAssistant] Querying actor with command:', {
          command: trimmed,
          sessionId: sid,
          stepId,
        });

        const actorResponse = await queryAgent(trimmed, domSnapshot, {
          sessionId: sid,
          stepId,
          metadata: {
            source: 'voice-assistant-context',
          },
        });

        const actorSessionId = actorResponse?.sessionId || sid;
        const actorStepId = actorResponse?.stepId || stepId;
        const actionPayload = actorResponse?.action ?? actorResponse;

        if (!validateAction(actionPayload)) {
          throw new Error('Actor returned an invalid action payload');
        }

        if (actorSessionId && actorSessionId !== sessionIdRef.current) {
          sessionIdRef.current = actorSessionId;
          setSessionId(actorSessionId);
        }

        console.log('[VoiceAssistant] Routing action to frontend:', actionPayload);
        const executionResult = await routeAndExecuteAction(actionPayload, domSnapshot);

        const record = {
          sessionId: actorSessionId,
          stepId: actorStepId,
          command: trimmed,
          action: actionPayload,
          result: executionResult,
          actorMeta: {
            rawAction: actorResponse?.rawAction ?? null,
          },
          timestamp: Date.now(),
        };

        setLastActionResult(record);
        notifyListeners('onActionExecuted', record);

        return record;
      } catch (err) {
        const normalized =
          err instanceof Error ? err : new Error('Voice assistant request failed.');
        setSubmissionError(normalized);
        notifyListeners('onActionError', normalized);
        throw normalized;
      } finally {
        pendingClarifierStepRef.current = null;
        setIsSubmitting(false);
      }
    },
    [ensureSessionId, notifyListeners],
  );

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

  const fallbackSpeak = useCallback(
    async text => {
      if (typeof window === 'undefined' || !window.speechSynthesis) {
        throw new Error('Browser speech synthesis not supported.');
      }

      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;
      utterance.lang = voice.options?.lang || 'en-US';

      const wasListening = !!voice.isListening;

      try {
        voice.disarmWakeWord?.();
      } catch {
        /* noop */
      }

      if (wasListening) {
        try {
          voice.stopListening?.();
        } catch {
          /* noop */
        }
      }

      setTtsError(null);
      setIsSpeaking(true);

      await new Promise((resolve, reject) => {
        const handleEnd = () => {
          cleanup();
          resolve();
        };
        const handleError = event => {
          cleanup();
          reject(
            event?.error
              ? new Error(String(event.error))
              : new Error('Browser speech synthesis failed.'),
          );
        };
        const cleanup = () => {
          utterance.removeEventListener('end', handleEnd);
          utterance.removeEventListener('error', handleError);
        };

        utterance.addEventListener('end', handleEnd);
        utterance.addEventListener('error', handleError);
        synth.cancel();
        synth.speak(utterance);
      });

      try {
        voice.armWakeWord?.();
      } catch {
        /* noop */
      }
      if (wasListening) {
        try {
          voice.startListening?.({ autoRestart: true });
        } catch {
          /* noop */
        }
      }
    },
    [voice],
  );

  const triggerTTS = useCallback(
    async text => {
      if (!text || isSpeaking) return;

      try {
      await playTTS(text, {
        isListening: voice.isListening,
        stopListening: voice.stopListening,
        startListening: voice.startListening,
        disarmWakeWord: voice.disarmWakeWord,
        armWakeWord: voice.armWakeWord,
        setSpeaking: value => setIsSpeaking(value),
        setError: err => setTtsError(err),
      });
      } catch (err) {
        console.warn('[VoiceAssistant] ElevenLabs TTS failed, falling back to browser TTS.', err);
        try {
          await fallbackSpeak(text);
        } catch (fallbackErr) {
          console.error('[VoiceAssistant] Fallback TTS failed:', fallbackErr);
          setTtsError(
            fallbackErr instanceof Error
              ? fallbackErr
              : new Error('Unable to play clarification audio.'),
          );
        } finally {
          setIsSpeaking(false);
        }
      }
    },
    [
      isSpeaking,
      voice.isListening,
      voice.stopListening,
      voice.startListening,
      voice.disarmWakeWord,
      voice.armWakeWord,
      fallbackSpeak,
    ],
  );

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    const handleBackendTts = async event => {
      const detail = event?.detail || {};
      const incomingText = detail.text;
      if (!incomingText) {
        return;
      }

      try {
        console.log('[VoiceAssistant] Received backend TTS payload:', detail);
      } catch {
        /* noop */
      }

      const payload = {
        text: incomingText,
        sessionId: detail.sessionId ?? null,
        stepId: detail.stepId ?? null,
        requestId: detail.requestId ?? null,
        receivedAt: Date.now(),
      };

      setLastBackendPrompt(payload);
      if (payload.sessionId && payload.sessionId !== sessionIdRef.current) {
        sessionIdRef.current = payload.sessionId;
        setSessionId(payload.sessionId);
      }
      pendingClarifierStepRef.current = payload.stepId ?? null;
      await triggerTTS(incomingText);
      clearLastBackendPrompt();
    };

    window.addEventListener('voice-assistant-tts', handleBackendTts);
    return () => {
      window.removeEventListener('voice-assistant-tts', handleBackendTts);
    };
  }, [triggerTTS]);

  const clearLastBackendPrompt = useCallback(() => setLastBackendPrompt(null), []);

  useEffect(() => {
    const segment = voice.lastFinalSegment;
    if (!segment) return;
    if (isSubmitting) return;

    const trimmed = segment.trim();
    if (!trimmed) return;

    const aggregate = voice.finalText?.trim() || '';
    const key = `${trimmed}|${aggregate.length}`;
    if (lastSubmittedKeyRef.current === key) {
      return;
    }
    lastSubmittedKeyRef.current = key;

    const resumeStepId =
      pendingClarifierStepRef.current || lastBackendPrompt?.stepId || undefined;
    const usedClarifierStep = Boolean(resumeStepId);

    (async () => {
      try {
        await submitUtterance(trimmed, { stepId: resumeStepId });
      } catch (err) {
        console.error('[VoiceAssistant] Failed to submit utterance:', err);
      } finally {
        if (usedClarifierStep) {
          pendingClarifierStepRef.current = null;
          clearLastBackendPrompt();
        }
      }
    })();
  }, [
    voice.lastFinalSegment,
    voice.finalText,
    submitUtterance,
    lastBackendPrompt,
    clearLastBackendPrompt,
    isSubmitting,
  ]);

  const contextValue = useMemo(
    () => ({
      ...voice,
      isSpeaking,
      ttsError,
      clearTtsError: clearTtsErrorFn,
      speakText: triggerTTS,
      registerListener,
      sessionId: sessionIdRef.current,
      submitUtterance,
      isSubmitting,
      submissionError,
      lastActionResult,
      lastBackendPrompt,
      clearLastBackendPrompt,
      setBiasPhrases: phrases => {
        setCustomBiasPhrases(Array.isArray(phrases) ? phrases : []);
      },
    }),
    [
      voice,
      isSpeaking,
      ttsError,
      triggerTTS,
      registerListener,
      clearTtsErrorFn,
      lastBackendPrompt,
      clearLastBackendPrompt,
      submitUtterance,
      isSubmitting,
      submissionError,
      lastActionResult,
    ],
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


