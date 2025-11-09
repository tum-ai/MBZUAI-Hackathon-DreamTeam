/**
 * Routes actions to main app or iframe based on element context
 */

import { executeAction as executeMainAction } from './actionExecutor.js'

const IFRAME_SELECTORS = [
  '.inspection-modal__iframe',
  '.template-selection__iframe',
  '#dynamic-content-iframe'
]
const IFRAME_TIMEOUT = 5000

const resolveIframeOrigin = () => {
  try {
    if (typeof import.meta !== 'undefined' && import.meta?.env?.VITE_IFRAME_ORIGIN) {
      return import.meta.env.VITE_IFRAME_ORIGIN.replace(/\/$/, '')
    }
  } catch (error) {
    console.warn('[Router] Failed to read VITE_IFRAME_ORIGIN:', error)
  }

  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.protocol}//${window.location.hostname}:5174`
  }

  return 'http://localhost:5174'
}

const IFRAME_ORIGIN = resolveIframeOrigin()

/**
 * Determine if action targets iframe element
 */
const isIframeAction = (action, domSnapshot) => {
  if (!action || !action.targetId) {
    return false
  }

  // Check if targetId starts with "external-" prefix
  if (action.targetId.startsWith('external-')) {
    console.log('[Router] Action targets iframe (prefix match):', action.targetId)
    return true
  }

  // Check if element exists in iframe elements in snapshot
  const element = domSnapshot.elements.find(el => 
    el.navId === action.targetId && el.context === 'iframe'
  )
  
  if (element) {
    console.log('[Router] Action targets iframe (snapshot match):', action.targetId)
    return true
  }

  console.log('[Router] Action targets main app:', action.targetId)
  return false
}

const isIframeVisible = (element) => {
  if (!element) return false
  const style = window.getComputedStyle(element)
  return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
}

const findActiveIframe = () => {
  for (const selector of IFRAME_SELECTORS) {
    const iframe = document.querySelector(selector)
    if (iframe?.contentWindow) {
      return { iframe, selector }
    }
  }

  const allIframes = document.querySelectorAll('iframe')
  for (const candidate of allIframes) {
    if (candidate?.contentWindow && isIframeVisible(candidate)) {
      return { iframe: candidate, selector: 'fallback-visible-iframe' }
    }
  }

  return { iframe: null, selector: null }
}

/**
 * Execute action in iframe via postMessage
 */
const executeIframeAction = (action) => {
  return new Promise((resolve, reject) => {
    const { iframe, selector } = findActiveIframe()

    if (!iframe) {
      console.warn('[Router] No active iframe found when routing action:', action)
      return reject(new Error('iframe not found'))
    }

    const timeout = setTimeout(() => {
      cleanup()
      reject(new Error('iframe action timeout'))
    }, IFRAME_TIMEOUT)

    const messageHandler = (event) => {
      if (event.origin !== IFRAME_ORIGIN) {
        return
      }
      
      if (event.data.type === 'ACTION_RESULT') {
        console.log('[Router] Received action result from iframe:', event.data.result)
        cleanup()
        resolve(event.data.result)
      }
    }

    const cleanup = () => {
      clearTimeout(timeout)
      window.removeEventListener('message', messageHandler)
    }

    window.addEventListener('message', messageHandler)

    // Send action to iframe
    console.log('[Router] Sending action to iframe:', {
      action,
      selector,
      origin: IFRAME_ORIGIN
    })

    try {
      iframe.contentWindow.postMessage(
        {
          type: 'EXECUTE_ACTION',
          action
        },
        IFRAME_ORIGIN
      )
    } catch (error) {
      cleanup()
      reject(error)
    }
  })
}

/**
 * Main routing function
 */
export const routeAndExecuteAction = async (action, domSnapshot) => {
  // Handle action sequences
  if (Array.isArray(action)) {
    console.log('[Router] Executing action sequence:', action.length, 'actions')
    const results = []
    
    for (const singleAction of action) {
      const result = await routeAndExecuteAction(singleAction, domSnapshot)
      results.push({ action: singleAction, result })
      
      // If any action fails, stop the sequence
      if (!result.success) {
        console.warn('[Router] Action failed, stopping sequence')
        break
      }
    }
    
    return {
      success: results.every(r => r.result.success),
      message: `Executed ${results.length} actions`,
      isSequence: true,
      actions: results
    }
  }

  // Single action routing
  if (isIframeAction(action, domSnapshot)) {
    console.log('[Router] → Routing to iframe:', action)
    try {
      const result = await executeIframeAction(action)
      return { ...result, routedTo: 'iframe' }
    } catch (error) {
      console.error('[Router] iframe action failed:', error)
      return {
        success: false,
        message: `iframe action failed: ${error.message}`,
        routedTo: 'iframe'
      }
    }
  } else {
    console.log('[Router] → Routing to main app:', action)
    const result = await executeMainAction(action)
    return { ...result, routedTo: 'main-app' }
  }
}

