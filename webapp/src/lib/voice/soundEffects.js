let audioContext = null;

function getAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }

  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }

  return audioContext;
}

function playTone(frequency, duration, type = 'sine', volume = 0.3) {
  const ctx = getAudioContext();
  const oscillator = ctx.createOscillator();
  const gainNode = ctx.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(ctx.destination);

  oscillator.type = type;
  oscillator.frequency.value = frequency;

  const now = ctx.currentTime;
  gainNode.gain.setValueAtTime(0, now);
  gainNode.gain.linearRampToValueAtTime(volume, now + 0.01);
  gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration);

  oscillator.start(now);
  oscillator.stop(now + duration);
}

function playSequence(notes, duration = 0.1, type = 'sine', volume = 0.3) {
  notes.forEach((frequency, index) => {
    const delay = index * duration * 0.8;
    setTimeout(() => playTone(frequency, duration, type, volume), delay * 1000);
  });
}

export function playActivationSound() {
  playSequence([440, 554, 659], 0.08, 'sine', 0.25);
}

export function playStoppedSound() {
  playSequence([659, 554, 440], 0.08, 'sine', 0.25);
}

export function playFinalResultSound() {
  playSequence([523, 659, 784, 988], 0.08, 'sine', 0.25);
}

export function playTTSStartSound() {
  playSequence([523, 659, 784], 0.1, 'sine', 0.3);
}


