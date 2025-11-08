import * as THREE from 'three';

let audioContext = null;
let analyser = null;
let microphone = null;
let micStream = null;
let dataArray = null;
let rafId = null;
let audioOrb = null;
let lastT = 0;
let containerEl = null;

class ReactiveAudioOrb {
  constructor(container) {
    this.container = container;
    this.time = 0;

    this.levels = { bass: 0, mid: 0, treble: 0, overall: 0 };
    this.smoothAlpha = 0.15;

    this.targetActive = 0;
    this.active = 0;
    this.isSpeaking = false;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      50,
      container.clientWidth / container.clientHeight,
      0.1,
      1000,
    );
    this.camera.position.set(0, 0, 5);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    container.appendChild(this.renderer.domElement);

    const amb = new THREE.AmbientLight(0xffb380, 0.35);
    const key = new THREE.DirectionalLight(0xffffff, 0.9);
    key.position.set(2.5, 3.5, 4.5);
    const rim = new THREE.DirectionalLight(0x88ffe0, 0.45);
    rim.position.set(-3, -2, -4);
    this.scene.add(amb);
    this.scene.add(key);
    this.scene.add(rim);

    const sphereGeo = new THREE.SphereGeometry(1.0, 64, 64);
    this.sphereMat = new THREE.MeshPhysicalMaterial({
      color: 0xff6b35,
      emissive: 0xff6b35,
      emissiveIntensity: 0.22,
      metalness: 0.2,
      roughness: 0.3,
      clearcoat: 0.85,
      clearcoatRoughness: 0.2,
      transparent: true,
      opacity: 0.95,
    });
    this.sphere = new THREE.Mesh(sphereGeo, this.sphereMat);
    this.sphere.visible = false;
    this.scene.add(this.sphere);

    const cageGeo = new THREE.IcosahedronGeometry(1.02, 3);
    const wireGeo = new THREE.WireframeGeometry(cageGeo);
    this.cageMat = new THREE.LineBasicMaterial({
      color: 0xff6b35,
      transparent: true,
      opacity: 0.85,
    });
    this.cage = new THREE.LineSegments(wireGeo, this.cageMat);
    this.cage.visible = false;
    this.scene.add(this.cage);

    const glowGeo = new THREE.SphereGeometry(1.12, 64, 64);
    this.glowMat = new THREE.MeshBasicMaterial({
      color: 0xff6b35,
      transparent: true,
      opacity: 0.18,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    this.glow = new THREE.Mesh(glowGeo, this.glowMat);
    this.glow.visible = false;
    this.scene.add(this.glow);

    this._hslScratch = new THREE.Color();
    this.orangeColor = new THREE.Color(0xff6b35);

    this.waveformPoints = 128;
    this.waveformWidth = 8;
    this.waveformHeight = 2;

    this.waveformGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.waveformPoints * 3 * 2);
    const colors = new Float32Array(this.waveformPoints * 3 * 2);

    this.waveformGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.waveformGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    this.waveformMat = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
    });

    this.waveform = new THREE.LineSegments(this.waveformGeo, this.waveformMat);
    this.scene.add(this.waveform);

    this.borderGeo = new THREE.BufferGeometry();
    const borderPositions = new Float32Array(this.waveformPoints * 2 * 3);
    const borderColors = new Float32Array(this.waveformPoints * 2 * 3);

    this.borderGeo.setAttribute('position', new THREE.BufferAttribute(borderPositions, 3));
    this.borderGeo.setAttribute('color', new THREE.BufferAttribute(borderColors, 3));

    this.borderMat = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 1.0,
    });

    this.border = new THREE.LineLoop(this.borderGeo, this.borderMat);
    this.scene.add(this.border);

    this.waveformData = new Float32Array(this.waveformPoints);
    for (let i = 0; i < this.waveformPoints; i += 1) {
      this.waveformData[i] = 0;
    }

    const count = 160;
    const pGeo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i += 1) {
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 1.18 + Math.random() * 0.18;
      pos[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.particles = new THREE.Points(
      pGeo,
      new THREE.PointsMaterial({
        size: 0.035,
        color: 0xffa366,
        transparent: true,
        opacity: 0.45,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      }),
    );
    this.scene.add(this.particles);

    this.handleResize = () => {
      if (!this.container) return;
      this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    };

    window.addEventListener('resize', this.handleResize);

    window.AudioOrb = {
      setLevels: levels => this.setLevels(levels),
      setActive: active => this.setActive(active),
      setSpeaking: speaking => this.setSpeaking(speaking),
    };

    this.waveform.visible = false;
    this.border.visible = false;
  }

  dispose() {
    window.removeEventListener('resize', this.handleResize);
    if (this.renderer) {
      this.renderer.dispose();
      if (this.renderer.domElement?.parentNode) {
        this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
      }
    }
    this.scene = null;
    this.renderer = null;
    this.camera = null;
    if (window.AudioOrb) {
      window.AudioOrb.setLevels = () => {};
      window.AudioOrb.setActive = () => {};
      window.AudioOrb.setSpeaking = () => {};
    }
  }

  setLevels({ bass = 0, mid = 0, treble = 0, overall = 0 }) {
    const a = this.smoothAlpha;
    this.levels.bass = this.levels.bass + (bass - this.levels.bass) * a;
    this.levels.mid = this.levels.mid + (mid - this.levels.mid) * a;
    this.levels.treble = this.levels.treble + (treble - this.levels.treble) * a;
    this.levels.overall = this.levels.overall + (overall - this.levels.overall) * a;
  }

  setActive(isActive) {
    this.targetActive = isActive ? 1 : 0;
  }

  setSpeaking(isSpeaking) {
    this.isSpeaking = !!isSpeaking;
    if (this.container) {
      if (isSpeaking) {
        this.container.classList.add('speaking');
      } else {
        this.container.classList.remove('speaking');
      }
    }

    if (this.sphere) this.sphere.visible = false;
    if (this.cage) this.cage.visible = !!isSpeaking;
    if (this.glow) this.glow.visible = !!isSpeaking;
    if (this.waveform) this.waveform.visible = false;
    if (this.border) this.border.visible = false;
  }

  updateWaveform(fftData) {
    if (!this.waveformGeo || !fftData || (this.waveform && !this.waveform.visible)) return;

    const posAttr = this.waveformGeo.getAttribute('position');
    const colorAttr = this.waveformGeo.getAttribute('color');
    const positions = posAttr.array;
    const colors = colorAttr.array;

    const segmentWidth = this.waveformWidth / this.waveformPoints;
    const startX = -this.waveformWidth / 2;

    const userColor = new THREE.Color(0xff6b35);
    const aiColor = new THREE.Color(0x00ff88);
    const baseColor = this.isSpeaking ? aiColor : userColor;

    const smoothAlpha = 0.3;
    const fftLength = fftData.length;
    const samplesPerPoint = Math.max(1, Math.floor(fftLength / this.waveformPoints));

    for (let i = 0; i < this.waveformPoints; i += 1) {
      let sum = 0;
      const startIdx = i * samplesPerPoint;
      const endIdx = Math.min(startIdx + samplesPerPoint, fftLength);
      for (let j = startIdx; j < endIdx; j += 1) {
        sum += fftData[j] / 255;
      }
      const value = sum / (endIdx - startIdx || 1);

      this.waveformData[i] = this.waveformData[i] + (value - this.waveformData[i]) * smoothAlpha;

      const centerDist = Math.abs(i - this.waveformPoints / 2) / (this.waveformPoints / 2);
      const fadeFactor = 1 - Math.pow(centerDist, 1.5);

      const height = this.waveformData[i] * this.waveformHeight * fadeFactor * this.active;

      const x = startX + i * segmentWidth;

      const topIdx = i * 6;
      positions[topIdx] = x;
      positions[topIdx + 1] = height;
      positions[topIdx + 2] = 0;

      const bottomIdx = i * 6 + 3;
      positions[bottomIdx] = x;
      positions[bottomIdx + 1] = -height;
      positions[bottomIdx + 2] = 0;

      const colorIntensity = fadeFactor * (0.6 + this.waveformData[i] * 0.4);
      const r = baseColor.r * colorIntensity;
      const g = baseColor.g * colorIntensity;
      const b = baseColor.b * colorIntensity;

      colors[topIdx] = r;
      colors[topIdx + 1] = g;
      colors[topIdx + 2] = b;

      colors[bottomIdx] = r;
      colors[bottomIdx + 1] = g;
      colors[bottomIdx + 2] = b;
    }

    posAttr.needsUpdate = true;
    colorAttr.needsUpdate = true;

    this.updateBorder();
  }

  updateBorder() {
    if (!this.borderGeo || (this.border && !this.border.visible)) return;

    const borderPosAttr = this.borderGeo.getAttribute('position');
    const borderColorAttr = this.borderGeo.getAttribute('color');
    const borderPositions = borderPosAttr.array;
    const borderColors = borderColorAttr.array;

    const segmentWidth = this.waveformWidth / this.waveformPoints;
    const startX = -this.waveformWidth / 2;
    const borderOffset = 0.02;

    const userColor = new THREE.Color(0xff6b35);
    const aiColor = new THREE.Color(0x00ff88);
    const borderColor = this.isSpeaking ? aiColor : userColor;

    let borderIdx = 0;
    for (let i = 0; i < this.waveformPoints; i += 1) {
      const centerDist = Math.abs(i - this.waveformPoints / 2) / (this.waveformPoints / 2);
      const fadeFactor = 1 - Math.pow(centerDist, 1.5);
      const height = this.waveformData[i] * this.waveformHeight * fadeFactor * this.active;

      const x = startX + i * segmentWidth;
      const y = height + borderOffset;

      borderPositions[borderIdx * 3] = x;
      borderPositions[borderIdx * 3 + 1] = y;
      borderPositions[borderIdx * 3 + 2] = 0;

      const colorIntensity = fadeFactor * (0.9 + this.waveformData[i] * 0.1);
      borderColors[borderIdx * 3] = borderColor.r * colorIntensity;
      borderColors[borderIdx * 3 + 1] = borderColor.g * colorIntensity;
      borderColors[borderIdx * 3 + 2] = borderColor.b * colorIntensity;

      borderIdx += 1;
    }

    for (let i = this.waveformPoints - 1; i >= 0; i -= 1) {
      const centerDist = Math.abs(i - this.waveformPoints / 2) / (this.waveformPoints / 2);
      const fadeFactor = 1 - Math.pow(centerDist, 1.5);
      const height = this.waveformData[i] * this.waveformHeight * fadeFactor * this.active;

      const x = startX + i * segmentWidth;
      const y = -height - borderOffset;

      borderPositions[borderIdx * 3] = x;
      borderPositions[borderIdx * 3 + 1] = y;
      borderPositions[borderIdx * 3 + 2] = 0;

      const colorIntensity = fadeFactor * (0.9 + this.waveformData[i] * 0.1);
      borderColors[borderIdx * 3] = borderColor.r * colorIntensity;
      borderColors[borderIdx * 3 + 1] = borderColor.g * colorIntensity;
      borderColors[borderIdx * 3 + 2] = borderColor.b * colorIntensity;

      borderIdx += 1;
    }

    borderPosAttr.needsUpdate = true;
    borderColorAttr.needsUpdate = true;
  }

  update(dt) {
    this.time += dt;

    const ease = 0.06;
    this.active += (this.targetActive - this.active) * ease;

    const { overall } = this.levels;

    const camOrbit = 0.05;
    this.camera.position.x = Math.sin(this.time * 0.12) * camOrbit;
    this.camera.position.y = Math.cos(this.time * 0.08) * camOrbit * 0.5;
    this.camera.lookAt(0, 0, 0);

    const pulse = Math.min(1, this.levels.overall) * this.active;
    if (this.particles) {
      const particlesActive = this.targetActive > 0;
      this.particles.visible = particlesActive;
      if (particlesActive) {
        this.particles.rotation.y += 0.0003 + pulse * 0.001;
        if (this.particles.material) {
          this.particles.material.opacity = 0.42 + this.levels.overall * 0.18 * this.active;
        }
      } else if (this.particles.material) {
        this.particles.material.opacity = 0;
      }
    }

    if (this.sphere) {
      if (this.isSpeaking && this.active > 0.001) {
        const growth = Math.min(0.12, overall * 0.25);
        const scale = 1.0 + growth * this.active;

        if (this.cage) {
          this.cage.scale.set(scale, scale, scale);
          this.cage.rotation.y += 0.002 + overall * 0.004;
          this.cage.rotation.x += 0.0007 + overall * 0.0015;
          if (this.cageMat) {
            this.cageMat.opacity = 0.7 + Math.min(0.25, overall * 0.3 * this.active);
          }
        }
        if (this.sphereMat && this.orangeColor) {
          this.sphereMat.color.copy(this.orangeColor);
          this.sphereMat.emissive.copy(this.orangeColor);
          this.sphereMat.emissiveIntensity = 0.2 + Math.min(0.4, overall * 0.6) * this.active;
          this.sphereMat.opacity = 0.05;
        }
        if (this.glow && this.glowMat && this.orangeColor) {
          const glowScale = scale * 1.04;
          this.glow.scale.set(glowScale, glowScale, glowScale);
          this.glowMat.opacity = 0.05;
          this.glowMat.color.copy(this.orangeColor);
        }
      } else {
        if (this.cage) {
          this.cage.scale.set(1, 1, 1);
          this.cage.rotation.set(0, 0, 0);
          if (this.cageMat) this.cageMat.opacity = 0.85;
        }
        if (this.sphereMat) {
          this.sphereMat.emissiveIntensity = 0.16;
          this.sphereMat.opacity = 0.9;
        }
        if (this.glow && this.glowMat) {
          this.glow.scale.set(1.04, 1.04, 1.04);
          this.glowMat.opacity = 0.08;
        }
      }
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
}

function ensureAudioGraph() {
  if (!audioContext || audioContext.state === 'closed') {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (!analyser) {
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.88;
  }
  if (!dataArray) {
    dataArray = new Uint8Array(analyser.frequencyBinCount);
  }
}

function disconnectAnalyserFromDest() {
  try {
    analyser?.disconnect(audioContext.destination);
  } catch {
    /* noop */
  }
}

function connectAnalyserToDest() {
  try {
    analyser?.connect(audioContext.destination);
  } catch {
    /* noop */
  }
}

function routeMicToAnalyser() {
  if (!microphone || !analyser) return;
  try {
    microphone.disconnect();
  } catch {
    /* noop */
  }
  try {
    microphone.connect(analyser);
  } catch {
    /* noop */
  }
  disconnectAnalyserFromDest();
}

function getBandLevelsFromFFT(fft, sampleRate) {
  const N = fft.length;
  const nyquist = sampleRate / 2;
  const binHz = nyquist / N;
  const band = (a, b) => {
    let sum = 0;
    let count = 0;
    const i1 = Math.max(0, Math.floor(a / binHz));
    const i2 = Math.min(N - 1, Math.ceil(b / binHz));
    for (let i = i1; i <= i2; i += 1) {
      sum += fft[i] * fft[i];
      count += 1;
    }
    return Math.min(1, Math.sqrt(sum / Math.max(1, count)) / 140);
  };
  const bass = band(20, 250);
  const mid = band(250, 2000);
  const treble = band(2000, 8000);
  const overall = Math.min(1, (bass * 0.5 + mid * 0.35 + treble * 0.15) * 1.1);
  return { bass, mid, treble, overall };
}

function loop() {
  rafId = requestAnimationFrame(loop);
  const now = performance.now();
  const dt = Math.min(0.05, Math.max(0.001, (now - lastT) / 1000));
  lastT = now;

  if (analyser && dataArray) {
    analyser.getByteFrequencyData(dataArray);
    const levels = getBandLevelsFromFFT(dataArray, audioContext?.sampleRate || 44100);
    audioOrb?.setLevels(levels);
    audioOrb?.updateWaveform(dataArray);
  }
  audioOrb?.update(dt);
}

export function ensureVisualizerLoop() {
  ensureAudioGraph();
  if (!lastT) lastT = performance.now();
  if (!rafId) loop();
}

function initVisualizer() {
  if (!containerEl) return;
  if (audioOrb) return;
  audioOrb = new ReactiveAudioOrb(containerEl);
  ensureVisualizerLoop();
}

export function setAudioVisualizerContainer(el) {
  if (containerEl === el) return;
  containerEl = el;
  if (audioOrb) {
    audioOrb.dispose();
    audioOrb = null;
  }
  if (containerEl) {
    initVisualizer();
  }
}

export async function ensureAudioContextRunning() {
  ensureAudioGraph();
  if (audioContext?.state === 'suspended') {
    try {
      await audioContext.resume();
    } catch (err) {
      console.warn('[VoiceAssistant] Unable to resume AudioContext:', err);
    }
  }
}

export async function startAudioVisualizer(withMic = true) {
  if (!containerEl) return;
  initVisualizer();
  ensureAudioGraph();

  if (audioContext?.state === 'suspended') {
    try {
      await audioContext.resume();
    } catch {
      /* noop */
    }
  }

  if (!withMic || (audioContext && microphone)) {
    lastT = performance.now();
    if (!rafId) loop();
    return;
  }

  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    microphone = audioContext.createMediaStreamSource(micStream);
    routeMicToAnalyser();
    lastT = performance.now();
    if (!rafId) loop();
  } catch (err) {
    console.warn('Microphone access denied or unavailable:', err);
    lastT = performance.now();
    if (!rafId) loop();
  }
}

export function stopAudioVisualizer() {
  try {
    microphone?.disconnect();
  } catch {
    /* noop */
  }
  microphone = null;
  if (micStream) {
    micStream.getTracks().forEach(track => track.stop());
    micStream = null;
  }
  if (window.AudioOrb) {
    window.AudioOrb.setActive(false);
    window.AudioOrb.setSpeaking(false);
  }
}

export function routeTTSToAnalyser(ttsAudioEl) {
  ensureAudioGraph();
  if (!audioContext || !analyser || !ttsAudioEl) return null;
  try {
    microphone?.disconnect();
  } catch {
    /* noop */
  }
  let ttsSourceNode = null;
  try {
    ttsSourceNode = audioContext.createMediaElementSource(ttsAudioEl);
    ttsSourceNode.connect(analyser);
  } catch {
    /* noop */
  }
  connectAnalyserToDest();
  return ttsSourceNode;
}

export function cleanupTTSAudio(ttsSourceNode, ttsAudioEl) {
  if (ttsSourceNode) {
    try {
      ttsSourceNode.disconnect();
    } catch {
      /* noop */
    }
  }
  if (ttsAudioEl) {
    try {
      ttsAudioEl.pause();
    } catch {
      /* noop */
    }
    URL.revokeObjectURL(ttsAudioEl.src);
    ttsAudioEl.src = '';
  }
  if (microphone) {
    routeMicToAnalyser();
  }
}

export function ensureVisualizerActive() {
  if (!containerEl) return;
  initVisualizer();
  ensureVisualizerLoop();
}

export function disposeVisualizer() {
  if (audioOrb) {
    audioOrb.dispose();
    audioOrb = null;
  }
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
  stopAudioVisualizer();
  if (micStream) {
    micStream.getTracks().forEach(track => track.stop());
    micStream = null;
  }
}


