import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.mount('#app')


const resolveParentOrigin = () => {
  if (typeof import.meta !== 'undefined' && import.meta?.env?.VITE_PARENT_ORIGIN) {
    return import.meta.env.VITE_PARENT_ORIGIN
  }
  
  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.protocol}//${window.location.hostname}:5173`
  }
  
  return 'http://localhost:5173'
}

const PARENT_ORIGIN = resolveParentOrigin()

const captureDOMSnapshot = () => {
  const elements = document.querySelectorAll('[data-nav-id]')
  const snapshot = []

  elements.forEach((element) => {
    const navId = element.getAttribute('data-nav-id')
    const tagName = element.tagName.toLowerCase()
    const text = element.textContent?.trim().substring(0, 100) || ''
    const isVisible = isElementVisible(element)
    
    const rect = element.getBoundingClientRect()
    const position = {
      top: Math.round(rect.top),
      left: Math.round(rect.left),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      isInViewport: rect.top >= 0 && rect.top <= window.innerHeight
    }

    snapshot.push({
      navId,
      tagName,
      text,
      isVisible,
      position,
      href: element.href || null,
      type: element.type || null,
      role: element.getAttribute('role') || null
    })
  })

  return {
    elements: snapshot,
    currentUrl: window.location.pathname,
    viewportHeight: window.innerHeight,
    scrollY: window.scrollY,
    totalHeight: document.documentElement.scrollHeight,
    source: 'iframe-content'
  }
}

const isElementVisible = (element) => {
  const style = window.getComputedStyle(element)
  return (
    style.display !== 'none' &&
    style.visibility !== 'hidden' &&
    style.opacity !== '0'
  )
}

window.addEventListener('message', (event) => {
  if (event.origin !== PARENT_ORIGIN) {
    console.warn('[Iframe] Ignoring message from unexpected origin:', event.origin, 'expected:', PARENT_ORIGIN)
    return
  }

  if (event.data?.type === 'DOM_SNAPSHOT_REQUEST') {
    console.log('[Iframe] Received DOM snapshot request from parent')
    
    const snapshot = captureDOMSnapshot()
    console.log('[Iframe] Captured', snapshot.elements.length, 'elements with data-nav-id')
    
    window.parent.postMessage(
      {
        type: 'DOM_SNAPSHOT_RESPONSE',
        snapshot: snapshot
      },
      PARENT_ORIGIN
    )
    
    console.log('[Iframe] Sent DOM snapshot response to parent')
  }
})

console.log('[Iframe] DOM snapshot listener initialized, listening for requests from:', PARENT_ORIGIN)

