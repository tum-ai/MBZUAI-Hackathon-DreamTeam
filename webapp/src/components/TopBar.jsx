import { useNavigate, useLocation } from 'react-router-dom'
import './TopBar.css'

function TopBar({ title = 'Voice-First Platform', showBack = false, children }) {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBack = () => {
    if (location.pathname.startsWith('/editor')) {
      navigate('/templates')
    } else if (location.pathname === '/templates') {
      navigate('/')
    } else {
      navigate(-1)
    }
  }

  return (
    <div className="top-bar">
      <div className="top-bar__left">
        {showBack && (
          <button className="top-bar__back" onClick={handleBack} aria-label="Go back" data-nav-id="topbar-back-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M12.5 15L7.5 10L12.5 5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        )}
        <div className="top-bar__logo">
          <svg viewBox="0 0 320 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* K2 geometric shape - complete */}
            {/* Top horizontal bar */}
            <rect x="25" y="17" width="89" height="18" fill="#EF5F3A"/>
            {/* Diagonal piece */}
            <polygon points="40,35 89,35 59,87 40,87 59,50" fill="#EF5F3A"/>
            {/* Bottom left square */}
            <rect x="10" y="67" width="30" height="20" fill="#EF5F3A"/>
            
            {/* K2 Ink text in strong orange */}
            <text x="123" y="70" fontFamily="Arial, sans-serif" fontSize="55" fontWeight="700" fill="#FF6B35">K2 Ink</text>
          </svg>
        </div>
      </div>
      <div className="top-bar__right">
        {children}
      </div>
    </div>
  )
}

export default TopBar

