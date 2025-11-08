<template>
  <div data-component-id="root-container" data-nav-id="root-container" class="page-container">
  <div data-component-id="sticky-header" data-nav-id="sticky-header" style="position: sticky; top: 0; left: 0; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid #333; box-sizing: border-box">
  <h3 data-component-id="header-logo" data-nav-id="header-logo" content="iPhone 17 Pro" style="font-weight: 700">iPhone 17 Pro</h3>
  <div data-component-id="header-links" data-nav-id="header-links" style="display: flex">
  <a data-component-id="nav-link-home" data-nav-id="nav-link-home" href="#/" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-home" data-nav-id="nav-text-home">Home</p>
  </a>
  <a data-component-id="nav-link-features" data-nav-id="nav-link-features" href="#/features" style="color: #fff; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
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
  <div data-component-id="features-content" data-nav-id="features-content" class="content-width">
  <h1 data-component-id="feat-title" data-nav-id="feat-title" content="Pro Features" style="font-size: 60px; text-align: center; margin: 3rem 0">Pro Features</h1>
  <ul data-component-id="feat-list-container" data-nav-id="feat-list-container" class="features-list" style="list-style: none; padding: 0">
  <li data-component-id="feat-item-1" data-nav-id="feat-item-1" style="display: flex; align-items: center; font-size: 20px; margin-bottom: 1rem">
  <svg data-component-id="feat-icon-1" data-nav-id="feat-icon-1" class="icon-check" viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em">
    <path d="M20 6L9 17l-5-5"></path>
  </svg>
  <p data-component-id="feat-text-1" data-nav-id="feat-text-1">Dynamic Island</p>
  </li>
  <li data-component-id="feat-item-2" data-nav-id="feat-item-2" style="display: flex; align-items: center; font-size: 20px; margin-bottom: 1rem">
  <svg data-component-id="feat-icon-2" data-nav-id="feat-icon-2" class="icon-check" viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em">
    <path d="M20 6L9 17l-5-5"></path>
  </svg>
  <p data-component-id="feat-text-2" data-nav-id="feat-text-2">ProMotion Display (1-120Hz)</p>
  </li>
  <li data-component-id="feat-item-3" data-nav-id="feat-item-3" style="display: flex; align-items: center; font-size: 20px; margin-bottom: 1rem">
  <svg data-component-id="feat-icon-3" data-nav-id="feat-icon-3" class="icon-check" viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em">
    <path d="M20 6L9 17l-5-5"></path>
  </svg>
  <p data-component-id="feat-text-3" data-nav-id="feat-text-3">48MP Main Camera with 10x Optical Zoom</p>
  </li>
  </ul>
  </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Add component-specific styles here */
</style>

