import { buildRecognition, attachRecognitionHandlers } from './speechRecognition.js';
import { buildWakeRecognition, isWakeUtterance, safeWakeRestart } from './wakeWord.js';
import {
  playActivationSound,
  playFinalResultSound,
  playStoppedSound,
} from './soundEffects.js';

const DEFAULT_OPTIONS = {
  lang: 'en-US',
  interimResults: true,
  autoRestart: false,
  wakeWordEnabled: true,
  forceLocal: false,
  biasPhrases: [],
};

export class VoiceAssistantController {
  constructor(SpeechRecognitionCtor, options = {}, callbacks = {}) {
    this.SR = SpeechRecognitionCtor;
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.callbacks = callbacks;

    this.recognition = null;
    this.wakeRecognition = null;

    this.recognizing = false;
    this.autoRestartWanted = false;

    this.wakeArmed = false;
    this.wakeListening = false;

    this.phraseBiasSupported = null;
    this.micPrimed = false;
    this.primingPromise = null;
  }

  init() {
    if (!this.SR) {
      throw new Error('SpeechRecognition API is not available in this environment.');
    }

    this._buildRecognition(this.options.forceLocal);
    if (this.options.wakeWordEnabled) {
      this._buildWakeRecognition(this.options.forceLocal);
    }
  }

  destroy() {
    this.autoRestartWanted = false;
    this.wakeArmed = false;
    try {
      this.recognition?.stop();
    } catch {
      /* noop */
    }
    try {
      this.wakeRecognition?.stop();
    } catch {
      /* noop */
    }
    this.recognition = null;
    this.wakeRecognition = null;
  }

  ensureMicPrimed() {
    if (this.micPrimed) return Promise.resolve();
    if (this.primingPromise) return this.primingPromise;

    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      this.micPrimed = true;
      try {
        console.log('[VoiceAssistant] Mic priming skipped (no mediaDevices).');
      } catch {
        /* noop */
      }
      return Promise.resolve();
    }

    this.primingPromise = navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(stream => {
        try {
          stream.getTracks().forEach(track => track.stop());
        } catch {
          /* noop */
        }
        this.micPrimed = true;
        try {
          console.log('[VoiceAssistant] Mic primed via getUserMedia.');
        } catch {
          /* noop */
        }
      })
      .catch(err => {
        this.micPrimed = false;
        try {
          console.warn('[VoiceAssistant] Mic priming failed:', err);
        } catch {
          /* noop */
        }
        throw err;
      })
      .finally(() => {
        this.primingPromise = null;
      });

    return this.primingPromise;
  }

  updateOptions(newOptions = {}) {
    const merged = { ...this.options, ...newOptions };
    const langChanged = merged.lang !== this.options.lang;
    const biasChanged =
      JSON.stringify(merged.biasPhrases ?? []) !== JSON.stringify(this.options.biasPhrases ?? []);
    const forceLocalChanged = merged.forceLocal !== this.options.forceLocal;
    const wakeToggleChanged = merged.wakeWordEnabled !== this.options.wakeWordEnabled;

    this.options = merged;

    if (langChanged || biasChanged || forceLocalChanged) {
      this._rebuildRecognition(merged.forceLocal, { restart: this.recognizing });
    }

    if (wakeToggleChanged || langChanged || biasChanged || forceLocalChanged) {
      if (merged.wakeWordEnabled) {
        this._rebuildWakeRecognition(merged.forceLocal);
        if (!this.recognizing) {
          this.armWakeWord();
        }
      } else {
        this.disarmWakeWord();
      }
    }
  }

  startListening(options = {}) {
    try {
      console.log('[VoiceAssistant] startListening called with', options);
    } catch {
      /* noop */
    }

    const attemptStart = () => {
      if (!this.recognition) {
        this._buildRecognition(this.options.forceLocal);
      }

      const { autoRestart } = options;
      if (typeof autoRestart === 'boolean') {
        this.autoRestartWanted = autoRestart;
      } else {
        this.autoRestartWanted = !!this.options.autoRestart;
      }

      this.disarmWakeWord();
      try {
        this.recognition.continuous = !!this.autoRestartWanted;
      } catch {
        /* noop */
      }

      try {
        console.log('[VoiceAssistant] recognition.start()');
        this.recognition.start();
      } catch (err) {
        try {
          this.recognition.stop();
        } catch {
          /* noop */
        }
        try {
          this.recognition.start();
        } catch (err2) {
          try {
            console.warn('[VoiceAssistant] recognition.start() failed:', err2);
          } catch {
            /* noop */
          }
          this.callbacks.onError?.(err);
        }
      }
    };

    if (this.micPrimed) {
      attemptStart();
      return;
    }

    this.ensureMicPrimed()
      .then(attemptStart)
      .catch(err => {
        this.callbacks.onError?.({ error: 'mic-permission', detail: err });
      });
  }

  stopListening() {
    this.autoRestartWanted = false;
    try {
      this.recognition?.stop();
    } catch {
      /* noop */
    }
    this.callbacks.onInterim?.('');
    if (this.options.wakeWordEnabled) {
      this.armWakeWord();
    }
  }

  armWakeWord() {
    if (!this.options.wakeWordEnabled || !this.wakeRecognition) return;
    this.wakeArmed = true;
    if (this.recognizing || this.wakeListening) return;

    const tryStart = () => {
      this.callbacks.onWakeActiveChange?.(true);
      this.wakeListening = true;
      try {
        console.log('[VoiceAssistant] Wake recognition starting');
      } catch {
        /* noop */
      }
      try {
        this.wakeRecognition.start();
      } catch {
        this.wakeListening = false;
        this.callbacks.onWakeActiveChange?.(false);
        try {
          this.wakeRecognition.stop();
        } catch {
          /* noop */
        }
        setTimeout(() => this.armWakeWord(), 200);
      }
    };

    if (this.micPrimed) {
      tryStart();
      return;
    }

    this.ensureMicPrimed()
      .then(() => {
        tryStart();
      })
      .catch(err => {
        try {
          console.warn('[VoiceAssistant] Wake arm failed (mic):', err);
        } catch {
          /* noop */
        }
        this.callbacks.onError?.({ error: 'mic-permission', detail: err });
      });
  }

  disarmWakeWord() {
    this.wakeArmed = false;
    this.wakeListening = false;
    this.callbacks.onWakeActiveChange?.(false);
    if (!this.wakeRecognition) return;
    try {
      this.wakeRecognition.abort?.();
    } catch {
      /* noop */
    }
    try {
      this.wakeRecognition.stop();
    } catch {
      /* noop */
    }
  }

  _buildRecognition(forceLocal) {
    const result = buildRecognition(this.SR, {
      lang: this.options.lang,
      interimResults: this.options.interimResults,
      continuous: !!this.options.autoRestart,
      forceLocal,
      biasPhrases: this.options.biasPhrases,
      phraseBiasSupported: this.phraseBiasSupported,
      onPhraseBiasChange: supported => {
        this.phraseBiasSupported = supported;
        this.callbacks.onPhraseBiasChange?.(supported);
      },
    });

    this.recognition = result.recognition;
    this.phraseBiasSupported = result.phraseBiasSupported;

    this.recognition.onaudiostart = () => {
      try {
        console.log('[VoiceAssistant] recognition onaudiostart');
      } catch {
        /* noop */
      }
    };
    this.recognition.onspeechstart = () => {
      try {
        console.log('[VoiceAssistant] recognition onspeechstart');
      } catch {
        /* noop */
      }
    };
    this.recognition.onsoundstart = () => {
      try {
        console.log('[VoiceAssistant] recognition onsoundstart');
      } catch {
        /* noop */
      }
    };

    attachRecognitionHandlers(this.recognition, {
      onStart: () => {
        this.recognizing = true;
        this.callbacks.onListeningChange?.(true);
        this.callbacks.onInterim?.('');
        try {
          console.log('[VoiceAssistant] recognition onstart');
        } catch {
          /* noop */
        }
        playActivationSound();
      },
      onError: event => {
        try {
          console.warn('[VoiceAssistant] recognition onerror:', event);
        } catch {
          /* noop */
        }
        this.callbacks.onError?.(event);
      },
      onLocalError: () => {
        if (forceLocal) {
          this._rebuildRecognition(false, { restart: true });
        }
      },
      onPhraseBiasError: () => {
        if (this.phraseBiasSupported !== false) {
          this.phraseBiasSupported = false;
          this.callbacks.onPhraseBiasChange?.(false);
          this._rebuildRecognition(forceLocal, { restart: this.recognizing });
        }
      },
      onEnd: () => {
        this.recognizing = false;
        this.callbacks.onListeningChange?.(false);
        this.callbacks.onInterim?.('');
        try {
          console.log('[VoiceAssistant] recognition onend (autoRestartWanted=%o)', this.autoRestartWanted);
        } catch {
          /* noop */
        }
        playStoppedSound();
      },
      onFinal: finals => {
        if (finals.length) {
          const joined = finals.join(' ');
          try {
            console.log('[VoiceAssistant] Final transcript:', joined);
          } catch {
            /* noop */
          }
          playFinalResultSound();
          this.callbacks.onFinal?.(joined, finals);
        }
      },
      onInterim: interim => {
        if (interim) {
          try {
            console.log('[VoiceAssistant] Interim transcript:', interim);
          } catch {
            /* noop */
          }
        }
        this.callbacks.onInterim?.(interim);
      },
      onRestart: () => {
        this.startListening({ autoRestart: true });
      },
      onArmWakeWord: () => {
        if (this.options.wakeWordEnabled) {
          this.armWakeWord();
        }
      },
      getAutoRestartWanted: () => this.autoRestartWanted,
      getPhraseBiasSupported: () => this.phraseBiasSupported,
    });
  }

  _rebuildRecognition(forceLocal, { restart = false } = {}) {
    const wasRunning = this.recognizing;
    try {
      this.recognition?.stop();
    } catch {
      /* noop */
    }
    this._buildRecognition(forceLocal);
    if (restart || wasRunning) {
      this.startListening({ autoRestart: this.autoRestartWanted });
    } else if (this.options.wakeWordEnabled) {
      this.armWakeWord();
    }
  }

  _buildWakeRecognition(forceLocal) {
    const result = buildWakeRecognition(this.SR, {
      lang: this.options.lang,
      forceLocal,
      phraseBiasSupported: this.phraseBiasSupported,
    });
    this.wakeRecognition = result.recognition;
    this.phraseBiasSupported = result.phraseBiasSupported;

    this.wakeRecognition.onaudiostart = () => {
      try {
        console.log('[VoiceAssistant] Wake onaudiostart');
      } catch {
        /* noop */
      }
    };

    this.wakeRecognition.onstart = () => {
      this.wakeListening = true;
      this.callbacks.onWakeActiveChange?.(true);
      try {
        console.log('[VoiceAssistant] Wake onstart');
      } catch {
        /* noop */
      }
    };

    this.wakeRecognition.onerror = () => {
      try {
        console.warn('[VoiceAssistant] Wake onerror');
      } catch {
        /* noop */
      }
      this.wakeListening = false;
      if (!this.recognizing && this.wakeArmed) {
        safeWakeRestart(this.wakeRecognition);
      }
    };

    this.wakeRecognition.onnomatch = () => {
      this.wakeListening = false;
      if (!this.recognizing && this.wakeArmed) {
        safeWakeRestart(this.wakeRecognition);
      }
    };

    this.wakeRecognition.onend = () => {
      this.wakeListening = false;
      this.callbacks.onWakeActiveChange?.(false);
      try {
        console.log('[VoiceAssistant] Wake onend (wakeArmed=%o recognizing=%o)', this.wakeArmed, this.recognizing);
      } catch {
        /* noop */
      }
      if (!this.recognizing && this.wakeArmed) {
        safeWakeRestart(this.wakeRecognition);
      }
    };

    this.wakeRecognition.onresult = event => {
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const res = event.results[i];
        const text = res[0].transcript;
        try {
          console.log('[VoiceAssistant] Wake result candidate:', text);
        } catch {
          /* noop */
        }
        if (isWakeUtterance(text)) {
          try {
            console.log('[VoiceAssistant] Wake word detected:', text);
          } catch {
            /* noop */
          }
          this.callbacks.onWakeTriggered?.(text);
          this.wakeArmed = false;
          try {
            this.wakeRecognition.abort?.();
          } catch {
            /* noop */
          }
          this.startListening();
          return;
        }
      }
    };
  }

  _rebuildWakeRecognition(forceLocal) {
    try {
      this.wakeRecognition?.stop();
    } catch {
      /* noop */
    }
    this._buildWakeRecognition(forceLocal);
  }
}


