/**
 * useActionExecutor Hook
 * Provides easy access to action execution for voice navigation
 */

import { useCallback } from 'react'
import { executeAction } from '../services/actionExecutor'
import { captureDOMSnapshot } from '../utils/domSnapshot'

/**
 * Hook for executing navigation actions
 * Returns a function that can execute single actions or action sequences
 */
export function useActionExecutor() {
  /**
   * Execute a single action or sequence of actions
   * @param {Object|Array} action - Action object or array of actions
   * @returns {Promise<Object>} Result of the action execution
   */
  const executeActions = useCallback(async (action) => {
    try {
      const result = await executeAction(action)
      return result
    } catch (error) {
      console.error('Error executing action:', error)
      return {
        success: false,
        message: error.message,
        action
      }
    }
  }, [])

  /**
   * Capture current DOM state
   * Useful for debugging and understanding what elements are available
   * @returns {Object} DOM snapshot with all navigatable elements
   */
  const captureDOM = useCallback(() => {
    return captureDOMSnapshot()
  }, [])

  return {
    executeActions,
    captureDOM
  }
}

export default useActionExecutor

