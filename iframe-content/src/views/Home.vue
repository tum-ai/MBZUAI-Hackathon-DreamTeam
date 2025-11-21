<template>
  <div data-component-id="root-container" data-nav-id="root-container" class="page-container">
  <div data-component-id="root-container.sticky-header" data-nav-id="root-container.sticky-header" style="position: sticky; top: 0; left: 0; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid #333; box-sizing: border-box">
  <h3 data-component-id="root-container.sticky-header.header-logo" data-nav-id="root-container.sticky-header.header-logo" content="iPhone 17 Pro" style="font-weight: 700">iPhone 17 Pro</h3>
  <div data-component-id="root-container.sticky-header.header-links" data-nav-id="root-container.sticky-header.header-links" style="display: flex">
  <a data-component-id="root-container.sticky-header.header-links.nav-link-home" data-nav-id="root-container.sticky-header.header-links.nav-link-home" href="#/" style="color: #fff; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-home.nav-text-home" data-nav-id="root-container.sticky-header.header-links.nav-link-home.nav-text-home">Home</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-features" data-nav-id="root-container.sticky-header.header-links.nav-link-features" href="#/features" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-features.nav-text-features" data-nav-id="root-container.sticky-header.header-links.nav-link-features.nav-text-features">Features</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-compare" data-nav-id="root-container.sticky-header.header-links.nav-link-compare" href="#/compare" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-compare.nav-text-compare" data-nav-id="root-container.sticky-header.header-links.nav-link-compare.nav-text-compare">Compare</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-pricing" data-nav-id="root-container.sticky-header.header-links.nav-link-pricing" href="#/pricing" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-pricing.nav-text-pricing" data-nav-id="root-container.sticky-header.header-links.nav-link-pricing.nav-text-pricing">Pricing</p>
  </a>
  </div>
  <button data-component-id="root-container.sticky-header.header-buy-btn" data-nav-id="root-container.sticky-header.header-buy-btn" class="btn-primary" style="padding: 5px 15px; font-size: 14px">Buy</button>
  </div>
  <div data-component-id="root-container.hero-section" data-nav-id="root-container.hero-section" id="hero-section" style="height: 100vh; width: 100%; position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow: hidden">
  <img data-component-id="root-container.hero-section.hero-img" data-nav-id="root-container.hero-section.hero-img" src="https://picsum.photos/1920/1080?random=1" alt="iPhone Hero" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="root-container.hero-section.hero-gradient" data-nav-id="root-container.hero-section.hero-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="root-container.hero-section.hero-text-box" data-nav-id="root-container.hero-section.hero-text-box" style="position: relative; z-index: 3">
  <h1 data-component-id="root-container.hero-section.hero-text-box.hero-title" data-nav-id="root-container.hero-section.hero-text-box.hero-title" content="iPhone 17 Pro" style="font-size: 80px">iPhone 17 Pro</h1>
  <p data-component-id="root-container.hero-section.hero-text-box.hero-subtitle" data-nav-id="root-container.hero-section.hero-text-box.hero-subtitle" style="font-size: 32px; color: #ccc">The Future. Now.</p>
  </div>
  </div>
  <div data-component-id="root-container.chip-section" data-nav-id="root-container.chip-section" id="chip-section" style="height: 100vh; width: 100%; position: relative; display: flex; justify-content: center; align-items: center; overflow: hidden">
  <img data-component-id="root-container.chip-section.chip-img" data-nav-id="root-container.chip-section.chip-img" src="https://picsum.photos/1920/1080?random=2" alt="A20 Bionic" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="root-container.chip-section.chip-gradient" data-nav-id="root-container.chip-section.chip-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="root-container.chip-section.chip-text" data-nav-id="root-container.chip-section.chip-text" style="position: relative; z-index: 3; text-align: center">
  <h2 data-component-id="root-container.chip-section.chip-text.chip-title" data-nav-id="root-container.chip-section.chip-text.chip-title" content="A20 Bionic" style="font-size: 60px">A20 Bionic</h2>
  <p data-component-id="root-container.chip-section.chip-text.chip-subtitle" data-nav-id="root-container.chip-section.chip-text.chip-subtitle" style="font-size: 24px; color: #ccc">The most powerful chip ever in an iPhone.</p>
  </div>
  </div>
  <div data-component-id="root-container.camera-section" data-nav-id="root-container.camera-section" id="camera-section" style="height: 100vh; width: 100%; position: relative; display: flex; justify-content: center; align-items: center; overflow: hidden">
  <img data-component-id="root-container.camera-section.camera-img" data-nav-id="root-container.camera-section.camera-img" src="https://picsum.photos/1920/1080?random=3" alt="Pro Camera" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1" />
  <div data-component-id="root-container.camera-section.camera-gradient" data-nav-id="root-container.camera-section.camera-gradient" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; z-index: 2; background: linear-gradient(to top, #000 20%, transparent)">
  </div>
  <div data-component-id="root-container.camera-section.camera-text" data-nav-id="root-container.camera-section.camera-text" style="position: relative; z-index: 3; text-align: center">
  <h2 data-component-id="root-container.camera-section.camera-text.camera-title" data-nav-id="root-container.camera-section.camera-text.camera-title" content="Pro Camera System" style="font-size: 60px">Pro Camera System</h2>
  <p data-component-id="root-container.camera-section.camera-text.camera-subtitle" data-nav-id="root-container.camera-section.camera-text.camera-subtitle" style="font-size: 24px; color: #ccc">Capture your world like never before.</p>
  </div>
  </div>
  <div data-component-id="root-container.footer" data-nav-id="root-container.footer" style="text-align: center; padding: 3rem; margin-top: 3rem; border-top: 1px solid #333">
  <p data-component-id="root-container.footer.footer-text" data-nav-id="root-container.footer.footer-text" style="font-size: 14px; color: #888">Copyright © 2025 GenAI Inc. All rights reserved.</p>
  </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Add component-specific styles here */
</style>