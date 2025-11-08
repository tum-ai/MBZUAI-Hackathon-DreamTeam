import { useState } from 'react'
import './GlassCard.css'

function GlassCard({ children, className = '', hoverable = false, onClick, style = {} }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className={`glass-card ${hoverable ? 'glass-card--hoverable' : ''} ${className}`}
      onClick={onClick}
      onMouseEnter={() => hoverable && setIsHovered(true)}
      onMouseLeave={() => hoverable && setIsHovered(false)}
      style={style}
    >
      {children}
    </div>
  )
}

export default GlassCard

