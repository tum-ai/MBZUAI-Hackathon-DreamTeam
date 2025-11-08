import { tryApplyPhrases } from './phraseBias.js';

export const WAKE_VARIANTS = [
  'hey k2',
  'hey, k2',
  'hey k two',
  'hey, k two',
  'okay k2',
  'ok k2',
  'ok k two',
  'okay k two',
  'hey key two',
  'hey kay two',
];

export function isWakeUtterance(text) {
  const normalized = text.trim().toLowerCase();
  if (WAKE_VARIANTS.some(variant => normalized.includes(variant))) return true;
  return /\bhey[, ]+k\s*2\b/.test(normalized) || /\bhey[, ]+k\s*two\b/.test(normalized);
}

export function buildWakeRecognition(SpeechRecognitionCtor, options) {
  const { lang = 'en-US', forceLocal = false, phraseBiasSupported = null } = options ?? {};
  const recognition = new SpeechRecognitionCtor();

  recognition.lang = lang;
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  try {
    if ('processLocally' in recognition) {
      recognition.processLocally = !!forceLocal;
    }
  } catch {
    /* noop */
  }

  const result = tryApplyPhrases(recognition, WAKE_VARIANTS, phraseBiasSupported);
  const updatedSupported =
    result.supported === null || result.supported === undefined
      ? phraseBiasSupported
      : result.supported;

  return { recognition, phraseBiasSupported: updatedSupported };
}

export function safeWakeRestart(recognition) {
  try {
    recognition.start();
  } catch {
    try {
      recognition.stop();
    } catch {
      /* noop */
    }
    setTimeout(() => {
      try {
        recognition.start();
      } catch {
        /* noop */
      }
    }, 150);
  }
}


