/**
 * Captures DOM from cross-origin iframe via postMessage
 */

import { captureDOMSnapshot } from './domSnapshot.js'

const IFRAME_SELECTOR = '#dynamic-content-iframe'
const IFRAME_TIMEOUT = 5000 // 5 seconds
const IFRAME_ORIGIN = 'http://localhost:3001'

/**
 * Request DOM snapshot from iframe using postMessage
 */
export const captureIframeDOMSnapshot = () => {
  return new Promise((resolve, reject) => {
    const iframe = document.querySelector(IFRAME_SELECTOR)
    
    if (!iframe) {
      console.log('[Main] iframe not found, returning empty snapshot')
      return resolve({ elements: [], source: 'iframe-not-found' })
    }

    // Set up response listener
    const timeout = setTimeout(() => {
      cleanup()
      reject(new Error('iframe snapshot timeout'))
    }, IFRAME_TIMEOUT)

    const messageHandler = (event) => {
      // Verify origin (security)
      if (event.origin !== IFRAME_ORIGIN) {
        console.warn('[Main] Ignoring message from wrong origin:', event.origin)
        return
      }
      
      if (event.data.type === 'DOM_SNAPSHOT_RESPONSE') {
        console.log('[Main] Received iframe DOM snapshot:', event.data.snapshot)
        cleanup()
        resolve(event.data.snapshot)
      }
    }

    const cleanup = () => {
      clearTimeout(timeout)
      window.removeEventListener('message', messageHandler)
    }

    window.addEventListener('message', messageHandler)

    // Request snapshot from iframe
    console.log('[Main] Requesting DOM snapshot from iframe...')
    iframe.contentWindow.postMessage({
      type: 'DOM_SNAPSHOT_REQUEST'
    }, IFRAME_ORIGIN)
  })
}

/**
 * Combine main app DOM + iframe DOM
 */
export const captureCombinedDOMSnapshot = async () => {
  // Capture main app DOM
  const mainSnapshot = captureDOMSnapshot()
  console.log('[Main] Captured main app DOM:', mainSnapshot.elements.length, 'elements')
  
  // Capture iframe DOM (async)
  let iframeSnapshot
  try {
    iframeSnapshot = await captureIframeDOMSnapshot()
    console.log('[Main] Captured iframe DOM:', iframeSnapshot.elements?.length || 0, 'elements')
    
    // DEBUG: Print all iframe nav-ids
    const iframeNavIds = (iframeSnapshot.elements || []).map(el => el.navId)
    console.log('[Main] 🔍 iframe nav-ids captured:', iframeNavIds)
    
    // DEBUG: Print dynamic button nav-ids specifically
    const buttonIds = iframeNavIds.filter(id => id && id.startsWith('external-btn-'))
    console.log('[Main] 🎯 Dynamic button IDs found:', buttonIds)
  } catch (error) {
    console.warn('[Main] Failed to capture iframe DOM:', error)
    iframeSnapshot = { elements: [] }
  }

  // Merge snapshots with context tags
  const combinedElements = [
    ...mainSnapshot.elements.map(el => ({ ...el, context: 'main-app' })),
    ...(iframeSnapshot.elements || []).map(el => ({ ...el, context: 'iframe' }))
  ]

  console.log('[Main] Combined snapshot:', {
    total: combinedElements.length,
    mainApp: mainSnapshot.elements.length,
    iframe: iframeSnapshot.elements?.length || 0
  })

  return {
    ...mainSnapshot,
    elements: combinedElements,
    iframeElementCount: iframeSnapshot.elements?.length || 0,
    totalElementCount: combinedElements.length
  }
}

