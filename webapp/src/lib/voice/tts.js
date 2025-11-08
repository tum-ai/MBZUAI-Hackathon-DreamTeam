import {
  ensureVisualizerLoop,
  ensureAudioContextRunning,
  routeTTSToAnalyser,
  cleanupTTSAudio,
} from './audioVisualizer.js';
import { playTTSStartSound } from './soundEffects.js';

const VOICE_ID = 'ashjVK50jp28G73AUTnb';
const MODEL_ID = 'eleven_flash_v2_5';
const STORAGE_KEY = 'ELEVENLABS_API_KEY';

function getEnvKey() {
  const key = import.meta?.env?.VITE_ELEVENLABS_API_KEY;
  return typeof key === 'string' && key.trim().length ? key.trim() : null;
}

function getMetaKey() {
  try {
    const meta = document.querySelector('meta[name="elevenlabs-key"]')?.content?.trim();
    return meta || null;
  } catch {
    return null;
  }
}

function getStoredKey() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored?.trim() || null;
  } catch {
    return null;
  }
}

function persistKey(key) {
  try {
    localStorage.setItem(STORAGE_KEY, key);
  } catch {
    /* noop */
  }
}

function resolveApiKey() {
  const envKey = getEnvKey();
  if (envKey) return envKey;

  const metaKey = getMetaKey();
  if (metaKey) return metaKey;

  const storedKey = getStoredKey();
  if (storedKey) return storedKey;

  return null;
}

function requestApiKeyInteractive() {
  const entered = prompt('Enter your ElevenLabs API key (stored locally):')?.trim();
  if (!entered) return null;
  persistKey(entered);
  return entered;
}

export async function speakText(text, {
  isListening = false,
  stopListening,
  startListening,
  disarmWakeWord,
  armWakeWord,
  setSpeaking,
  setError,
} = {}) {
  const trimmed = text?.trim();
  if (!trimmed) return;

  if (setError) setError(null);

  let apiKey = resolveApiKey();
  if (!apiKey) {
    apiKey = requestApiKeyInteractive();
  }

  if (!apiKey) {
    const err = new Error('Missing ElevenLabs API key. Set VITE_ELEVENLABS_API_KEY or enter it when prompted.');
    setError?.(err);
    console.warn('[VoiceAssistant] ElevenLabs API key missing – set VITE_ELEVENLABS_API_KEY or store via prompt');
    return;
  }

  const wasListening = !!isListening;

  if (wasListening) {
    try {
      stopListening?.();
    } catch {
      /* noop */
    }
  }

  try {
    disarmWakeWord?.();
  } catch {
    /* noop */
  }

  setSpeaking?.(true);

  try {
    ensureVisualizerLoop();
  } catch {
    /* noop */
  }

  if (window.AudioOrb) {
    try {
      window.AudioOrb.setActive(true);
      window.AudioOrb.setSpeaking(true);
    } catch {
      /* noop */
    }
  }

  playTTSStartSound();
  await new Promise(resolve => setTimeout(resolve, 400));

  let ttsSourceNode = null;
  let ttsAudioEl = null;

  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/stream`,
      {
        method: 'POST',
        headers: {
          Accept: 'audio/mpeg',
          'xi-api-key': apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: trimmed,
          model_id: MODEL_ID,
          voice_settings: { stability: 0.5, similarity_boost: 0.75 },
        }),
      },
    );

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `TTS request failed (${response.status})`);
    }

    const blob = await response.blob();
    if (!blob || !blob.size) {
      throw new Error('Received empty audio response from ElevenLabs');
    }
    const url = URL.createObjectURL(blob);
    ttsAudioEl = document.createElement('audio');
    ttsAudioEl.crossOrigin = 'anonymous';
    ttsAudioEl.src = url;
    ttsAudioEl.preload = 'auto';
    ttsAudioEl.volume = 1;
    document.body.appendChild(ttsAudioEl);

    try {
      ttsSourceNode = routeTTSToAnalyser(ttsAudioEl);
    } catch (err) {
      console.warn('[VoiceAssistant] Unable to route TTS audio to analyser:', err);
    }

    let endedReason = 'ended';
    const endedPromise = new Promise(resolve =>
      ttsAudioEl.addEventListener(
        'ended',
        () => {
          endedReason = 'ended';
          resolve();
        },
        { once: true },
      ),
    );
    const errorPromise = new Promise((resolve, reject) =>
      ttsAudioEl.addEventListener(
        'error',
        event => {
          endedReason = 'error';
          const err =
            event?.target?.error ||
            new Error('Audio element encountered an error during playback');
          reject(err);
        },
        { once: true },
      ),
    );
    let timeoutId = null;
    const timeoutPromise = new Promise((resolve, reject) => {
      timeoutId = setTimeout(() => {
        endedReason = 'timeout';
        reject(new Error('TTS playback timed out before completion'));
      }, 60_000);
    });
    const clearTimeoutSafe = () => {
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
    endedPromise.finally(clearTimeoutSafe);
    errorPromise.finally(clearTimeoutSafe);

    try {
      console.log('[VoiceAssistant] TTS blob size:', blob.size);
      await ensureAudioContextRunning();
      await ttsAudioEl.play();
    } catch (err) {
      console.error('TTS playback blocked:', err);
      throw err;
    }

    await Promise.race([endedPromise, errorPromise, timeoutPromise]);
    console.log('[VoiceAssistant] TTS playback finished with reason:', endedReason);
  } catch (err) {
    console.error('TTS error:', err);
    setError?.(err instanceof Error ? err : new Error('TTS playback failed'));
  } finally {
    cleanupTTSAudio(ttsSourceNode, ttsAudioEl);
    if (ttsAudioEl && ttsAudioEl.parentNode) {
      ttsAudioEl.parentNode.removeChild(ttsAudioEl);
    }
    if (window.AudioOrb) {
      try {
        window.AudioOrb.setSpeaking(false);
        window.AudioOrb.setActive(false);
      } catch {
        /* noop */
      }
    }
    setSpeaking?.(false);
    try {
      armWakeWord?.();
    } catch {
      /* noop */
    }
    if (wasListening) {
      try {
        startListening?.({ autoRestart: true });
      } catch {
        /* noop */
      }
    }
  }
}


