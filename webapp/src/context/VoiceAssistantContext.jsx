import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';
import { useStreamingPlan } from '../hooks/useStreamingPlan';
import { speakText as playTTS } from '../lib/voice/tts';
import { captureCombinedDOMSnapshot } from '../utils/domSnapshot';
import { validateAction, parseActionPayload } from '../services/llmAgent';
import { routeAndExecuteAction } from '../services/actionRouter';

const VoiceAssistantContext = createContext(null);
const SESSION_STORAGE_KEY = 'voice-assistant-session-id';

const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
};

// Feature flag for streaming execution
// Set VITE_USE_STREAMING_PLAN=true in .env to enable
const USE_STREAMING = import.meta.env?.VITE_USE_STREAMING_PLAN === 'true';

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
  const [lastPlanResponse, setLastPlanResponse] = useState(null);
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

  const llmApiBase = useMemo(() => {
    const envBase = import.meta?.env?.VITE_LLM_API_BASE_URL;
    if (envBase && typeof envBase === 'string') {
      return envBase.replace(/\/$/, '');
    }
    if (typeof window !== 'undefined' && typeof window.__LLM_API_BASE_URL === 'string') {
      return window.__LLM_API_BASE_URL.replace(/\/$/, '');
    }
    return 'http://localhost:8000';
  }, []);

  // Initialize streaming plan hook (only if enabled)
  const streamingPlan = USE_STREAMING ? useStreamingPlan({
    wsUrl: `${llmApiBase.replace('http', 'ws')}/plan-stream`
  }) : null;

  // Session state for Vite editor
  const [viteUrl, setViteUrl] = useState(null);
  const [isInitializingSession, setIsInitializingSession] = useState(false);
  const initializationStartedRef = useRef(false);

  useEffect(() => {
    const initSession = async () => {
      if (initializationStartedRef.current) return;
      initializationStartedRef.current = true;

      try {
        setIsInitializingSession(true);

        // Try to recover existing session from localStorage
        let sessionId = localStorage.getItem('vite_session_id');

        if (sessionId) {
          // Check if session still exists
          try {
            const response = await fetch(`http://localhost:8000/sessions/${sessionId}/exists`);
            if (response.ok) {
              const { exists } = await response.json();

              if (!exists) {
                console.log('[VoiceAssistant] Previous session expired, creating new one');
                sessionId = null;
              } else {
                console.log('[VoiceAssistant] Recovered existing session:', sessionId);
                // Get session info
                const infoResponse = await fetch(`http://localhost:8000/sessions/${sessionId}/info`);
                if (infoResponse.ok) {
                  const sessionInfo = await infoResponse.json();
                  setViteUrl(sessionInfo.vite_url);
                  sessionIdRef.current = sessionId;
                  setSessionId(sessionId);
                }
              }
            }
          } catch (e) {
            console.warn('[VoiceAssistant] Failed to check session existence:', e);
            sessionId = null;
          }
        }

        // Create new session if needed
        if (!sessionId) {
          sessionId = crypto.randomUUID();
          console.log('[VoiceAssistant] Creating new session:', sessionId);

          const response = await fetch('http://localhost:8000/sessions/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
          });

          if (response.ok) {
            const sessionInfo = await response.json();
            console.log('[VoiceAssistant] Session created:', sessionInfo);

            setViteUrl(sessionInfo.vite_url);
            sessionIdRef.current = sessionId;
            setSessionId(sessionId);
            localStorage.setItem('vite_session_id', sessionId);
          }
        }

      } catch (error) {
        console.error('[VoiceAssistant] Failed to initialize session:', error);
      } finally {
        setIsInitializingSession(false);
      }
    };

    initSession();
  }, []);

  useEffect(() => {
    if (USE_STREAMING) {
      console.log('[VoiceAssistant] Streaming mode ENABLED');
      console.log('[VoiceAssistant] WebSocket connection:', streamingPlan?.isConnected ? 'Connected' : 'Disconnected');
    } else {
      console.log('[VoiceAssistant] Streaming mode DISABLED (using traditional /plan endpoint)');
    }
  }, [streamingPlan?.isConnected]);

  // Ref for triggerTTS to avoid dependency issues
  const triggerTTSRef = useRef(null);

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

      // Use streaming if enabled and connected
      if (USE_STREAMING && streamingPlan?.isConnected) {
        try {
          console.log('[VoiceAssistant] Using STREAMING mode');

          let domSnapshot = null;
          const executionRecords = [];

          return new Promise((resolve, reject) => {
            streamingPlan.sendPlanRequest(trimmed, sid, {
              onStepComplete: async (stepData) => {
                console.log('[VoiceAssistant] Stream step completed:', stepData.stepType);

                try {
                  // Handle action steps
                  if (stepData.stepType === 'act') {
                    // Capture DOM if not already done
                    if (!domSnapshot) {
                      domSnapshot = await captureCombinedDOMSnapshot();
                    }

                    const actionPayload = parseActionPayload(stepData.result);
                    if (!validateAction(actionPayload)) {
                      throw new Error('Invalid action payload');
                    }

                    console.log('[VoiceAssistant] Executing action immediately:', actionPayload);
                    const executionResult = await routeAndExecuteAction(actionPayload, domSnapshot);

                    const record = {
                      sessionId: sid,
                      stepId: stepData.stepId,
                      command: trimmed,
                      action: actionPayload,
                      result: executionResult,
                      agentType: stepData.stepType,
                      timestamp: Date.now(),
                    };

                    executionRecords.push(record);
                    setLastActionResult(record);
                    notifyListeners('onActionExecuted', record);

                    // Refresh DOM for next action
                    domSnapshot = await captureCombinedDOMSnapshot();
                  }

                  // Handle clarifications
                  if (stepData.stepType === 'clarify') {
                    if (triggerTTSRef.current) {
                      await triggerTTSRef.current(stepData.result);
                    }
                    notifyListeners('onClarifyResult', {
                      step_id: stepData.stepId,
                      result: stepData.result,
                      agent_type: 'clarify'
                    });
                  }
                } catch (err) {
                  console.error('[VoiceAssistant] Error executing step:', err);
                  setSubmissionError(err);
                  notifyListeners('onActionError', err);
                }
              },
              onFinish: (data) => {
                console.log('[VoiceAssistant] Stream finished:', data);
                setIsSubmitting(false);
                resolve({
                  plan: { totalSteps: data.totalSteps },
                  actions: executionRecords
                });
              },
              onError: (error) => {
                console.error('[VoiceAssistant] Stream error:', error);
                setSubmissionError(error);
                setIsSubmitting(false);
                notifyListeners('onActionError', error);
                reject(error);
              }
            });
          });
        } catch (err) {
          const normalized = err instanceof Error ? err : new Error('Streaming request failed.');
          setSubmissionError(normalized);
          setIsSubmitting(false);
          notifyListeners('onActionError', normalized);
          throw normalized;
        }
      }

      // Fall back to traditional /plan endpoint
      console.log('[VoiceAssistant] Using TRADITIONAL mode');
      try {
        console.log('[VoiceAssistant] Sending /plan request:', {
          command: trimmed,
          sessionId: sid,
          stepId,
          endpoint: `${llmApiBase}/plan`,
        });

        const response = await fetch(`${llmApiBase}/plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sid,
            text: trimmed,
            step_id: stepId,
          }),
        });

        if (!response.ok) {
          const message = await response.text();
          throw new Error(message || `LLM request failed (${response.status})`);
        }

        const planJson = await response.json();
        const planSessionId = planJson?.sid || sid;

        if (planSessionId && planSessionId !== sessionIdRef.current) {
          sessionIdRef.current = planSessionId;
          setSessionId(planSessionId);
        }

        const planRecord = {
          sessionId: planSessionId,
          stepId,
          command: trimmed,
          response: planJson,
          timestamp: Date.now(),
        };
        setLastPlanResponse(planRecord);
        notifyListeners('onPlanComplete', planRecord);

        const planResults = Array.isArray(planJson?.results) ? planJson.results : [];
        const actResults = planResults.filter(result => result?.agent_type === 'act');
        const clarifierResults = planResults.filter(result => result?.agent_type === 'clarify');

        clarifierResults.forEach(result => {
          notifyListeners('onClarifyResult', result);
        });

        const executionRecords = [];

        let domSnapshot = null;
        if (actResults.length > 0) {
          console.log('[VoiceAssistant] Capturing DOM snapshot for ACT execution');
          domSnapshot = await captureCombinedDOMSnapshot();
        }

        for (let index = 0; index < actResults.length; index += 1) {
          const actResult = actResults[index];

          let actionPayload;
          try {
            actionPayload = parseActionPayload(actResult.result);
          } catch (parseError) {
            console.error('[VoiceAssistant] Failed to parse planner action:', {
              result: actResult.result,
              error: parseError,
            });
            throw new Error('Planner returned an unparsable action payload');
          }

          if (!validateAction(actionPayload)) {
            console.error('[VoiceAssistant] Planner returned invalid action:', actionPayload);
            throw new Error('Planner returned an invalid action payload');
          }

          console.log('[VoiceAssistant] Executing planner action:', {
            action: actionPayload,
            stepId: actResult.step_id,
          });

          const executionResult = await routeAndExecuteAction(
            actionPayload,
            domSnapshot || { elements: [] },
          );

          const record = {
            sessionId: actResult.session_id || planSessionId,
            stepId: actResult.step_id,
            command: trimmed,
            action: actionPayload,
            result: executionResult,
            agentType: actResult.agent_type,
            timestamp: Date.now(),
          };

          executionRecords.push(record);
          setLastActionResult(record);
          notifyListeners('onActionExecuted', record);

          if (index < actResults.length - 1) {
            try {
              domSnapshot = await captureCombinedDOMSnapshot();
            } catch (snapshotError) {
              console.warn('[VoiceAssistant] Failed to refresh DOM snapshot between actions:', snapshotError);
            }
          }
        }

        if (executionRecords.length === 0) {
          setLastActionResult(null);
        }

        return {
          plan: planJson,
          actions: executionRecords,
        };
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
    [ensureSessionId, llmApiBase, streamingPlan, notifyListeners],
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
    if (!listener) return () => { };
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

  // Update ref when triggerTTS changes
  useEffect(() => {
    triggerTTSRef.current = triggerTTS;
  }, [triggerTTS]);

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
      lastPlanResponse,
      // Session state
      viteUrl,
      isInitializingSession,
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
      lastPlanResponse,
      viteUrl,
      isInitializingSession,
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


