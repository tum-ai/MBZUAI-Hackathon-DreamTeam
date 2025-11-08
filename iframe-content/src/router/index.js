import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Features from '../views/Features.vue'
import Compare from '../views/Compare.vue'
import Pricing from '../views/Pricing.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/features',
    name: 'Features',
    component: Features
  },
  {
    path: '/compare',
    name: 'Compare',
    component: Compare
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: Pricing
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

