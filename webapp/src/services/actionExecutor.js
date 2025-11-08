/**
 * Action Executor Service
 * Executes navigation actions in the browser
 */

import { findElementByNavId, highlightElement } from '../utils/domSnapshot'

/**
 * Phase 5: Check if an action can be reversed
 */
export const isReversible = (action) => {
  if (!action || !action.action) return false
  
  switch (action.action) {
    case 'navigate':
    case 'scroll':
    case 'scrollToElement':
    case 'type':
    case 'clear':
      return true
    
    case 'submit':
      return false // ⚠️ Cannot undo form submission
    
    case 'wait':
    case 'focus':
      return null // No state change to undo
    
    default:
      return false
  }
}

/**
 * Phase 5: Get user-friendly reason why action can't be reversed
 */
export const getNonReversibleReason = (action) => {
  if (!action || !action.action) return 'Unknown action'
  
  switch (action.action) {
    case 'submit':
      return 'Form submissions cannot be undone as they may have already been processed by the server'
    default:
      return 'This action cannot be reversed'
  }
}

/**
 * Phase 5: Capture state before action for undo
 */
export const captureBeforeState = (action) => {
  if (!action || !action.action) return {}
  
  try {
    switch (action.action) {
      case 'navigate':
        return {
          url: window.location.pathname,
          scrollY: window.scrollY
        }
      
      case 'scroll':
      case 'scrollToElement':
        return {
          scrollY: window.scrollY
        }
      
      case 'type':
      case 'clear':
        const element = findElementByNavId(action.targetId)
        return {
          value: element?.value || '',
          targetId: action.targetId
        }
      
      case 'submit':
        return {
          warning: 'Form submission cannot be fully undone'
        }
      
      default:
        return {}
    }
  } catch (error) {
    console.error('Error capturing before state:', error)
    return {}
  }
}

/**
 * Execute a navigation action (supports single action or array of actions)
 */
export const executeAction = async (action) => {
  console.log('Executing action:', action)

  // Handle action sequences (Phase 2 feature)
  if (Array.isArray(action)) {
    return await executeActionSequence(action)
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
      return executeError(action)
    
    default:
      throw new Error(`Unknown action type: ${action.action}`)
  }
}

/**
 * Execute navigate action (click on element)
 */
const executeNavigate = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Visual feedback: highlight before clicking
  highlightElement(element, 800)
  
  // Wait a moment for visual feedback
  await sleep(400)
  
  // Execute the click
  element.click()
  
  return {
    success: true,
    message: `Clicked on ${action.targetId}`,
    action
  }
}

/**
 * Execute scroll action
 */
const executeScroll = async (action) => {
  const { direction, amount } = action
  
  let scrollOptions = {
    behavior: 'smooth'
  }

  switch (direction) {
    case 'up':
      window.scrollBy({ top: -(amount || 300), ...scrollOptions })
      break
    
    case 'down':
      window.scrollBy({ top: (amount || 300), ...scrollOptions })
      break
    
    case 'top':
      window.scrollTo({ top: 0, ...scrollOptions })
      break
    
    case 'bottom':
      window.scrollTo({ 
        top: document.documentElement.scrollHeight, 
        ...scrollOptions 
      })
      break
    
    default:
      throw new Error(`Unknown scroll direction: ${direction}`)
  }

  return {
    success: true,
    message: `Scrolled ${direction}`,
    action
  }
}

/**
 * Execute scroll to specific element (Phase 2)
 */
const executeScrollToElement = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Visual feedback: highlight the target
  highlightElement(element, 1500)
  
  // Scroll to element smoothly
  element.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start',
    inline: 'nearest'
  })

  return {
    success: true,
    message: `Scrolled to ${action.targetId}`,
    action
  }
}

/**
 * Execute wait action (Phase 2)
 */
const executeWait = async (action) => {
  const duration = action.duration || 500
  await sleep(duration)
  
  return {
    success: true,
    message: `Waited ${duration}ms`,
    action
  }
}

/**
 * Execute type action (Phase 4) - Type text into an input field
 */
const executeType = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Check if element is an input or textarea
  const tagName = element.tagName.toLowerCase()
  if (tagName !== 'input' && tagName !== 'textarea') {
    throw new Error(`Cannot type into ${tagName} element`)
  }

  // Visual feedback: highlight the input
  highlightElement(element, 1000)
  
  // Focus the element
  element.focus()
  await sleep(200)
  
  // Set the value
  element.value = action.text
  
  // Trigger input event for React/Vue reactivity
  const inputEvent = new Event('input', { bubbles: true })
  element.dispatchEvent(inputEvent)
  
  // Trigger change event
  const changeEvent = new Event('change', { bubbles: true })
  element.dispatchEvent(changeEvent)

  return {
    success: true,
    message: `Typed "${action.text}" into ${action.targetId}`,
    action
  }
}

/**
 * Execute focus action (Phase 4) - Focus on an input field
 */
const executeFocus = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Visual feedback
  highlightElement(element, 800)
  
  // Focus the element
  element.focus()

  return {
    success: true,
    message: `Focused on ${action.targetId}`,
    action
  }
}

/**
 * Execute submit action (Phase 4) - Submit a form
 */
const executeSubmit = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Check if it's a form or submit button
  const tagName = element.tagName.toLowerCase()
  
  if (tagName === 'form') {
    // Highlight form briefly
    highlightElement(element, 1000)
    await sleep(500)
    
    // Submit the form
    element.submit()
  } else if (tagName === 'button' || (tagName === 'input' && element.type === 'submit')) {
    // Highlight button
    highlightElement(element, 800)
    await sleep(400)
    
    // Click the submit button
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

/**
 * Execute clear action (Phase 4) - Clear an input field
 */
const executeClear = async (action) => {
  const element = findElementByNavId(action.targetId)
  
  if (!element) {
    throw new Error(`Element not found: ${action.targetId}`)
  }

  // Check if element is an input or textarea
  const tagName = element.tagName.toLowerCase()
  if (tagName !== 'input' && tagName !== 'textarea') {
    throw new Error(`Cannot clear ${tagName} element`)
  }

  // Visual feedback
  highlightElement(element, 800)
  
  // Clear the value
  element.value = ''
  
  // Trigger events for reactivity
  const inputEvent = new Event('input', { bubbles: true })
  element.dispatchEvent(inputEvent)
  
  const changeEvent = new Event('change', { bubbles: true })
  element.dispatchEvent(changeEvent)

  return {
    success: true,
    message: `Cleared ${action.targetId}`,
    action
  }
}

/**
 * Execute undo action (Phase 5)
 */
const executeUndo = async (historyEntry) => {
  if (!historyEntry) {
    throw new Error('No action to undo')
  }

  const { action, beforeState } = historyEntry
  
  switch (action.action) {
    case 'navigate':
      // Navigate back to previous URL
      if (beforeState.url !== window.location.pathname) {
        window.history.pushState({}, '', beforeState.url)
        window.dispatchEvent(new PopStateEvent('popstate'))
        await sleep(300)
      }
      if (beforeState.scrollY !== window.scrollY) {
        window.scrollTo({ top: beforeState.scrollY, behavior: 'smooth' })
      }
      break
    
    case 'scroll':
    case 'scrollToElement':
      // Scroll back to previous position
      window.scrollTo({ top: beforeState.scrollY, behavior: 'smooth' })
      break
    
    case 'type':
    case 'clear':
      // Restore previous input value
      const element = findElementByNavId(beforeState.targetId)
      if (element) {
        element.value = beforeState.value
        element.dispatchEvent(new Event('input', { bubbles: true }))
        element.dispatchEvent(new Event('change', { bubbles: true }))
        highlightElement(element, 800)
      }
      break
    
    default:
      throw new Error(`Cannot undo action type: ${action.action}`)
  }
  
  return {
    success: true,
    message: `Undid: ${historyEntry.command}`,
    action: { action: 'undo', command: historyEntry.command }
  }
}

/**
 * Handle error action
 */
const executeError = (action) => {
  return {
    success: false,
    message: action.message,
    action
  }
}

/**
 * Utility: sleep function
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Phase 5: Export undo executor for external use
 */
export { executeUndo }

/**
 * Execute a sequence of actions (Phase 2 feature)
 */
export const executeActionSequence = async (actions, onProgress) => {
  const results = []
  
  console.log(`Executing action sequence (${actions.length} actions)`)
  
  for (let i = 0; i < actions.length; i++) {
    const action = actions[i]
    
    console.log(`Step ${i + 1}/${actions.length}:`, action)
    
    if (onProgress) {
      onProgress(i, actions.length, action)
    }

    try {
      // Execute individual action (but not if it's an array itself)
      let result
      if (Array.isArray(action)) {
        throw new Error('Nested action sequences are not supported')
      }
      
      // Execute single action
      switch (action.action) {
        case 'navigate':
          result = await executeNavigate(action)
          break
        case 'scroll':
          result = await executeScroll(action)
          break
        case 'scrollToElement':
          result = await executeScrollToElement(action)
          break
        case 'wait':
          result = await executeWait(action)
          break
        case 'type':
          result = await executeType(action)
          break
        case 'focus':
          result = await executeFocus(action)
          break
        case 'submit':
          result = await executeSubmit(action)
          break
        case 'clear':
          result = await executeClear(action)
          break
        case 'error':
          result = executeError(action)
          break
        default:
          throw new Error(`Unknown action type: ${action.action}`)
      }
      
      results.push(result)
      
      // Brief pause between actions (unless it's a wait action)
      if (action.action !== 'wait') {
        await sleep(300)
      }
    } catch (error) {
      results.push({
        success: false,
        message: error.message,
        action
      })
      break // Stop on first error
    }
  }

  // Return summary result
  const allSuccess = results.every(r => r.success)
  return {
    success: allSuccess,
    message: allSuccess 
      ? `Completed ${results.length} actions successfully` 
      : `Failed after ${results.filter(r => r.success).length} actions`,
    actions: results,
    isSequence: true
  }
}

