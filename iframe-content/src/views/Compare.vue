<template>
  <div data-component-id="root-container" data-nav-id="root-container" class="page-container">
  <div data-component-id="sticky-header" data-nav-id="sticky-header" style="position: sticky; top: 0; left: 0; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid #333; box-sizing: border-box">
  <h3 data-component-id="header-logo" data-nav-id="header-logo" content="iPhone 17 Pro" style="font-weight: 700">iPhone 17 Pro</h3>
  <div data-component-id="header-links" data-nav-id="header-links" style="display: flex">
  <a data-component-id="nav-link-home" data-nav-id="nav-link-home" href="#/" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-home" data-nav-id="nav-text-home">Home</p>
  </a>
  <a data-component-id="nav-link-features" data-nav-id="nav-link-features" href="#/features" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-features" data-nav-id="nav-text-features">Features</p>
  </a>
  <a data-component-id="nav-link-compare" data-nav-id="nav-link-compare" href="#/compare" style="color: #fff; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-compare" data-nav-id="nav-text-compare">Compare</p>
  </a>
  <a data-component-id="nav-link-pricing" data-nav-id="nav-link-pricing" href="#/pricing" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="nav-text-pricing" data-nav-id="nav-text-pricing">Pricing</p>
  </a>
  </div>
  <button data-component-id="header-buy-btn" data-nav-id="header-buy-btn" class="btn-primary" style="padding: 5px 15px; font-size: 14px">Buy</button>
  </div>
  <div data-component-id="compare-content" data-nav-id="compare-content" class="content-width">
  <h1 data-component-id="compare-title" data-nav-id="compare-title" content="Compare Models" style="font-size: 60px; text-align: center; margin: 3rem 0">Compare Models</h1>
  <table data-component-id="compare-table" data-nav-id="compare-table" style="width: 100%; font-size: 18px; border-collapse: collapse; text-align: left" class="compare-table">
    <thead>
      <tr><th>Feature</th><th>iPhone 17 Pro</th><th>iPhone 16 Pro</th></tr>
    </thead>
    <tbody>
    <tr><td>Chip</td><td>A20 Bionic</td><td>A19 Pro</td></tr>
    <tr><td>Display</td><td>ProMotion 1-120Hz</td><td>ProMotion 10-120Hz</td></tr>
    <tr><td>Camera</td><td>48MP Main, 10x Optical Zoom</td><td>48MP Main, 5x Optical Zoom</td></tr>
    <tr><td>Material</td><td>Titanium Grade 6</td><td>Titanium Grade 5</td></tr>
    </tbody>
  </table>
  </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Add component-specific styles here */
</style>

