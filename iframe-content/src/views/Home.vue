<template>
  <div data-component-id="root-container" data-nav-id="root-container" class="page-container">
  <div data-component-id="sticky-header" data-nav-id="sticky-header" style="position: sticky; top: 0; left: 0; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid #333; box-sizing: border-box">
  <h3 data-component-id="header-logo" data-nav-id="header-logo" content="iPhone 17 Pro" style="font-weight: 700">iPhone 17 Pro</h3>
  <div data-component-id="header-links" data-nav-id="header-links" style="display: flex">
  <a data-component-id="nav-link-home" data-nav-id="nav-link-home" href="#/" style="color: #fff; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-home" data-nav-id="nav-text-home">Home</p>
  </a>
  <a data-component-id="nav-link-features" data-nav-id="nav-link-features" href="#/features" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-features" data-nav-id="nav-text-features">Features</p>
  </a>
  <a data-component-id="nav-link-compare" data-nav-id="nav-link-compare" href="#/compare" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-compare" data-nav-id="nav-text-compare">Compare</p>
  </a>
  <a data-component-id="nav-link-pricing" data-nav-id="nav-link-pricing" href="#/pricing" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-pricing" data-nav-id="nav-text-pricing">Pricing</p>
  </a>
  </div>
  <button data-component-id="header-buy-btn" data-nav-id="header-buy-btn" class="btn-primary" style="padding: 5px 15px; font-size: 14px">Buy</button>
  </div>
  <div data-component-id="hero-section" data-nav-id="hero-section" id="hero-section" style="height: 100vh; width: 100%; position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow: hidden">
  <img data-component-id="hero-img" data-nav-id="hero-img" src="https://picsum.photos/1920/1080?random=1" alt="iPhone Hero" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="hero-gradient" data-nav-id="hero-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="hero-text-box" data-nav-id="hero-text-box" style="position: relative; z-index: 3">
  <h1 data-component-id="hero-title" data-nav-id="hero-title" content="iPhone 17 Pro" style="font-size: 80px">iPhone 17 Pro</h1>
  <p data-component-id="hero-subtitle" data-nav-id="hero-subtitle" style="font-size: 32px; color: #ccc">The Future. Now.</p>
  </div>
  </div>
  <div data-component-id="chip-section" data-nav-id="chip-section" id="chip-section" style="height: 100vh; width: 100%; position: relative; display: flex; justify-content: center; align-items: center; overflow: hidden">
  <img data-component-id="chip-img" data-nav-id="chip-img" src="https://picsum.photos/1920/1080?random=2" alt="A20 Bionic" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="chip-gradient" data-nav-id="chip-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="chip-text" data-nav-id="chip-text" style="position: relative; z-index: 3; text-align: center">
  <h2 data-component-id="chip-title" data-nav-id="chip-title" content="A20 Bionic" style="font-size: 60px">A20 Bionic</h2>
  <p data-component-id="chip-subtitle" data-nav-id="chip-subtitle" style="font-size: 24px; color: #ccc">The most powerful chip ever in an iPhone.</p>
  </div>
  </div>
  <div data-component-id="camera-section" data-nav-id="camera-section" id="camera-section" style="height: 100vh; width: 100%; position: relative; display: flex; justify-content: center; align-items: center; overflow: hidden">
  <img data-component-id="camera-img" data-nav-id="camera-img" src="https://picsum.photos/1920/1080?random=3" alt="Pro Camera" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="camera-gradient" data-nav-id="camera-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="camera-text" data-nav-id="camera-text" style="position: relative; z-index: 3; text-align: center">
  <h2 data-component-id="camera-title" data-nav-id="camera-title" content="Pro Camera System" style="font-size: 60px">Pro Camera System</h2>
  <p data-component-id="camera-subtitle" data-nav-id="camera-subtitle" style="font-size: 24px; color: #ccc">Capture your world like never before.</p>
  </div>
  </div>
  <div data-component-id="footer" data-nav-id="footer" style="text-align: center; padding: 3rem; margin-top: 3rem; border-top: 1px solid #333">
  <p data-component-id="footer-text" data-nav-id="footer-text" style="font-size: 14px; color: #888">Copyright © 2025 GenAI Inc. All rights reserved.</p>
  </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Add component-specific styles here */
</style>

