import { tryApplyPhrases } from './phraseBias.js';

export function buildRecognition(SpeechRecognitionCtor, options = {}) {
  const {
    lang = 'en-US',
    continuous = false,
    interimResults = true,
    forceLocal = false,
    phraseBiasSupported = null,
    biasPhrases = [],
    onPhraseBiasChange,
  } = options;

  const recognition = new SpeechRecognitionCtor();
  recognition.lang = lang;
  recognition.continuous = !!continuous;
  recognition.interimResults = !!interimResults;
  recognition.maxAlternatives = 1;

  try {
    if ('processLocally' in recognition) {
      recognition.processLocally = !!forceLocal;
    }
  } catch {
    /* noop */
  }

  const result = tryApplyPhrases(recognition, biasPhrases, phraseBiasSupported);
  if (result.supported !== null && result.supported !== phraseBiasSupported) {
    onPhraseBiasChange?.(result.supported);
  }

  return { recognition, phraseBiasSupported: result.supported ?? phraseBiasSupported };
}

export function attachRecognitionHandlers(recognition, handlers = {}) {
  const {
    onStart,
    onError,
    onLocalError,
    onPhraseBiasError,
    onEnd,
    onFinal,
    onInterim,
    onRestart,
    onArmWakeWord,
    getAutoRestartWanted = () => false,
    getPhraseBiasSupported = () => null,
  } = handlers;

  recognition.onstart = () => {
    onStart?.();
  };

  recognition.onerror = event => {
    if (event?.error === 'phrases-not-supported') {
      onPhraseBiasError?.();
      return;
    }
    onError?.(event);
    if (recognition.processLocally) {
      onLocalError?.(event);
    }
  };

  recognition.onend = () => {
    onEnd?.();

    if (getAutoRestartWanted()) {
      onRestart?.();
    } else {
      onArmWakeWord?.();
    }
  };

  recognition.onresult = event => {
    let interimText = '';
    const finalChunks = [];
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const res = event.results[i];
      const text = res[0].transcript;
      if (res.isFinal) {
        finalChunks.push(text);
      } else {
        interimText += text + ' ';
      }
    }

    if (finalChunks.length) {
      onFinal?.(finalChunks);
    }
    onInterim?.(interimText.trim());
  };
}


