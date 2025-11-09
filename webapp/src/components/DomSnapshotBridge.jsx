import { useEffect, useRef, useState } from 'react'
import { captureCombinedDOMSnapshot } from '../utils/domSnapshot'

const DOM_WEBSOCKET_PATH = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_DOM_WEBSOCKET_PATH) || '/dom-snapshot'
const DOM_WEBSOCKET_HOST = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_DOM_WEBSOCKET_HOST) || null
const RECONNECT_DELAY_MS = 3000
const BRIDGE_KEY = '__DOM_SNAPSHOT_BRIDGE__'

const DomSnapshotBridge = () => {
  const socketRef = useRef(null)
  const reconnectTimerRef = useRef(null)
  const captureInProgressRef = useRef(false)
  const isShuttingDownRef = useRef(false)
  const didInitRef = useRef(false)
  const [connectionState, setConnectionState] = useState('idle')

  useEffect(() => {
    if (didInitRef.current) return
      didInitRef.current = true

    if (window[BRIDGE_KEY]?.active) {
      setConnectionState('connected')
      return
    }
    window[BRIDGE_KEY] = { active: true }

    isShuttingDownRef.current = false;
    if (typeof window === 'undefined' || typeof WebSocket === 'undefined') {
      return undefined
    }

    const connect = () => {
      if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
        return
      }
      clearReconnectTimer()

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = DOM_WEBSOCKET_HOST || window.location.host
      const url = `${protocol}//${host}${DOM_WEBSOCKET_PATH}`

      setConnectionState('connecting')

      console.log('[DomSnapshotBridge] Connecting to', url)
      const socket = new WebSocket(url)
      socketRef.current = socket

      socket.addEventListener('open', () => {
        setConnectionState('connected')
        safeSend(socket, { type: 'register', role: 'frontend' })
      })

      socket.addEventListener('close', () => {
        if (isShuttingDownRef.current) return
        setConnectionState('disconnected')
        scheduleReconnect()
      })

      socket.addEventListener('error', () => {
        socket.close()
      })

      socket.addEventListener('message', (event) => {
        let payload
        try {
          payload = JSON.parse(event.data)
        } catch (error) {
          console.warn('[DomSnapshotBridge] Received non-JSON message', error)
          return
        }

        if (payload?.type === 'dom_snapshot_request') {
          handleSnapshotRequest(socket, payload)
        } else if (payload?.type === 'ping') {
          safeSend(socket, { type: 'pong', timestamp: Date.now() })
        } else if (payload?.type === 'status') {
          setConnectionState((prev) => (prev === 'connected' ? prev : 'connected'))
        }
      })
    }

    const safeSend = (socket, message) => {
      if (!socket || socket.readyState !== WebSocket.OPEN) return
      try {
        socket.send(JSON.stringify(message))
      } catch (error) {
        console.warn('[DomSnapshotBridge] Failed to send message', error)
      }
    }

    const handleSnapshotRequest = async (socket, payload) => {
      if (captureInProgressRef.current) {
        safeSend(socket, {
          type: 'dom_snapshot_response',
          requestId: payload?.requestId || null,
          error: 'capture_in_progress'
        })
        return
      }

      captureInProgressRef.current = true
      try {
        const snapshot = await captureCombinedDOMSnapshot()
        safeSend(socket, {
          type: 'dom_snapshot_response',
          requestId: payload?.requestId || null,
          snapshot,
          timestamp: Date.now()
        })
      } catch (error) {
        safeSend(socket, {
          type: 'dom_snapshot_response',
          requestId: payload?.requestId || null,
          error: error?.message || 'capture_failed'
        })
      } finally {
        captureInProgressRef.current = false
      }
    }

    const scheduleReconnect = () => {
      if (reconnectTimerRef.current || isShuttingDownRef.current) return
      reconnectTimerRef.current = window.setTimeout(() => {
        reconnectTimerRef.current = null
        connect()
      }, RECONNECT_DELAY_MS)
    }

    const clearReconnectTimer = () => {
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current)
        reconnectTimerRef.current = null
      }
    }

    connect()

    return () => {
      isShuttingDownRef.current = true
      clearReconnectTimer()
      const socket = socketRef.current
      if (socket && socket.readyState === WebSocket.OPEN) {
        try {
          socket.close(1000, 'component_unmounted')
        } catch {
          socket.close()
        }
      }
      socketRef.current = null
      if (window[BRIDGE_KEY]) window[BRIDGE_KEY].active = false
    }
  }, [])

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.__DOM_SNAPSHOT_BRIDGE_STATE__ = connectionState
    }
  }, [connectionState])

  return null
}

export default DomSnapshotBridge


