import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { VoiceAssistantController } from '../lib/voice/voiceAssistantController.js';

const DEFAULT_CTRL_OPTIONS = {
  lang: 'en-US',
  interimResults: true,
  autoRestart: false,
  wakeWordEnabled: true,
  biasPhrases: [],
  forceLocal: false,
};

export function useVoiceAssistant(options = {}) {
  const {
    lang = DEFAULT_CTRL_OPTIONS.lang,
    interimResults = DEFAULT_CTRL_OPTIONS.interimResults,
    autoRestart = DEFAULT_CTRL_OPTIONS.autoRestart,
    wakeWordEnabled = DEFAULT_CTRL_OPTIONS.wakeWordEnabled,
    biasPhrases = DEFAULT_CTRL_OPTIONS.biasPhrases,
    forceLocal = DEFAULT_CTRL_OPTIONS.forceLocal,
    onFinalSegment,
    onInterim,
    onWakeTriggered,
  } = options;

  const controllerOptions = useMemo(
    () => ({
      lang,
      interimResults,
      autoRestart,
      wakeWordEnabled,
      biasPhrases,
      forceLocal,
    }),
    [lang, interimResults, autoRestart, wakeWordEnabled, biasPhrases, forceLocal],
  );

  const finalCallbackRef = useRef(onFinalSegment);
  const interimCallbackRef = useRef(onInterim);
  const wakeTriggeredRef = useRef(onWakeTriggered);

  useEffect(() => {
    finalCallbackRef.current = onFinalSegment;
  }, [onFinalSegment]);

  useEffect(() => {
    interimCallbackRef.current = onInterim;
  }, [onInterim]);

  useEffect(() => {
    wakeTriggeredRef.current = onWakeTriggered;
  }, [onWakeTriggered]);

  const controllerRef = useRef(null);

  const [isSupported, setIsSupported] = useState(() => typeof window !== 'undefined');
  const [isListening, setIsListening] = useState(false);
  const [isWakeActive, setIsWakeActive] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [finalText, setFinalText] = useState('');
  const [lastFinalSegment, setLastFinalSegment] = useState(null);
  const [phraseBiasSupported, setPhraseBiasSupported] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setIsSupported(false);
      return undefined;
    }
    const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) {
      setIsSupported(false);
      return undefined;
    }

    setIsSupported(true);

    const controller = new VoiceAssistantController(
      SpeechRecognitionCtor,
      controllerOptions,
      {
        onListeningChange: next => {
          setIsListening(next);
          if (next) {
            setError(null);
          }
        },
        onWakeActiveChange: next => setIsWakeActive(next),
        onInterim: text => {
          setInterimText(text);
          interimCallbackRef.current?.(text);
        },
        onFinal: (joined, segments) => {
          setLastFinalSegment(joined);
          setFinalText(prev => {
            if (!prev) return joined;
            const needsSpace = prev && !prev.endsWith(' ');
            return `${prev}${needsSpace ? ' ' : ''}${joined}`.trim();
          });
          finalCallbackRef.current?.(joined, segments);
        },
        onError: event => {
          // Ignore "no-speech" errors - these are not real errors, just timeouts
          if (event?.error === 'no-speech') {
            console.log('[VoiceAssistant] No speech detected (timeout), ignoring...');
            return;
          }

          console.warn('[VoiceAssistant] Controller error:', event);
          setError(event);
        },
        onPhraseBiasChange: supported => setPhraseBiasSupported(supported),
        onWakeTriggered: transcript => wakeTriggeredRef.current?.(transcript),
      },
    );

    try {
      controller.init();
    } catch (err) {
      console.warn('Voice assistant initialization failed:', err);
      setError(err);
      setIsSupported(false);
      return undefined;
    }

    controllerRef.current = controller;

    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
    // we intentionally exclude controllerOptions from deps here; updates handled below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    controllerRef.current?.updateOptions(controllerOptions);
  }, [controllerOptions]);

  const startListening = useCallback(
    (startOptions = {}) => {
      setInterimText('');
      controllerRef.current?.startListening(startOptions);
    },
    [],
  );

  const stopListening = useCallback(() => {
    controllerRef.current?.stopListening();
  }, []);

  const armWakeWord = useCallback(() => {
    controllerRef.current?.armWakeWord();
  }, []);

  const disarmWakeWord = useCallback(() => {
    controllerRef.current?.disarmWakeWord();
  }, []);

  const resetTranscripts = useCallback(() => {
    setInterimText('');
    setFinalText('');
    setLastFinalSegment(null);
  }, []);

  return {
    isSupported,
    isListening,
    isWakeActive,
    interimText,
    finalText,
    lastFinalSegment,
    phraseBiasSupported,
    error,
    options: controllerOptions,
    startListening,
    stopListening,
    armWakeWord,
    disarmWakeWord,
    resetTranscripts,
  };
}


