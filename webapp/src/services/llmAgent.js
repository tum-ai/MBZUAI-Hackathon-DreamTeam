/**
 * LLM Agent Service
 * Translates user intent into navigation actions via the backend actor.
 */

const DEFAULT_LLM_API_BASE_URL = 'http://localhost:8000'
const ACTOR_SESSION_STORAGE_KEY = 'voice-control-actor-session-id'

const isBrowser = typeof window !== 'undefined'

const readEnvBaseUrl = () => {
  try {
    return import.meta?.env?.VITE_LLM_API_BASE_URL
  } catch (error) {
    console.warn('[LLM] Unable to read VITE_LLM_API_BASE_URL:', error)
    return undefined
  }
}

const getLlmApiBaseUrl = () => {
  const envBase = readEnvBaseUrl()
  if (envBase && typeof envBase === 'string') {
    return envBase.replace(/\/$/, '')
  }
  if (isBrowser && typeof window.__LLM_API_BASE_URL === 'string') {
    return window.__LLM_API_BASE_URL.replace(/\/$/, '')
  }
  return DEFAULT_LLM_API_BASE_URL
}

const safeGetLocalStorageItem = (key) => {
  if (!isBrowser) {
    return null
  }
  try {
    return window.localStorage.getItem(key)
  } catch (error) {
    console.warn('[LLM] Failed to read from localStorage:', error)
    return null
  }
}

const safeSetLocalStorageItem = (key, value) => {
  if (!isBrowser) {
    return
  }
  try {
    window.localStorage.setItem(key, value)
  } catch (error) {
    console.warn('[LLM] Failed to write to localStorage:', error)
  }
}

const generateId = () => {
  if (typeof globalThis !== 'undefined' && globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }
  return `id_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`
}

const ensureActorSessionId = () => {
  const stored = safeGetLocalStorageItem(ACTOR_SESSION_STORAGE_KEY)
  if (stored) {
    return stored
  }
  const generated = generateId()
  safeSetLocalStorageItem(ACTOR_SESSION_STORAGE_KEY, generated)
  return generated
}

const persistActorSessionId = (sessionId) => {
  if (!sessionId || typeof sessionId !== 'string') {
    return
  }
  safeSetLocalStorageItem(ACTOR_SESSION_STORAGE_KEY, sessionId)
}

/**
 * Build dynamic sitemap from DOM snapshot
 */
const buildDynamicSitemap = (domSnapshot = {}) => {
  const sitemap = {
    mainApp: { sections: [], elements: [], navLinks: [] },
    iframe: { sections: [], elements: [], navLinks: [] }
  }

  const elements = Array.isArray(domSnapshot.elements) ? domSnapshot.elements : []

  elements.forEach((el) => {
    const context = el?.context === 'iframe' ? 'iframe' : 'mainApp'
    const target = context === 'iframe' ? sitemap.iframe : sitemap.mainApp
    const navId = el?.navId || ''

    if (navId.includes('-section')) {
      target.sections.push({
        id: navId,
        text: (el?.text || '').substring(0, 40),
        visible: !!el?.isVisible
      })
    } else if (navId.startsWith('nav-') && el?.tagName === 'a') {
      target.navLinks.push({
        id: navId,
        text: el?.text || '',
        href: el?.href || 'unknown'
      })
    } else {
      target.elements.push({
        id: navId,
        type: el?.tagName || '',
        text: (el?.text || '').substring(0, 40),
        visible: !!el?.isVisible
      })
    }
  })

  return sitemap
}

const buildActorContext = (domSnapshot, extras = {}) => {
  const extraPayload = extras && typeof extras === 'object' ? extras : {}
  const baseContext = {
    source: 'voice-control-frontend',
    timestamp: Date.now(),
    ...extraPayload
  }

  if (!domSnapshot || typeof domSnapshot !== 'object') {
    return JSON.stringify(baseContext)
  }

  const sitemap = buildDynamicSitemap(domSnapshot)
  const contextPayload = {
    ...baseContext,
    currentUrl: domSnapshot.currentUrl ?? null,
    totalElementCount: domSnapshot.totalElementCount ?? null,
    iframeElementCount: domSnapshot.iframeElementCount ?? null,
    viewportHeight: domSnapshot.viewportHeight ?? null,
    scrollY: domSnapshot.scrollY ?? null,
    mainAppNavLinks: sitemap.mainApp.navLinks.slice(0, 10).map((link) => link.id),
    iframeNavLinks: sitemap.iframe.navLinks.slice(0, 10).map((link) => link.id),
    visibleSections: sitemap.mainApp.sections
      .filter((section) => section.visible)
      .slice(0, 10)
      .map((section) => section.id),
    iframeElements: sitemap.iframe.elements.slice(0, 10).map((el) => el.id)
  }

  return JSON.stringify(contextPayload)
}

const stripCodeFence = (text) => text.replace(/```(?:json)?/gi, '').trim()

const extractLikelyJson = (text) => {
  if (!text) {
    return text
  }

  const braceIndex = text.indexOf('{')
  const bracketIndex = text.indexOf('[')

  const startCandidates = [braceIndex, bracketIndex].filter((idx) => idx >= 0)
  if (startCandidates.length === 0) {
    return text
  }

  const start = Math.min(...startCandidates)

  const lastBrace = text.lastIndexOf('}')
  const lastBracket = text.lastIndexOf(']')
  const endCandidates = [lastBrace, lastBracket].filter((idx) => idx >= 0)

  if (endCandidates.length === 0) {
    return text.slice(start)
  }

  const end = Math.max(...endCandidates)
  if (end <= start) {
    return text.slice(start)
  }

  return text.slice(start, end + 1)
}

const parseActionPayload = (raw) => {
  if (raw == null) {
    throw new Error('Actor response is missing an action payload')
  }

  if (typeof raw === 'object') {
    return raw
  }

  if (typeof raw !== 'string') {
    throw new Error(`Actor returned an unsupported action payload type: ${typeof raw}`)
  }

  let candidate = stripCodeFence(raw)

  const tryParse = (value) => {
    try {
      return JSON.parse(value)
    } catch {
      return null
    }
  }

  let parsed = tryParse(candidate)
  if (parsed !== null) {
    return parsed
  }

  candidate = extractLikelyJson(candidate)
  parsed = tryParse(candidate)

  if (parsed !== null) {
    return parsed
  }

  console.error('[LLM] Failed to parse actor action payload:', raw)
  throw new Error('Actor returned an invalid action payload')
}

/**
 * Query the backend actor with the user command.
 */
export const queryAgent = async (userCommand, domSnapshot, options = {}) => {
  if (!userCommand || typeof userCommand !== 'string') {
    throw new Error('User command is required to query the actor')
  }

  const {
    sessionId: overrideSessionId,
    stepId: overrideStepId,
    context: overrideContext,
    signal,
    metadata
  } = options

  const baseUrl = getLlmApiBaseUrl()
  const sessionId = overrideSessionId || ensureActorSessionId()
  const stepId = overrideStepId || generateId()

  const context =
    typeof overrideContext === 'string'
      ? overrideContext
      : buildActorContext(domSnapshot, metadata)

  const payload = {
    session_id: sessionId,
    step_id: stepId,
    intent: userCommand,
    context: context || ''
  }

  console.log('[LLM] Sending actor request', payload)

  const response = await fetch(`${baseUrl}/action`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload),
    signal
  })

  if (!response.ok) {
    const errorText = await response.text()
    let message = `Actor request failed (${response.status})`

    if (errorText) {
      try {
        const parsedError = JSON.parse(errorText)
        const detail = parsedError?.detail
        if (Array.isArray(detail)) {
          message = detail
            .map((item) => {
              if (typeof item === 'string') return item
              if (item?.msg) return item.msg
              return JSON.stringify(item)
            })
            .join('; ')
        } else if (typeof detail === 'string') {
          message = detail
        } else if (parsedError?.message) {
          message = parsedError.message
        }
      } catch {
        message = errorText
      }
    }

    throw new Error(message)
  }

  const responseJson = await response.json()
  const finalSessionId = responseJson.session_id || sessionId
  const finalStepId = responseJson.step_id || stepId

  persistActorSessionId(finalSessionId)

  const parsedAction = parseActionPayload(responseJson.action)

  console.log('[LLM] Actor response', {
    sessionId: finalSessionId,
    stepId: finalStepId,
    action: parsedAction
  })

  return {
    action: parsedAction,
    rawAction: responseJson.action,
    sessionId: finalSessionId,
    stepId: finalStepId
  }
}

/**
 * Validate that an action has the required fields (Phase 2: supports arrays)
 */
export const validateAction = (action) => {
  // Handle action sequences
  if (Array.isArray(action)) {
    return action.length > 0 && action.every((a) => validateAction(a))
  }

  if (!action || typeof action !== 'object') {
    return false
  }

  if (!action.action) {
    return false
  }

  // Validate based on action type
  switch (action.action) {
    case 'navigate':
      return !!action.targetId
    case 'scroll':
      return !!action.direction
    case 'scrollToElement':
      return !!action.targetId
    case 'wait':
      return typeof action.duration === 'number' && action.duration > 0
    case 'type':
      return !!action.targetId && typeof action.text === 'string'
    case 'focus':
      return !!action.targetId
    case 'submit':
      return !!action.targetId
    case 'clear':
      return !!action.targetId
    case 'undo':
    case 'redo':
      return true // No additional validation needed
    case 'error':
      return !!action.message
    default:
      return false
  }
}

