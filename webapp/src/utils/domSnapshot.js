/**
 * Captures all interactive elements with data-nav-id attributes
 * This creates a "navigation map" for the LLM agent
 */
const IFRAME_SELECTOR = '#dynamic-content-iframe'
const IFRAME_TIMEOUT = 5000

const resolveIframeOrigin = () => {
  if (typeof import.meta !== 'undefined' && import.meta?.env?.VITE_IFRAME_ORIGIN) {
    return import.meta.env.VITE_IFRAME_ORIGIN
  }

  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.protocol}//${window.location.hostname}:5174`
  }

  return 'http://localhost:5174'
}

const IFRAME_ORIGIN = resolveIframeOrigin()

export const captureDOMSnapshot = () => {
  const elements = document.querySelectorAll('[data-nav-id]')
  const snapshot = []

  elements.forEach((element) => {
    const navId = element.getAttribute('data-nav-id')
    const tagName = element.tagName.toLowerCase()
    const text = element.textContent?.trim().substring(0, 100) || ''
    const isVisible = isElementVisible(element)
    
    // Get element position for spatial reasoning
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
    totalHeight: document.documentElement.scrollHeight
  }
}

/**
 * Checks if an element is actually visible on the page
 */
const isElementVisible = (element) => {
  const style = window.getComputedStyle(element)
  return (
    style.display !== 'none' &&
    style.visibility !== 'hidden' &&
    style.opacity !== '0'
  )
}

/**
 * Find an element by its data-nav-id
 */
export const findElementByNavId = (navId) => {
  return document.querySelector(`[data-nav-id="${navId}"]`)
}

/**
 * Highlight an element temporarily (visual feedback)
 */
export const highlightElement = (element, duration = 1000) => {
  if (!element) return

  const originalOutline = element.style.outline
  const originalOutlineOffset = element.style.outlineOffset
  const originalTransition = element.style.transition
  const originalBoxShadow = element.style.boxShadow
  const originalBorderRadius = element.style.borderRadius
  
  // Get the computed border-radius to match rounded corners
  const computedStyle = window.getComputedStyle(element)
  const borderRadius = computedStyle.borderRadius
  
  element.style.transition = 'all 0.2s ease'
  
  // If the element has border-radius, use box-shadow with matching border-radius
  if (borderRadius && borderRadius !== '0px') {
    element.style.boxShadow = `0 0 0 3px #3B82F6`
    element.style.borderRadius = borderRadius // Ensure border-radius is preserved
    element.style.outline = 'none'
  } else {
    element.style.outline = '3px solid #3B82F6'
    element.style.outlineOffset = '0px'
  }
  
  setTimeout(() => {
    element.style.boxShadow = originalBoxShadow
    element.style.outline = originalOutline
    element.style.outlineOffset = originalOutlineOffset
    element.style.borderRadius = originalBorderRadius
    setTimeout(() => {
      element.style.transition = originalTransition
    }, 200)
  }, duration)
}

export const captureIframeDOMSnapshot = () => {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return Promise.resolve({ elements: [], source: 'no-window' })
  }

  return new Promise((resolve, reject) => {
    const iframe = document.querySelector(IFRAME_SELECTOR)

    if (!iframe || !iframe.contentWindow) {
      console.log('[DOM Snapshot] iframe not found, returning empty snapshot')
      resolve({ elements: [], source: 'iframe-not-found' })
      return
    }

    const timeout = setTimeout(() => {
      cleanup()
      reject(new Error('iframe snapshot timeout'))
    }, IFRAME_TIMEOUT)

    const messageHandler = (event) => {
      if (event.origin !== IFRAME_ORIGIN) {
        console.warn('[DOM Snapshot] Ignoring message from unexpected origin:', event.origin)
        return
      }

      if (event.data?.type === 'DOM_SNAPSHOT_RESPONSE') {
        cleanup()
        resolve(event.data.snapshot)
      }
    }

    const cleanup = () => {
      clearTimeout(timeout)
      window.removeEventListener('message', messageHandler)
    }

    window.addEventListener('message', messageHandler)

    iframe.contentWindow.postMessage(
      {
        type: 'DOM_SNAPSHOT_REQUEST'
      },
      IFRAME_ORIGIN
    )
  })
}

export const captureCombinedDOMSnapshot = async () => {
  const mainSnapshot = captureDOMSnapshot()

  let iframeSnapshot = { elements: [] }
  try {
    iframeSnapshot = await captureIframeDOMSnapshot()
  } catch (error) {
    console.warn('[DOM Snapshot] Failed to capture iframe DOM:', error)
  }

  const combinedElements = [
    ...mainSnapshot.elements.map((element) => ({ ...element, context: 'main-app' })),
    ...(iframeSnapshot.elements || []).map((element) => ({ ...element, context: 'iframe' }))
  ]

  return {
    ...mainSnapshot,
    elements: combinedElements,
    iframeElementCount: iframeSnapshot.elements?.length || 0,
    totalElementCount: combinedElements.length
  }
}

