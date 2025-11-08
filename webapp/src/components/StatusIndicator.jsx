import './StatusIndicator.css'

function StatusIndicator({ status = 'connected', label }) {
  const statusConfig = {
    connected: {
      color: 'var(--status-connected)',
      label: label || 'Connected'
    },
    updating: {
      color: 'var(--status-updating)',
      label: label || 'Updating'
    },
    error: {
      color: 'var(--status-error)',
      label: label || 'Error'
    }
  }

  const config = statusConfig[status] || statusConfig.connected

  return (
    <div className="status-indicator">
      <div
        className={`status-indicator__dot ${status === 'updating' ? 'status-indicator__dot--pulse' : ''}`}
        style={{ backgroundColor: config.color }}
        aria-label={config.label}
      />
      <span className="status-indicator__label">{config.label}</span>
    </div>
  )
}

export default StatusIndicator

