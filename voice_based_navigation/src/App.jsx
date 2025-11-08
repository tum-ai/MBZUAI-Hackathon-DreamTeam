import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import VoiceControl from './components/VoiceControl'
import ActionFeedback from './components/ActionFeedback'
import Home from './pages/Home'
import About from './pages/About'
import Contact from './pages/Contact'
import EditorPage from './pages/EditorPage'
import { VoiceProvider } from './context/VoiceContext'

function App() {
  return (
    <VoiceProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation Bar */}
          <Navigation />
          
          {/* Main Content */}
          <main className="pb-20">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/editor" element={<EditorPage />} />
            </Routes>
          </main>
          
          {/* Voice Control UI - Fixed at bottom */}
          <VoiceControl />
          
          {/* Action Feedback Display */}
          <ActionFeedback />
        </div>
      </Router>
    </VoiceProvider>
  )
}

export default App

