import { useVoice } from '../context/VoiceContext'
import { useState } from 'react'

function ActionFeedback() {
  const { actions, clearActions } = useVoice()
  const [isExpanded, setIsExpanded] = useState(true)

  if (actions.length === 0) {
    return null
  }

  const latestAction = actions[actions.length - 1]

  return (
    <div 
      className="fixed top-20 right-4 w-96 bg-white rounded-lg shadow-xl border z-40"
      data-nav-id="action-feedback-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center">
          <span className="text-lg font-semibold text-gray-800">
            Action History
          </span>
          <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
            {actions.length}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-500 hover:text-gray-700"
            data-nav-id="toggle-history-button"
          >
            <svg 
              className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={clearActions}
            className="text-gray-500 hover:text-gray-700"
            data-nav-id="clear-history-button"
            title="Clear history"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      {/* Latest Action (Always Visible) */}
      {!isExpanded && (
        <div className="p-4">
          <ActionItem action={latestAction} isLatest={true} />
        </div>
      )}

      {/* Action List */}
      {isExpanded && (
        <div 
          className="max-h-96 overflow-y-auto"
          data-nav-id="action-history-list"
        >
          {actions.slice().reverse().map((action, index) => (
            <div 
              key={index}
              className="border-b last:border-b-0"
            >
              <ActionItem 
                action={action} 
                isLatest={index === 0}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ActionItem({ action, isLatest }) {
  const getStatusIcon = () => {
    if (action.success) {
      return <span className="text-green-500">✓</span>
    } else {
      return <span className="text-red-500">✗</span>
    }
  }

  const getActionTypeColor = (actionType) => {
    switch (actionType) {
      case 'navigate':
        return 'bg-blue-100 text-blue-800'
      case 'scroll':
        return 'bg-purple-100 text-purple-800'
      case 'scrollToElement':
        return 'bg-indigo-100 text-indigo-800'
      case 'wait':
        return 'bg-gray-100 text-gray-600'
      case 'type':
        return 'bg-green-100 text-green-800'
      case 'focus':
        return 'bg-yellow-100 text-yellow-800'
      case 'submit':
        return 'bg-emerald-100 text-emerald-800'
      case 'clear':
        return 'bg-orange-100 text-orange-800'
      case 'undo':
        return 'bg-amber-100 text-amber-800'
      case 'redo':
        return 'bg-teal-100 text-teal-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Check if this is a multi-step action (Phase 2)
  const isSequence = action.result?.isSequence || Array.isArray(action.action)
  
  // Phase 5: Check if action is non-reversible
  const isNonReversible = action.canUndo === false
  
  return (
    <div className={`p-4 ${isLatest ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            {getStatusIcon()}
            <span className="font-semibold text-sm text-gray-800">
              "{action.command}"
            </span>
            {isSequence && (
              <span className="text-xs bg-purple-200 text-purple-800 px-2 py-0.5 rounded font-semibold">
                {action.result.actions?.length || 0} steps
              </span>
            )}
            
            {/* Phase 5: Non-reversible badge */}
            {isNonReversible && (
              <span 
                className="text-xs bg-orange-100 text-orange-800 px-2 py-0.5 rounded font-semibold flex items-center"
                title={action.nonReversibleReason}
              >
                <span className="mr-1">⚠️</span>
                Cannot Undo
              </span>
            )}
          </div>
          
          {/* Multi-Step Sequence (Phase 2) */}
          {isSequence && action.result?.actions ? (
            <div className="ml-6 mt-2 space-y-2">
              {action.result.actions.map((step, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-xs">
                  <span className="text-gray-400 font-mono">
                    {idx + 1}.
                  </span>
                  <div className="flex-1">
                    <span className={`font-semibold px-2 py-0.5 rounded ${getActionTypeColor(step.action.action)}`}>
                      {step.action.action}
                    </span>
                    {step.action.targetId && (
                      <span className="ml-2 text-gray-600 font-mono">
                        {step.action.targetId}
                      </span>
                    )}
                    {step.action.direction && (
                      <span className="ml-2 text-gray-600">
                        → {step.action.direction}
                      </span>
                    )}
                    {step.action.duration && (
                      <span className="ml-2 text-gray-600">
                        ({step.action.duration}ms)
                      </span>
                    )}
                    {step.action.text && (
                      <span className="ml-2 text-gray-600 italic">
                        "{step.action.text.substring(0, 30)}{step.action.text.length > 30 ? '...' : ''}"
                      </span>
                    )}
                    {step.result.success ? (
                      <span className="ml-2 text-green-600">✓</span>
                    ) : (
                      <span className="ml-2 text-red-600">✗</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : action.action && !Array.isArray(action.action) ? (
            /* Single Action */
            <div className="ml-6">
              <span className={`text-xs font-semibold px-2 py-1 rounded ${getActionTypeColor(action.action.action)}`}>
                {action.action.action}
              </span>
              {action.action.targetId && (
                <span className="ml-2 text-xs text-gray-600 font-mono">
                  {action.action.targetId}
                </span>
              )}
              {action.action.direction && (
                <span className="ml-2 text-xs text-gray-600">
                  → {action.action.direction}
                </span>
              )}
              {action.action.text && (
                <span className="ml-2 text-xs text-gray-600 italic">
                  "{action.action.text.substring(0, 30)}{action.action.text.length > 30 ? '...' : ''}"
                </span>
              )}
            </div>
          ) : null}

          {/* Reasoning (for single actions) */}
          {!isSequence && action.action?.reasoning && (
            <p className="ml-6 mt-1 text-xs text-gray-500 italic">
              {action.action.reasoning}
            </p>
          )}

          {/* Result Message */}
          <p className={`ml-6 mt-1 text-xs ${action.success ? 'text-gray-600' : 'text-red-600'}`}>
            {action.result.message}
          </p>
          
          {/* Phase 5: Show reason for non-reversibility */}
          {isNonReversible && action.nonReversibleReason && (
            <div className="ml-6 mt-2 text-xs bg-orange-50 border-l-2 border-orange-400 p-2 rounded">
              <span className="text-orange-800">
                ⚠️ {action.nonReversibleReason}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ActionFeedback

