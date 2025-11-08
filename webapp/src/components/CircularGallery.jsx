import { Camera, Mesh, Plane, Program, Renderer, Texture, Transform } from 'ogl';
import { useEffect, useRef } from 'react';
import './CircularGallery.css';

function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

function lerp(p1, p2, t) {
  return p1 + (p2 - p1) * t;
}

function autoBind(instance) {
  const proto = Object.getPrototypeOf(instance);
  Object.getOwnPropertyNames(proto).forEach(key => {
    if (key !== 'constructor' && typeof instance[key] === 'function') {
      instance[key] = instance[key].bind(instance);
    }
  });
}

function createTextTexture(gl, text, font = 'bold 30px monospace', color = 'black') {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  context.font = font;
  const metrics = context.measureText(text);
  const textWidth = Math.ceil(metrics.width);
  const textHeight = Math.ceil(parseInt(font, 10) * 1.2);
  canvas.width = textWidth + 20;
  canvas.height = textHeight + 20;
  context.font = font;
  context.fillStyle = color;
  context.textBaseline = 'middle';
  context.textAlign = 'center';
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  const texture = new Texture(gl, { generateMipmaps: false });
  texture.image = canvas;
  return { texture, width: canvas.width, height: canvas.height };
}

class Title {
  constructor({ gl, plane, renderer, text, textColor = '#545050', font = '30px sans-serif' }) {
    autoBind(this);
    this.gl = gl;
    this.plane = plane;
    this.renderer = renderer;
    this.text = text;
    this.textColor = textColor;
    this.font = font;
    this.createMesh();
  }

  createMesh() {
    const { texture, width, height } = createTextTexture(this.gl, this.text, this.font, this.textColor);
    const geometry = new Plane(this.gl);
    const program = new Program(this.gl, {
      vertex: `
        attribute vec3 position;
        attribute vec2 uv;
        uniform mat4 modelViewMatrix;
        uniform mat4 projectionMatrix;
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragment: `
        precision highp float;
        uniform sampler2D tMap;
        varying vec2 vUv;
        void main() {
          vec4 color = texture2D(tMap, vUv);
          if (color.a < 0.1) discard;
          gl_FragColor = color;
        }
      `,
      uniforms: { tMap: { value: texture } },
      transparent: true
    });
    this.mesh = new Mesh(this.gl, { geometry, program });
    const aspect = width / height;
    const textHeight = this.plane.scale.y * 0.15;
    const textWidth = textHeight * aspect;
    this.mesh.scale.set(textWidth, textHeight, 1);
    // Adjust title position for 90° rotated parent - position to the right of image
    this.mesh.position.x = this.plane.scale.x * 0.5 + textWidth * 0.5 + 0.05;
    this.mesh.position.y = 0;
    this.mesh.setParent(this.plane);
  }
}

class Media {
  constructor({
    geometry,
    gl,
    image,
    index,
    length,
    renderer,
    scene,
    screen,
    text,
    viewport,
    bend,
    textColor,
    borderRadius = 0,
    font
  }) {
    this.extra = 0;
    this.geometry = geometry;
    this.gl = gl;
    this.image = image;
    this.index = index;
    this.length = length;
    this.renderer = renderer;
    this.scene = scene;
    this.screen = screen;
    this.text = text;
    this.viewport = viewport;
    this.bend = bend;
    this.textColor = textColor;
    this.borderRadius = borderRadius;
    this.font = font;
    this.createShader();
    this.createMesh();
    this.createTitle();
    this.onResize();
  }

  createShader() {
    const texture = new Texture(this.gl, {
      generateMipmaps: true
    });
    this.program = new Program(this.gl, {
      depthTest: false,
      depthWrite: false,
      vertex: `
        precision highp float;
        attribute vec3 position;
        attribute vec2 uv;
        uniform mat4 modelViewMatrix;
        uniform mat4 projectionMatrix;
        uniform float uTime;
        uniform float uSpeed;
        varying vec2 vUv;
        void main() {
          vUv = uv;
          vec3 p = position;
          // Only apply wiggle effect when there's movement (speed > threshold)
          float speedFactor = smoothstep(0.0, 0.5, abs(uSpeed));
          p.z = (sin(p.x * 4.0 + uTime) * 1.5 + cos(p.y * 2.0 + uTime) * 1.5) * speedFactor * 0.15;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
        }
      `,
      fragment: `
        precision highp float;
        uniform vec2 uImageSizes;
        uniform vec2 uPlaneSizes;
        uniform sampler2D tMap;
        uniform float uBorderRadius;
        varying vec2 vUv;
        
        float roundedBoxSDF(vec2 p, vec2 b, float r) {
          vec2 d = abs(p) - b;
          return length(max(d, vec2(0.0))) + min(max(d.x, d.y), 0.0) - r;
        }
        
        void main() {
          vec2 p = vUv - 0.5;
          
          // Outer container with proper rounded corners
          float outerSize = 0.49;
          float outerD = roundedBoxSDF(p, vec2(outerSize - uBorderRadius), uBorderRadius);
          float edgeSmooth = 0.002;
          float outerAlpha = 1.0 - smoothstep(-edgeSmooth, edgeSmooth, outerD);
          
          // Inner area for image with padding (matching enlarged view: 16px padding)
          // 16px relative to typical 200-250px image size = ~0.08 in UV space
          float innerPadding = 0.08;
          float innerSize = outerSize - innerPadding;
          float innerRadius = uBorderRadius * 0.8;
          float innerD = roundedBoxSDF(p, vec2(innerSize - innerRadius), innerRadius);
          float imageAlpha = 1.0 - smoothstep(-edgeSmooth, edgeSmooth, innerD);
          
          // Border frame (area between outer and inner)
          float borderMask = smoothstep(-edgeSmooth, edgeSmooth, innerD);
          
          // Calculate UV for the image within the padded area
          float scale = innerSize / outerSize;
          vec2 imageUV = (p / scale) + 0.5;
          
          // Apply image sizing ratio
          vec2 ratio = vec2(
            min((uPlaneSizes.x / uPlaneSizes.y) / (uImageSizes.x / uImageSizes.y), 1.0),
            min((uPlaneSizes.y / uPlaneSizes.x) / (uImageSizes.y / uImageSizes.x), 1.0)
          );
          vec2 uv = vec2(
            imageUV.x * ratio.x + (1.0 - ratio.x) * 0.5,
            imageUV.y * ratio.y + (1.0 - ratio.y) * 0.5
          );
          
          vec4 imageColor = texture2D(tMap, uv);
          
          // Milk glass border color - matching enlarged view (18% opacity white)
          vec3 borderColor = vec3(1.0, 1.0, 1.0);
          
          // Combine: border frame + image
          vec3 finalColor = mix(imageColor.rgb, borderColor, borderMask);
          // Border opacity: 0.18 to match --glass-bg-medium
          float finalAlpha = outerAlpha * mix(imageAlpha, 0.18, borderMask);
          
          gl_FragColor = vec4(finalColor, finalAlpha);
        }
      `,
      uniforms: {
        tMap: { value: texture },
        uPlaneSizes: { value: [0, 0] },
        uImageSizes: { value: [0, 0] },
        uSpeed: { value: 0 },
        uTime: { value: 100 * Math.random() },
        uBorderRadius: { value: 0.15 }
      },
      transparent: true
    });
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = this.image;
    img.onload = () => {
      texture.image = img;
      this.program.uniforms.uImageSizes.value = [img.naturalWidth, img.naturalHeight];
    };
  }

  createMesh() {
    this.plane = new Mesh(this.gl, {
      geometry: this.geometry,
      program: this.program
    });
    this.plane.rotation.z = 0; // No rotation - natural orientation
    this.plane.setParent(this.scene);
  }

  createTitle() {
    this.title = new Title({
      gl: this.gl,
      plane: this.plane,
      renderer: this.renderer,
      text: this.text,
      textColor: this.textColor,
      fontFamily: this.font
    });
  }

  update(scroll, direction) {
    // Changed to vertical positioning (Y-axis)
    this.plane.position.y = this.x - scroll.current - this.extra;
    const y = this.plane.position.y;
    const H = this.viewport.height / 2;
    if (this.bend === 0) {
      this.plane.position.x = 0;
      this.plane.rotation.z = 0; // No rotation
    } else {
      const B_abs = Math.abs(this.bend);
      const R = (H * H + B_abs * B_abs) / (2 * B_abs);
      const effectiveY = Math.min(Math.abs(y), H);
      const arc = R - Math.sqrt(R * R - effectiveY * effectiveY);
      if (this.bend > 0) {
        // Outward curve (positive X for curving away from center)
        this.plane.position.x = arc;
        this.plane.rotation.z = -Math.sign(y) * Math.asin(effectiveY / R);
      } else {
        this.plane.position.x = -arc;
        this.plane.rotation.z = Math.sign(y) * Math.asin(effectiveY / R);
      }
    }
    
    this.speed = scroll.current - scroll.last;
    this.program.uniforms.uTime.value += 0.04;
    this.program.uniforms.uSpeed.value = this.speed;
    const planeOffset = this.plane.scale.y / 2;
    const viewportOffset = this.viewport.height / 2;
    this.isBefore = this.plane.position.y + planeOffset < -viewportOffset;
    this.isAfter = this.plane.position.y - planeOffset > viewportOffset;
    if (direction === 'right' && this.isBefore) {
      this.extra -= this.widthTotal;
      this.isBefore = this.isAfter = false;
    }
    if (direction === 'left' && this.isAfter) {
      this.extra += this.widthTotal;
      this.isBefore = this.isAfter = false;
    }
  }

  onResize({ screen, viewport } = {}) {
    if (screen) this.screen = screen;
    if (viewport) {
      this.viewport = viewport;
      if (this.plane.program.uniforms.uViewportSizes) {
        this.plane.program.uniforms.uViewportSizes.value = [this.viewport.width, this.viewport.height];
      }
    }
    this.scale = this.screen.height / 1500;
    // Reduced size to show ~5 images at once
    this.plane.scale.y = (this.viewport.height * (250 * this.scale)) / this.screen.height;
    this.plane.scale.x = (this.viewport.width * (200 * this.scale)) / this.screen.width;
    this.plane.program.uniforms.uPlaneSizes.value = [this.plane.scale.x, this.plane.scale.y];
    
    this.padding = 1.5;
    this.width = this.plane.scale.x + this.padding;
    this.widthTotal = this.width * this.length;
    this.x = this.width * this.index;
  }
}

class App {
  constructor(
    container,
    {
      items,
      bend,
      textColor = '#ffffff',
      borderRadius = 0,
      font = 'bold 30px Figtree',
      scrollSpeed = 2,
      scrollEase = 0.05,
      onImageClick
    } = {}
  ) {
    document.documentElement.classList.remove('no-js');
    this.container = container;
    this.scrollSpeed = scrollSpeed;
    this.scroll = { ease: scrollEase, current: 0, target: 0, last: 0 };
    this.onCheckDebounce = debounce(this.onCheck, 200);
    this.onImageClick = onImageClick;
    this.createRenderer();
    this.createCamera();
    this.createScene();
    this.onResize();
    this.createGeometry();
    this.createMedias(items, bend, textColor, borderRadius, font);
    this.update();
    this.addEventListeners();
  }

  createRenderer() {
    this.renderer = new Renderer({
      alpha: true,
      antialias: true,
      dpr: Math.min(window.devicePixelRatio || 1, 2)
    });
    this.gl = this.renderer.gl;
    this.gl.clearColor(0, 0, 0, 0);
    this.container.appendChild(this.gl.canvas);
  }

  createCamera() {
    this.camera = new Camera(this.gl);
    this.camera.fov = 45;
    this.camera.position.z = 20;
  }

  createScene() {
    this.scene = new Transform();
  }

  createGeometry() {
    this.planeGeometry = new Plane(this.gl, {
      heightSegments: 50,
      widthSegments: 100
    });
  }

  createMedias(items, bend = 1, textColor, borderRadius, font) {
    const defaultItems = [
      { image: `https://picsum.photos/seed/1/800/600?grayscale`, text: 'Bridge' },
      { image: `https://picsum.photos/seed/2/800/600?grayscale`, text: 'Desk Setup' },
      { image: `https://picsum.photos/seed/3/800/600?grayscale`, text: 'Waterfall' },
      { image: `https://picsum.photos/seed/4/800/600?grayscale`, text: 'Strawberries' },
      { image: `https://picsum.photos/seed/5/800/600?grayscale`, text: 'Deep Diving' },
      { image: `https://picsum.photos/seed/16/800/600?grayscale`, text: 'Train Track' },
      { image: `https://picsum.photos/seed/17/800/600?grayscale`, text: 'Santorini' },
      { image: `https://picsum.photos/seed/8/800/600?grayscale`, text: 'Blurry Lights' },
      { image: `https://picsum.photos/seed/9/800/600?grayscale`, text: 'New York' },
      { image: `https://picsum.photos/seed/10/800/600?grayscale`, text: 'Good Boy' },
      { image: `https://picsum.photos/seed/21/800/600?grayscale`, text: 'Coastline' },
      { image: `https://picsum.photos/seed/12/800/600?grayscale`, text: 'Palm Trees' }
    ];
    const galleryItems = items && items.length ? items : defaultItems;
    this.mediasImages = galleryItems.concat(galleryItems);
    this.medias = this.mediasImages.map((data, index) => {
      return new Media({
        geometry: this.planeGeometry,
        gl: this.gl,
        image: data.image,
        index,
        length: this.mediasImages.length,
        renderer: this.renderer,
        scene: this.scene,
        screen: this.screen,
        text: data.text,
        viewport: this.viewport,
        bend,
        textColor,
        borderRadius,
        font
      });
    });
  }

  onTouchDown(e) {
    this.isDown = true;
    this.scroll.position = this.scroll.current;
    this.start = e.touches ? e.touches[0].clientX : e.clientX;
    this.hasMoved = false;
  }

  onTouchMove(e) {
    if (!this.isDown) return;
    const x = e.touches ? e.touches[0].clientX : e.clientX;
    const distance = (x - this.start) * (this.scrollSpeed * 0.025);
    if (Math.abs(distance) > 2) {
      this.hasMoved = true;
    }
    this.scroll.target = this.scroll.position - distance;
  }

  onTouchUp(e) {
    if (this.isDown && !this.hasMoved && this.onImageClick) {
      // This was a click, not a drag
      this.onClick(e);
    }
    this.isDown = false;
    this.onCheck();
  }

  onClick(e) {
    if (!this.onImageClick || !this.medias || !this.medias.length) return;
    
    // Find the image closest to center (using Y-axis for vertical gallery)
    let closestMedia = null;
    let minDistance = Infinity;
    
    this.medias.forEach(media => {
      const distance = Math.abs(media.plane.position.y);
      if (distance < minDistance) {
        minDistance = distance;
        closestMedia = media;
      }
    });
    
    if (closestMedia) {
      // Get the original image data
      const halfLength = this.mediasImages.length / 2;
      const originalIndex = closestMedia.index % halfLength;
      const imageData = this.mediasImages[originalIndex];
      this.onImageClick(imageData);
    }
  }

  onWheel(e) {
    const delta = e.deltaY || e.wheelDelta || e.detail;
    this.scroll.target += (delta > 0 ? this.scrollSpeed : -this.scrollSpeed) * 0.2;
    this.onCheckDebounce();
  }

  onCheck() {
    if (!this.medias || !this.medias[0]) return;
    const width = this.medias[0].width;
    const itemIndex = Math.round(Math.abs(this.scroll.target) / width);
    const item = width * itemIndex;
    this.scroll.target = this.scroll.target < 0 ? -item : item;
  }

  onResize() {
    this.screen = {
      width: this.container.clientWidth,
      height: this.container.clientHeight
    };
    this.renderer.setSize(this.screen.width, this.screen.height);
    this.camera.perspective({
      aspect: this.screen.width / this.screen.height
    });
    const fov = (this.camera.fov * Math.PI) / 180;
    const height = 2 * Math.tan(fov / 2) * this.camera.position.z;
    const width = height * this.camera.aspect;
    this.viewport = { width, height };
    if (this.medias) {
      this.medias.forEach(media => media.onResize({ screen: this.screen, viewport: this.viewport }));
    }
  }

  update() {
    this.scroll.current = lerp(this.scroll.current, this.scroll.target, this.scroll.ease);
    const direction = this.scroll.current > this.scroll.last ? 'right' : 'left';
    if (this.medias) {
      this.medias.forEach(media => media.update(this.scroll, direction));
    }
    this.renderer.render({ scene: this.scene, camera: this.camera });
    this.scroll.last = this.scroll.current;
    this.raf = window.requestAnimationFrame(this.update.bind(this));
  }

  addEventListeners() {
    this.boundOnResize = this.onResize.bind(this);
    this.boundOnWheel = this.onWheel.bind(this);
    this.boundOnTouchDown = this.onTouchDown.bind(this);
    this.boundOnTouchMove = this.onTouchMove.bind(this);
    this.boundOnTouchUp = this.onTouchUp.bind(this);
    window.addEventListener('resize', this.boundOnResize);
    window.addEventListener('mousewheel', this.boundOnWheel);
    window.addEventListener('wheel', this.boundOnWheel);
    window.addEventListener('mousedown', this.boundOnTouchDown);
    window.addEventListener('mousemove', this.boundOnTouchMove);
    window.addEventListener('mouseup', this.boundOnTouchUp);
    window.addEventListener('touchstart', this.boundOnTouchDown);
    window.addEventListener('touchmove', this.boundOnTouchMove);
    window.addEventListener('touchend', this.boundOnTouchUp);
  }

  destroy() {
    window.cancelAnimationFrame(this.raf);
    window.removeEventListener('resize', this.boundOnResize);
    window.removeEventListener('mousewheel', this.boundOnWheel);
    window.removeEventListener('wheel', this.boundOnWheel);
    window.removeEventListener('mousedown', this.boundOnTouchDown);
    window.removeEventListener('mousemove', this.boundOnTouchMove);
    window.removeEventListener('mouseup', this.boundOnTouchUp);
    window.removeEventListener('touchstart', this.boundOnTouchDown);
    window.removeEventListener('touchmove', this.boundOnTouchMove);
    window.removeEventListener('touchend', this.boundOnTouchUp);
    if (this.renderer && this.renderer.gl && this.renderer.gl.canvas.parentNode) {
      this.renderer.gl.canvas.parentNode.removeChild(this.renderer.gl.canvas);
    }
  }
}

// Helper function to convert text to kebab-case for data-nav-id
function toKebabCase(text) {
  return text
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

export default function CircularGallery({
  items,
  bend = 3,
  textColor = '#ffffff',
  borderRadius = 0.05,
  font = 'bold 30px Figtree',
  scrollSpeed = 1,
  scrollEase = 0.02,
  onImageClick
}) {
  const containerRef = useRef(null);
  const appRef = useRef(null);

  // Default items for the gallery
  const defaultItems = [
    { image: `https://picsum.photos/seed/1/800/600?grayscale`, text: 'Bridge' },
    { image: `https://picsum.photos/seed/2/800/600?grayscale`, text: 'Desk Setup' },
    { image: `https://picsum.photos/seed/3/800/600?grayscale`, text: 'Waterfall' },
    { image: `https://picsum.photos/seed/4/800/600?grayscale`, text: 'Strawberries' },
    { image: `https://picsum.photos/seed/5/800/600?grayscale`, text: 'Deep Diving' },
    { image: `https://picsum.photos/seed/16/800/600?grayscale`, text: 'Train Track' },
    { image: `https://picsum.photos/seed/17/800/600?grayscale`, text: 'Santorini' },
    { image: `https://picsum.photos/seed/8/800/600?grayscale`, text: 'Blurry Lights' },
    { image: `https://picsum.photos/seed/9/800/600?grayscale`, text: 'New York' },
    { image: `https://picsum.photos/seed/10/800/600?grayscale`, text: 'Good Boy' },
    { image: `https://picsum.photos/seed/21/800/600?grayscale`, text: 'Coastline' },
    { image: `https://picsum.photos/seed/12/800/600?grayscale`, text: 'Palm Trees' }
  ];

  const galleryItems = items && items.length ? items : defaultItems;

  // Handler for clicking on a specific image by title
  const handleImageNavigation = (imageData) => {
    // Store current scroll position to prevent reset
    const currentScrollTarget = appRef.current?.scroll?.target;
    
    // Find the media object that's closest to center (the one being clicked)
    if (appRef.current?.medias && containerRef.current) {
      let closestMedia = null;
      let minDistance = Infinity;
      
      appRef.current.medias.forEach(media => {
        const distance = Math.abs(media.plane.position.y);
        if (distance < minDistance) {
          minDistance = distance;
          closestMedia = media;
        }
      });
      
      if (closestMedia && closestMedia.plane) {
        // Create a temporary highlight overlay
        const overlay = document.createElement('div');
        const galleryRect = containerRef.current.getBoundingClientRect();
        
        // Calculate the position and size based on the plane
        const planeScale = closestMedia.plane.scale;
        const viewport = appRef.current.viewport;
        
        // Approximate size in pixels (this is a rough conversion from WebGL units)
        const imageHeight = (planeScale.y / viewport.height) * galleryRect.height * 0.4;
        const imageWidth = imageHeight * (planeScale.x / planeScale.y);
        
        overlay.style.position = 'absolute';
        overlay.style.top = '50%';
        overlay.style.left = '50%';
        overlay.style.transform = 'translate(-50%, -50%)';
        overlay.style.width = `${imageWidth}px`;
        overlay.style.height = `${imageHeight}px`;
        overlay.style.border = '3px solid #3B82F6';
        overlay.style.borderRadius = '8px';
        overlay.style.pointerEvents = 'none';
        overlay.style.zIndex = '1000';
        overlay.style.transition = 'opacity 0.2s ease';
        
        containerRef.current.parentElement.style.position = 'relative';
        containerRef.current.parentElement.appendChild(overlay);
        
        // Remove overlay after 800ms
        setTimeout(() => {
          overlay.style.opacity = '0';
          setTimeout(() => {
            overlay.remove();
          }, 200);
        }, 800);
      }
    }
    
    if (onImageClick) {
      onImageClick(imageData);
    }
    
    // Restore scroll position after a brief delay to prevent reset
    if (currentScrollTarget !== undefined && appRef.current?.scroll) {
      setTimeout(() => {
        if (appRef.current?.scroll) {
          appRef.current.scroll.target = currentScrollTarget;
        }
      }, 100);
    }
  };

  // Scroll the gallery wheel
  const scrollGallery = (direction) => {
    if (appRef.current && appRef.current.scroll) {
      const scrollAmount = 4.4; // Small scroll amount - adjust as needed
      if (direction === 'down' || direction === 'next') {
        appRef.current.scroll.target += scrollAmount;
      } else if (direction === 'up' || direction === 'previous') {
        appRef.current.scroll.target -= scrollAmount;
      }
      
      // Note: The gallery has snap-to-grid behavior (onCheck() debounced 200ms)
      // Wait >200ms between scrolls to prevent position reset
    }
  };

  useEffect(() => {
    const app = new App(containerRef.current, { items, bend, textColor, borderRadius, font, scrollSpeed, scrollEase, onImageClick });
    appRef.current = app;
    return () => {
      app.destroy();
    };
  }, [items, bend, textColor, borderRadius, font, scrollSpeed, scrollEase, onImageClick]);

  return (
    <>
      <div className="circular-gallery" ref={containerRef} />
      {/* Hidden buttons for voice navigation with data-nav-id */}
      {/* These are completely removed from layout flow but accessible to the action executor */}
      <div style={{ 
        position: 'fixed',
        top: '-10000px',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden',
        opacity: 0,
        pointerEvents: 'none',
        zIndex: -1
      }}>
        {/* Scroll control buttons */}
        <button
          data-nav-id="gallery-scroll-next"
          onClick={() => scrollGallery('next')}
          aria-label="Scroll gallery to next image"
          tabIndex={-1}
        >
          Next Image
        </button>
        <button
          data-nav-id="gallery-scroll-previous"
          onClick={() => scrollGallery('previous')}
          aria-label="Scroll gallery to previous image"
          tabIndex={-1}
        >
          Previous Image
        </button>
        
        {/* Image selection buttons */}
        {galleryItems.map((item, index) => (
          <button
            key={index}
            data-nav-id={`gallery-${toKebabCase(item.text)}`}
            onClick={() => handleImageNavigation(item)}
            aria-label={`Select ${item.text}`}
            tabIndex={-1}
          >
            {item.text}
          </button>
        ))}
      </div>
    </>
  );
}

