import { BrowserRouter } from 'react-router-dom'
import AppRouter from './router'
import { VoiceAssistantProvider } from './context/VoiceAssistantContext'
import VoiceAssistantOverlay from './components/VoiceAssistantOverlay'
import DomSnapshotBridge from './components/DomSnapshotBridge'

function App() {
  return (
    <VoiceAssistantProvider>
      <DomSnapshotBridge />
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
      <VoiceAssistantOverlay />
    </VoiceAssistantProvider>
  )
}

export default App

