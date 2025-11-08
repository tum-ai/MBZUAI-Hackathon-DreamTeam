import { BrowserRouter } from 'react-router-dom'
import AppRouter from './router'
import { VoiceAssistantProvider } from './context/VoiceAssistantContext'
import VoiceAssistantOverlay from './components/VoiceAssistantOverlay'

function App() {
  return (
    <VoiceAssistantProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
      <VoiceAssistantOverlay />
    </VoiceAssistantProvider>
  )
}

export default App

