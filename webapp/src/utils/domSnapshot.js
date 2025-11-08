/**
 * Captures all interactive elements with data-nav-id attributes
 * This creates a "navigation map" for the LLM agent
 */
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

