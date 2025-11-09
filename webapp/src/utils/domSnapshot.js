/**
 * Captures all interactive elements with data-nav-id attributes
 * This creates a "navigation map" for the LLM agent
 */
const IFRAME_SELECTORS = [
  '.inspection-modal__iframe', // Priority: modal iframe when editing
  '.template-selection__iframe', // Fallback: template grid iframes
  '#dynamic-content-iframe' // Legacy: original selector
]
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
    element.style.boxShadow = `0 0 0 3px #EF5D2A`
    element.style.borderRadius = borderRadius // Ensure border-radius is preserved
    element.style.outline = 'none'
  } else {
    element.style.outline = '3px solid #EF5D2A'
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
    // Try to find the first visible iframe using priority selectors
    let iframe = null
    let matchedSelector = null
    let iframeContext = {}
    
    for (const selector of IFRAME_SELECTORS) {
      const found = document.querySelector(selector)
      if (found && found.contentWindow) {
        iframe = found
        matchedSelector = selector
        console.log(`[DOM Snapshot] Found iframe using selector: ${selector}`)
        break
      }
    }

    // If no prioritized iframe found, try to find any iframe that's visible
    if (!iframe) {
      const allIframes = document.querySelectorAll('iframe')
      for (const candidateIframe of allIframes) {
        if (candidateIframe.contentWindow && isElementVisible(candidateIframe)) {
          iframe = candidateIframe
          matchedSelector = 'fallback-visible-iframe'
          console.log('[DOM Snapshot] Found visible iframe as fallback')
          break
        }
      }
    }

    if (!iframe || !iframe.contentWindow) {
      console.log('[DOM Snapshot] No iframe found, returning empty snapshot')
      resolve({ elements: [], source: 'iframe-not-found' })
      return
    }

    // Extract context about which iframe this is
    iframeContext = {
      selector: matchedSelector,
      title: iframe.title || null,
      src: iframe.src || null,
    }

    // Check if this is the inspection modal (editing mode)
    const isInModal = matchedSelector === '.inspection-modal__iframe'
    if (isInModal) {
      // Try to find which template option is being inspected from iframe title
      // Title format: "Editing Design Option A" or "Inspecting Design Option A"
      const templateMatch = iframe.title?.match(/Option ([A-D])/i)
      const editModeMatch = iframe.title?.match(/Editing/i)
      
      iframeContext.mode = editModeMatch ? 'editing' : 'inspecting'
      iframeContext.templateId = templateMatch?.[1] || null
      iframeContext.editMode = !!editModeMatch
      
      // Also check for the footer as a backup way to detect edit mode
      const modal = iframe.closest('.inspection-modal')
      const hasFooter = modal?.querySelector('.inspection-modal__footer')
      if (!iframeContext.editMode && !hasFooter) {
        iframeContext.editMode = true
        iframeContext.mode = 'editing'
      }
      
      console.log(`[DOM Snapshot] Capturing from Template ${iframeContext.templateId || '?'} - ${iframeContext.editMode ? 'EDIT MODE' : 'INSPECTION MODE'}`)
    } else if (matchedSelector === '.template-selection__iframe') {
      iframeContext.mode = 'grid-view'
      // Try to identify which grid item this is by finding parent option div
      const optionDiv = iframe.closest('[data-nav-id^="template-option-"]')
      if (optionDiv) {
        const navId = optionDiv.getAttribute('data-nav-id')
        const templateMatch = navId?.match(/template-option-([a-d])/i)
        iframeContext.templateId = templateMatch?.[1]?.toUpperCase() || null
      }
    } else {
      iframeContext.mode = 'grid-view'
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
        // Add iframe context metadata to the snapshot
        const snapshotWithContext = {
          ...event.data.snapshot,
          iframeContext
        }
        resolve(snapshotWithContext)
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
  console.log('[DOM Snapshot] Captured main app:', mainSnapshot.elements.length, 'elements')

  let iframeSnapshot = { elements: [] }
  try {
    iframeSnapshot = await captureIframeDOMSnapshot()
    console.log('[DOM Snapshot] Captured iframe:', iframeSnapshot.elements?.length || 0, 'elements')
    
    // Log which iframe was captured
    if (iframeSnapshot.iframeContext) {
      const ctx = iframeSnapshot.iframeContext
      console.log('[DOM Snapshot] Active iframe:', {
        mode: ctx.mode,
        templateId: ctx.templateId || 'unknown',
        editMode: ctx.editMode,
        selector: ctx.selector
      })
    }
  } catch (error) {
    console.warn('[DOM Snapshot] Failed to capture iframe DOM:', error)
  }

  const combinedElements = [
    ...mainSnapshot.elements.map((element) => ({ ...element, context: 'main-app' })),
    ...(iframeSnapshot.elements || []).map((element) => ({ ...element, context: 'iframe' }))
  ]

  console.log('[DOM Snapshot] Combined snapshot:', {
    mainApp: mainSnapshot.elements.length,
    iframe: iframeSnapshot.elements?.length || 0,
    total: combinedElements.length
  })

  return {
    ...mainSnapshot,
    elements: combinedElements,
    iframeElementCount: iframeSnapshot.elements?.length || 0,
    totalElementCount: combinedElements.length,
    // Include iframe context so consumers know which iframe was captured
    activeIframe: iframeSnapshot.iframeContext || null
  }
}

