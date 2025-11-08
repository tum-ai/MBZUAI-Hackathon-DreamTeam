import { createContext, useContext, useState } from 'react'

const VoiceContext = createContext()

export const useVoice = () => {
  const context = useContext(VoiceContext)
  if (!context) {
    throw new Error('useVoice must be used within VoiceProvider')
  }
  return context
}

export const VoiceProvider = ({ children }) => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [actions, setActions] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  
  // Phase 5: History for undo/redo
  const [history, setHistory] = useState([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  
  // Phase 5: Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({ visible: false })

  const addAction = (action) => {
    setActions(prev => [...prev, { ...action, timestamp: new Date().toISOString() }])
  }

  const clearActions = () => {
    setActions([])
  }
  
  // Phase 5: History management
  const addToHistory = (entry) => {
    // Remove any "future" history if we're in the middle of the stack
    const newHistory = history.slice(0, historyIndex + 1)
    newHistory.push({
      ...entry,
      id: `action-${Date.now()}`,
      timestamp: new Date().toISOString()
    })
    
    // Keep only last 20 actions to avoid memory issues
    const trimmedHistory = newHistory.slice(-20)
    
    setHistory(trimmedHistory)
    setHistoryIndex(trimmedHistory.length - 1)
  }
  
  const canUndo = () => {
    if (historyIndex < 0) return false
    
    // Find the last reversible action
    for (let i = historyIndex; i >= 0; i--) {
      if (history[i].canUndo) return true
    }
    return false
  }
  
  const canRedo = () => {
    return historyIndex < history.length - 1
  }
  
  const getUndoAction = () => {
    // Find the last reversible action
    for (let i = historyIndex; i >= 0; i--) {
      if (history[i].canUndo) {
        return { entry: history[i], index: i }
      }
    }
    return null
  }
  
  const getRedoAction = () => {
    if (canRedo()) {
      return { entry: history[historyIndex + 1], index: historyIndex + 1 }
    }
    return null
  }

  const value = {
    isListening,
    setIsListening,
    transcript,
    setTranscript,
    actions,
    addAction,
    clearActions,
    isProcessing,
    setIsProcessing,
    // Phase 5: History
    history,
    historyIndex,
    addToHistory,
    canUndo,
    canRedo,
    getUndoAction,
    getRedoAction,
    setHistoryIndex,
    // Phase 5: Confirmation dialog
    confirmDialog,
    setConfirmDialog
  }

  return (
    <VoiceContext.Provider value={value}>
      {children}
    </VoiceContext.Provider>
  )
}

