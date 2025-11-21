<template>
  <div data-component-id="root-container" data-nav-id="root-container" class="page-container">
  <div data-component-id="root-container.sticky-header" data-nav-id="root-container.sticky-header" style="position: sticky; top: 0; left: 0; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 1000; border-bottom: 1px solid #333; box-sizing: border-box">
  <h3 data-component-id="root-container.sticky-header.header-logo" data-nav-id="root-container.sticky-header.header-logo" content="iPhone 17 Pro" style="font-weight: 700">iPhone 17 Pro</h3>
  <div data-component-id="root-container.sticky-header.header-links" data-nav-id="root-container.sticky-header.header-links" style="display: flex">
  <a data-component-id="root-container.sticky-header.header-links.nav-link-home" data-nav-id="root-container.sticky-header.header-links.nav-link-home" href="#/" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-home.nav-text-home" data-nav-id="root-container.sticky-header.header-links.nav-link-home.nav-text-home">Home</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-features" data-nav-id="root-container.sticky-header.header-links.nav-link-features" href="#/features" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-features.nav-text-features" data-nav-id="root-container.sticky-header.header-links.nav-link-features.nav-text-features">Features</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-compare" data-nav-id="root-container.sticky-header.header-links.nav-link-compare" href="#/compare" style="color: #888; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-compare.nav-text-compare" data-nav-id="root-container.sticky-header.header-links.nav-link-compare.nav-text-compare">Compare</p>
  </a>
  <a data-component-id="root-container.sticky-header.header-links.nav-link-pricing" data-nav-id="root-container.sticky-header.header-links.nav-link-pricing" href="#/pricing" style="color: #fff; text-decoration: none; font-weight: 500; padding: 0 1rem; font-size: 14px">
  <p data-component-id="root-container.sticky-header.header-links.nav-link-pricing.nav-text-pricing" data-nav-id="root-container.sticky-header.header-links.nav-link-pricing.nav-text-pricing">Pricing</p>
  </a>
  </div>
  <button data-component-id="root-container.sticky-header.header-buy-btn" data-nav-id="root-container.sticky-header.header-buy-btn" class="btn-primary" style="padding: 5px 15px; font-size: 14px">Buy</button>
  </div>
  <div data-component-id="root-container.pricing-content" data-nav-id="root-container.pricing-content" class="content-width">
  <h1 data-component-id="root-container.pricing-content.pricing-title" data-nav-id="root-container.pricing-content.pricing-title" content="Choose Your iPhone" style="font-size: 60px; text-align: center; margin: 3rem 0">Choose Your iPhone</h1>
  <div data-component-id="root-container.pricing-content.toggle-box" data-nav-id="root-container.pricing-content.toggle-box" style="text-align: center; margin-bottom: 2rem">
  <button data-component-id="root-container.pricing-content.toggle-box.toggle-btn-full" data-nav-id="root-container.pricing-content.toggle-box.toggle-btn-full" @click=onroot_container_pricing_content_toggle_box_toggle_btn_full_click>Pay Full</button>
  <button data-component-id="root-container.pricing-content.toggle-box.toggle-btn-monthly" data-nav-id="root-container.pricing-content.toggle-box.toggle-btn-monthly" style="margin-left: 1rem" @click=onroot_container_pricing_content_toggle_box_toggle_btn_monthly_click>Pay Monthly</button>
  </div>
  <div data-component-id="root-container.pricing-content.pricing-cards" data-nav-id="root-container.pricing-content.pricing-cards" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem">
  <div data-component-id="root-container.pricing-content.pricing-cards.card-pro" data-nav-id="root-container.pricing-content.pricing-cards.card-pro" style="border: 1px solid #333; border-radius: 12px; padding: 2rem">
  <h3 data-component-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-title" data-nav-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-title" content="iPhone 17 Pro" style="font-size: 24px">iPhone 17 Pro</h3>
  <p data-component-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-price-full" data-nav-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-price-full" v-if="pricingMode === 'full'" style="font-size: 32px; margin: 1rem 0">From $1199</p>
  <p data-component-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-price-monthly" data-nav-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-price-monthly" v-if="pricingMode === 'monthly'" style="font-size: 32px; margin: 1rem 0">From $49.95/mo</p>
  <button data-component-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-btn" data-nav-id="root-container.pricing-content.pricing-cards.card-pro.card-pro-btn" class="btn-primary">Buy</button>
  </div>
  <div data-component-id="root-container.pricing-content.pricing-cards.card-max" data-nav-id="root-container.pricing-content.pricing-cards.card-max" style="border: 1px solid #333; border-radius: 12px; padding: 2rem">
  <h3 data-component-id="root-container.pricing-content.pricing-cards.card-max.card-max-title" data-nav-id="root-container.pricing-content.pricing-cards.card-max.card-max-title" content="iPhone 17 Pro Max" style="font-size: 24px">iPhone 17 Pro Max</h3>
  <p data-component-id="root-container.pricing-content.pricing-cards.card-max.card-max-price-full" data-nav-id="root-container.pricing-content.pricing-cards.card-max.card-max-price-full" v-if="pricingMode === 'full'" style="font-size: 32px; margin: 1rem 0">From $1299</p>
  <p data-component-id="root-container.pricing-content.pricing-cards.card-max.card-max-price-monthly" data-nav-id="root-container.pricing-content.pricing-cards.card-max.card-max-price-monthly" v-if="pricingMode === 'monthly'" style="font-size: 32px; margin: 1rem 0">From $54.12/mo</p>
  <button data-component-id="root-container.pricing-content.pricing-cards.card-max.card-max-btn" data-nav-id="root-container.pricing-content.pricing-cards.card-max.card-max-btn" class="btn-primary">Buy</button>
  </div>
  </div>
  </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const pricingMode = ref("full")

function onroot_container_pricing_content_toggle_box_toggle_btn_full_click() {

  pricingMode.value = "full";
}

function onroot_container_pricing_content_toggle_box_toggle_btn_monthly_click() {

  pricingMode.value = "monthly";
}
</script>

<style scoped>
/* Add component-specific styles here */
</style>