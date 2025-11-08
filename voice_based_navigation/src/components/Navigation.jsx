import { Link, useLocation } from 'react-router-dom'

function Navigation() {
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <nav 
      className="bg-white shadow-md sticky top-0 z-50"
      data-nav-id="main-navigation"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center" data-nav-id="nav-logo">
            <Link 
              to="/" 
              className="text-2xl font-bold text-blue-600"
              data-nav-id="nav-home"
            >
              🎤 VoiceNav
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex space-x-1" data-nav-id="nav-links">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg transition ${
                isActive('/') 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              data-nav-id="nav-home-link"
            >
              Home
            </Link>
            <Link
              to="/about"
              className={`px-4 py-2 rounded-lg transition ${
                isActive('/about') 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              data-nav-id="nav-about-link"
            >
              About
            </Link>
            <Link
              to="/contact"
              className={`px-4 py-2 rounded-lg transition ${
                isActive('/contact') 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              data-nav-id="nav-contact-link"
            >
              Contact
            </Link>
            <Link
              to="/editor"
              className={`px-4 py-2 rounded-lg transition ${
                isActive('/editor') 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              data-nav-id="nav-editor-link"
            >
              Editor
            </Link>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center" data-nav-id="nav-status">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Voice Ready</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation

