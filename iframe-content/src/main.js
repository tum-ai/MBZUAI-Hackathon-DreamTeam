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
    return `${window.location.protocol}//${window.location.hostname}:5178`
  }
  
  return 'http://localhost:5178'
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

const findElementByNavId = (targetId) => {
  if (!targetId) {
    return null
  }

  return document.querySelector(`[data-nav-id="${targetId}"]`)
}

const sleep = (ms = 0) => new Promise(resolve => setTimeout(resolve, ms))

const executeNavigate = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  element.click()

  return {
    success: true,
    message: `Clicked on ${action.targetId}`,
    action
  }
}

const executeScroll = async (action) => {
  const amount = typeof action.amount === 'number' ? action.amount : 300
  switch (action.direction) {
    case 'up':
      window.scrollBy({ top: -amount, behavior: 'smooth' })
      break
    case 'down':
      window.scrollBy({ top: amount, behavior: 'smooth' })
      break
    case 'top':
      window.scrollTo({ top: 0, behavior: 'smooth' })
      break
    case 'bottom':
      window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' })
      break
    default:
      throw new Error(`Unknown scroll direction: ${action.direction}`)
  }

  return {
    success: true,
    message: `Scrolled ${action.direction}`,
    action
  }
}

const executeScrollToElement = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  element.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
    inline: 'nearest'
  })

  return {
    success: true,
    message: `Scrolled to ${action.targetId}`,
    action
  }
}

const executeWait = async (action) => {
  const duration = typeof action.duration === 'number' ? action.duration : 500
  await sleep(duration)
  return {
    success: true,
    message: `Waited ${duration}ms`,
    action
  }
}

const executeType = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  const tagName = element.tagName.toLowerCase()
  if (tagName !== 'input' && tagName !== 'textarea') {
    throw new Error(`Cannot type into ${tagName} element`)
  }

  element.focus()
  element.value = action.text
  element.dispatchEvent(new Event('input', { bubbles: true }))
  element.dispatchEvent(new Event('change', { bubbles: true }))

  return {
    success: true,
    message: `Typed "${action.text}" into ${action.targetId}`,
    action
  }
}

const executeFocus = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  element.focus()
  return {
    success: true,
    message: `Focused on ${action.targetId}`,
    action
  }
}

const executeSubmit = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  const tagName = element.tagName.toLowerCase()
  if (tagName === 'form') {
    if (typeof element.requestSubmit === 'function') {
      element.requestSubmit()
    } else {
      element.submit()
    }
  } else if (tagName === 'button' || (tagName === 'input' && element.type === 'submit')) {
    element.click()
  } else {
    throw new Error(`Cannot submit ${tagName} element`)
  }

  return {
    success: true,
    message: `Submitted ${action.targetId}`,
    action
  }
}

const executeClear = async (action) => {
  const element = findElementByNavId(action.targetId)
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  const tagName = element.tagName.toLowerCase()
  if (tagName !== 'input' && tagName !== 'textarea') {
    throw new Error(`Cannot clear ${tagName} element`)
  }

  element.value = ''
  element.dispatchEvent(new Event('input', { bubbles: true }))
  element.dispatchEvent(new Event('change', { bubbles: true }))

  return {
    success: true,
    message: `Cleared ${action.targetId}`,
    action
  }
}

const executeError = async (action) => ({
  success: false,
  message: action.message || 'Unknown error',
  action
})

const executeSingleAction = async (action) => {
  if (!action || typeof action !== 'object') {
    throw new Error('Invalid action payload')
  }

  switch (action.action) {
    case 'navigate':
      return await executeNavigate(action)
    case 'scroll':
      return await executeScroll(action)
    case 'scrollToElement':
      return await executeScrollToElement(action)
    case 'wait':
      return await executeWait(action)
    case 'type':
      return await executeType(action)
    case 'focus':
      return await executeFocus(action)
    case 'submit':
      return await executeSubmit(action)
    case 'clear':
      return await executeClear(action)
    case 'error':
      return await executeError(action)
    default:
      throw new Error(`Unknown action type: ${action.action}`)
  }
}

const executeAction = async (action) => {
  if (Array.isArray(action)) {
    const results = []
    for (const single of action) {
      const result = await executeSingleAction(single)
      results.push(result)

      if (!result.success) {
        return {
          success: false,
          message: `Sequence failed on action ${single.action}`,
          actions: results,
          isSequence: true
        }
      }

      if (single.action !== 'wait') {
        await sleep(150)
      }
    }

    return {
      success: true,
      message: `Executed ${results.length} actions`,
      actions: results,
      isSequence: true
    }
  }

  return await executeSingleAction(action)
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

  if (event.data?.type === 'EXECUTE_ACTION') {
    const action = event.data.action
    console.log('[Iframe] Received EXECUTE_ACTION:', action)

    executeAction(action)
      .then((result) => {
        console.log('[Iframe] Action executed:', result)
        window.parent.postMessage(
          {
            type: 'ACTION_RESULT',
            result
          },
          PARENT_ORIGIN
        )
      })
      .catch((error) => {
        console.error('[Iframe] Action execution failed:', error)
        window.parent.postMessage(
          {
            type: 'ACTION_RESULT',
            result: {
              success: false,
              message: error?.message || 'Iframe action execution failed',
              action
            }
          },
          PARENT_ORIGIN
        )
      })
  }
})

console.log('[Iframe] DOM snapshot listener initialized, listening for requests from:', PARENT_ORIGIN)

