import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/tokens.css'
import './styles/global.css'
import { initializeTestHelpers } from './tests/voiceNavigationTests'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// Initialize voice navigation test helpers (for development/testing)
if (import.meta.env.DEV) {
  initializeTestHelpers()
}
