import StatusIndicator from './StatusIndicator'
import './CanvasFrame.css'

function CanvasFrame({ src, status = 'connected', title = 'Canvas — Live Preview' }) {
  return (
    <div className="canvas-frame">
      <div className="canvas-frame__header">
        <span className="canvas-frame__title">{title}</span>
        <StatusIndicator status={status} />
      </div>
      <div className="canvas-frame__container">
        <iframe
          src={src}
          className="canvas-frame__iframe"
          title={title}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        />
      </div>
    </div>
  )
}

export default CanvasFrame

