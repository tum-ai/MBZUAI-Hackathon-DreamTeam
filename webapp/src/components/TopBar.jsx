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
          <button className="top-bar__back" onClick={handleBack} aria-label="Go back">
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
        <h1 className="top-bar__title">{title}</h1>
      </div>
      <div className="top-bar__right">
        {children}
      </div>
    </div>
  )
}

export default TopBar

