import { useState, useRef } from 'react'
import { useVoice } from '../context/VoiceContext'
import { recordAndTranscribe } from '../services/whisper'
import { queryAgent, validateAction } from '../services/llmAgent'
import { executeAction, executeUndo, isReversible, getNonReversibleReason, captureBeforeState } from '../services/actionExecutor'
import { captureCombinedDOMSnapshot } from '../utils/iframeDomSnapshot'
import { routeAndExecuteAction } from '../services/actionRouter'

function VoiceControl() {
  const { 
    isListening, 
    setIsListening, 
    transcript, 
    setTranscript,
    addAction,
    isProcessing,
    setIsProcessing,
    // Phase 5: History
    addToHistory,
    canUndo,
    canRedo,
    getUndoAction,
    getRedoAction,
    setHistoryIndex,
    // Phase 5: Confirmation
    confirmDialog,
    setConfirmDialog
  } = useVoice()

  const [error, setError] = useState(null)
  const recorderRef = useRef(null)

  const handleStartRecording = async () => {
    try {
      setError(null)
      setTranscript('')
      
      const recorder = await recordAndTranscribe(
        async (transcribedText) => {
          setIsListening(false)
          setTranscript(transcribedText)
          
          // Process the command
          await processCommand(transcribedText)
        },
        (error) => {
          setIsListening(false)
          setError(error.message)
        }
      )

      recorderRef.current = recorder
      setIsListening(true)
    } catch (error) {
      setError(error.message)
      setIsListening(false)
    }
  }

  const handleStopRecording = () => {
    if (recorderRef.current) {
      recorderRef.current.stop()
    }
  }

  // Phase 5: Check if action contains submit
  const containsSubmit = (act) => {
    if (Array.isArray(act)) {
      return act.some(a => a.action === 'submit')
    }
    return act && act.action === 'submit'
  }

  // Phase 5: Show confirmation dialog
  const confirmSubmit = () => {
    return new Promise((resolve) => {
      setConfirmDialog({
        visible: true,
        message: "⚠️ You're about to submit a form. This action cannot be undone. Continue?",
        onConfirm: () => {
          setConfirmDialog({ visible: false })
          resolve(true)
        },
        onCancel: () => {
          setConfirmDialog({ visible: false })
          resolve(false)
        }
      })
    })
  }

  // Phase 5: Handle undo
  const handleUndo = async () => {
    const undoData = getUndoAction()
    if (!undoData) {
      return
    }

    try {
      setIsProcessing(true)
      
      const result = await executeUndo(undoData.entry)
      
      setHistoryIndex(undoData.index - 1)
      
      addAction({
        command: `Undo: ${undoData.entry.command}`,
        action: result.action,
        result,
        success: result.success
      })
      
      setIsProcessing(false)
    } catch (error) {
      console.error('Error undoing:', error)
      setError(error.message)
      setIsProcessing(false)
    }
  }

  // Phase 5: Handle redo
  const handleRedo = async () => {
    const redoData = getRedoAction()
    if (!redoData) {
      return
    }

    try {
      setIsProcessing(true)
      
      const result = await executeAction(redoData.entry.action)
      
      setHistoryIndex(redoData.index)
      
      addAction({
        command: `Redo: ${redoData.entry.command}`,
        action: redoData.entry.action,
        result,
        success: result.success
      })
      
      setIsProcessing(false)
    } catch (error) {
      console.error('Error redoing:', error)
      setError(error.message)
      setIsProcessing(false)
    }
  }

  const processCommand = async (command) => {
    try {
      setIsProcessing(true)
      
      // Step 1: Capture combined DOM state (main app + iframe)
      console.log('[VoiceControl] Capturing combined DOM snapshot...')
      const domSnapshot = await captureCombinedDOMSnapshot()
      console.log('[VoiceControl] Combined DOM snapshot:', {
        total: domSnapshot.totalElementCount,
        mainApp: domSnapshot.elements.filter(el => el.context === 'main-app').length,
        iframe: domSnapshot.iframeElementCount
      })
      
      // Step 2: Query LLM agent
      const action = await queryAgent(command, domSnapshot)
      console.log('[VoiceControl] LLM action:', action)
      
      // Step 3: Validate action
      if (!validateAction(action)) {
        throw new Error('Invalid action returned from agent')
      }

      // Phase 5: Handle undo command
      if (action.action === 'undo') {
        setIsProcessing(false)
        await handleUndo()
        return
      }

      // Phase 5: Handle redo command
      if (action.action === 'redo') {
        setIsProcessing(false)
        await handleRedo()
        return
      }

      // Phase 5: Confirmation for submit
      if (containsSubmit(action)) {
        const confirmed = await confirmSubmit()
        if (!confirmed) {
          addAction({
            command,
            action: null,
            result: { success: false, message: 'Submission cancelled by user' },
            success: false
          })
          setIsProcessing(false)
          return
        }
      }

      // Phase 5: Capture state before action for undo
      const beforeState = Array.isArray(action) 
        ? {} // For sequences, we'll handle this differently
        : captureBeforeState(action)

      // Step 4: Route and execute action (main app or iframe)
      console.log('[VoiceControl] Routing action...')
      const result = await routeAndExecuteAction(action, domSnapshot)
      console.log('[VoiceControl] Action result:', result)

      // Phase 5: Determine if action can be undone
      const reversibility = Array.isArray(action)
        ? action.some(a => isReversible(a) === false) ? false : true
        : isReversible(action)
      
      const canUndoAction = reversibility === true
      const nonReversibleReason = reversibility === false
        ? (Array.isArray(action) 
           ? 'Sequence contains non-reversible actions'
           : getNonReversibleReason(action))
        : null

      // Step 5: Log to action history
      addAction({
        command,
        action,
        result,
        success: result.success,
        canUndo: canUndoAction,
        nonReversibleReason
      })

      // Phase 5: Add to undo history
      if (canUndoAction) {
        addToHistory({
          command,
          action,
          beforeState,
          result,
          canUndo: true
        })
      } else {
        addToHistory({
          command,
          action,
          beforeState,
          result,
          canUndo: false,
          nonReversibleReason
        })
      }

      setIsProcessing(false)
    } catch (error) {
      console.error('Error processing command:', error)
      setError(error.message)
      setIsProcessing(false)
      
      addAction({
        command,
        action: null,
        result: { success: false, message: error.message },
        success: false
      })
    }
  }

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg"
      data-nav-id="voice-control-panel"
    >
      <div className="container mx-auto px-4 py-4">
        {/* Error Display */}
        {error && (
          <div 
            className="mb-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm"
            data-nav-id="error-message"
          >
            ⚠️ {error}
          </div>
        )}

        {/* Transcript Display */}
        {transcript && (
          <div 
            className="mb-3 bg-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-lg"
            data-nav-id="transcript-display"
          >
            <span className="font-semibold">You said:</span> "{transcript}"
          </div>
        )}

        {/* Processing Indicator */}
        {isProcessing && (
          <div 
            className="mb-3 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 rounded-lg flex items-center"
            data-nav-id="processing-indicator"
          >
            <div className="animate-spin mr-2 h-4 w-4 border-2 border-yellow-600 border-t-transparent rounded-full"></div>
            Processing your command...
          </div>
        )}

        <div className="flex items-center justify-between">
          {/* Instructions */}
          <div className="flex-1" data-nav-id="voice-instructions">
            <p className="text-sm text-gray-600">
              {isListening ? (
                <span className="text-red-600 font-semibold animate-pulse">
                  🎤 Listening... Speak your command
                </span>
              ) : (
                <>
                  Press the microphone to start. Try: <span className="font-mono text-blue-600">"Go to About"</span> or <span className="font-mono text-blue-600">"Undo"</span>
                </>
              )}
            </p>
          </div>

          {/* Phase 5: Undo/Redo Buttons */}
          <div className="flex space-x-2 ml-4">
            <button 
              onClick={handleUndo}
              disabled={!canUndo() || isProcessing}
              title={canUndo() ? "Undo last action" : "Nothing to undo"}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
              data-nav-id="undo-button"
            >
              ↶ Undo
            </button>
            <button 
              onClick={handleRedo}
              disabled={!canRedo() || isProcessing}
              title={canRedo() ? "Redo action" : "Nothing to redo"}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
              data-nav-id="redo-button"
            >
              ↷ Redo
            </button>
          </div>

          {/* Microphone Button */}
          <button
            onClick={isListening ? handleStopRecording : handleStartRecording}
            disabled={isProcessing}
            className={`
              ml-4 w-16 h-16 rounded-full flex items-center justify-center
              transition-all transform hover:scale-110 active:scale-95
              ${isListening 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-600 hover:bg-blue-700'
              }
              ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'shadow-lg'}
              disabled:hover:scale-100
            `}
            data-nav-id="microphone-button"
          >
            {isListening ? (
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <rect x="6" y="6" width="8" height="8" />
              </svg>
            ) : (
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M7 4a3 3 0 016 0v6a3 3 0 11-6 0V4z" />
                <path d="M5.5 9.643a.75.75 0 00-1.5 0V10c0 3.06 2.29 5.585 5.25 5.954V17.5h-1.5a.75.75 0 000 1.5h4.5a.75.75 0 000-1.5h-1.5v-1.546A6.001 6.001 0 0016 10v-.357a.75.75 0 00-1.5 0V10a4.5 4.5 0 01-9 0v-.357z" />
              </svg>
            )}
          </button>
        </div>

        {/* Phase 5: Confirmation Dialog */}
        {confirmDialog.visible && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-nav-id="confirmation-dialog">
            <div className="bg-white rounded-lg p-6 max-w-md shadow-2xl">
              <h3 className="text-lg font-bold mb-3 flex items-center">
                <span className="text-2xl mr-2">⚠️</span>
                Confirm Submission
              </h3>
              <p className="text-gray-700 mb-6">
                {confirmDialog.message}
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={confirmDialog.onCancel}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDialog.onConfirm}
                  className="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition"
                >
                  Submit Anyway
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default VoiceControl

