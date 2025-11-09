import { createHash, randomBytes, randomUUID as cryptoRandomUUID } from 'node:crypto'
import { createServer } from 'node:http'

const HANDSHAKE_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
const DEFAULT_PATH = '/dom-snapshot'
const DEFAULT_TIMEOUT_MS = 10000
const DEFAULT_HOST = '0.0.0.0'

const createRequestId = () => {
  if (typeof cryptoRandomUUID === 'function') {
    return cryptoRandomUUID()
  }
  return randomBytes(16).toString('hex')
}

class RawWebSocketConnection {
  constructor(socket) {
    this.socket = socket
    this.buffer = Buffer.alloc(0)
    this.isClosed = false
    this.role = 'unknown'
    this.id = createRequestId()
    this.messageHandler = null
    this.closeHandler = null
    this.isAlive = true

    socket.on('data', (chunk) => this.handleData(chunk))
    socket.on('close', () => this.handleClose())
    socket.on('end', () => this.handleClose())
    socket.on('error', () => this.handleClose())
  }

  onMessage(handler) {
    this.messageHandler = handler
  }

  onClose(handler) {
    this.closeHandler = handler
  }

  sendJson(payload) {
    if (this.isClosed) return
    try {
      const data = Buffer.from(JSON.stringify(payload))
      this.sendFrame(data, 0x1)
    } catch (error) {
      console.warn('[DomSnapshotServer] Failed to serialize payload', error)
    }
  }

  handleData(chunk) {
    if (this.isClosed) {
      return
    }

    this.buffer = Buffer.concat([this.buffer, chunk])

    while (this.buffer.length >= 2) {
      const firstByte = this.buffer[0]
      const secondByte = this.buffer[1]

      const fin = (firstByte & 0x80) !== 0
      const opcode = firstByte & 0x0f
      const masked = (secondByte & 0x80) !== 0

      let payloadLength = secondByte & 0x7f
      let offset = 2

      if (payloadLength === 126) {
        if (this.buffer.length < offset + 2) return
        payloadLength = this.buffer.readUInt16BE(offset)
        offset += 2
      } else if (payloadLength === 127) {
        if (this.buffer.length < offset + 8) return
        const high = this.buffer.readUInt32BE(offset)
        const low = this.buffer.readUInt32BE(offset + 4)
        payloadLength = high * 2 ** 32 + low
        offset += 8
      }

      let maskingKey = null
      if (masked) {
        if (this.buffer.length < offset + 4) return
        maskingKey = this.buffer.slice(offset, offset + 4)
        offset += 4
      }

      if (this.buffer.length < offset + payloadLength) {
        return
      }

      let payload = this.buffer.slice(offset, offset + payloadLength)
      this.buffer = this.buffer.slice(offset + payloadLength)

      if (masked && maskingKey) {
        const unmasked = Buffer.allocUnsafe(payload.length)
        for (let i = 0; i < payload.length; i += 1) {
          unmasked[i] = payload[i] ^ maskingKey[i % 4]
        }
        payload = unmasked
      }

      if (!fin) {
        this.close(1002, 'Fragmented frames not supported')
        return
      }

      switch (opcode) {
        case 0x1: {
          const text = payload.toString('utf8')
          this.messageHandler?.(text)
          break
        }
        case 0x2:
          this.close(1003, 'Binary frames not supported')
          return
        case 0x8:
          this.close()
          return
        case 0x9:
          this.sendFrame(payload, 0xA)
          break
        case 0xA:
          this.isAlive = true
          break
        default:
          this.close(1003, 'Unsupported opcode')
          return
      }
    }
  }

  sendFrame(payload, opcode = 0x1) {
    if (this.isClosed) return

    const data = Buffer.isBuffer(payload) ? payload : Buffer.from(payload)
    const length = data.length
    let header

    if (length < 126) {
      header = Buffer.from([0x80 | opcode, length])
    } else if (length < 65536) {
      header = Buffer.alloc(4)
      header[0] = 0x80 | opcode
      header[1] = 126
      header.writeUInt16BE(length, 2)
    } else {
      header = Buffer.alloc(10)
      header[0] = 0x80 | opcode
      header[1] = 127
      const high = Math.floor(length / 2 ** 32)
      const low = length >>> 0
      header.writeUInt32BE(high, 2)
      header.writeUInt32BE(low, 6)
    }

    this.socket.write(Buffer.concat([header, data]))
  }

  close(code = 1000, reason = '') {
    if (this.isClosed) return
    this.isClosed = true

    try {
      const reasonBuffer = Buffer.from(reason)
      const payload = Buffer.alloc(reason ? reasonBuffer.length + 2 : 2)
      payload.writeUInt16BE(code, 0)
      if (reason) {
        reasonBuffer.copy(payload, 2)
      }
      this.sendFrame(payload, 0x8)
    } catch {
      // Ignore serialization errors
    }

    try {
      this.socket.end()
    } catch {
      this.socket.destroy()
    }

    this.closeHandler?.()
  }

  handleClose() {
    if (this.isClosed) {
      this.closeHandler?.()
      return
    }
    this.isClosed = true
    this.closeHandler?.()
  }
}

const attachDomSnapshotBridge = (httpServer, options) => {
  if (!httpServer) {
    return null
  }

  if (httpServer.__domSnapshotBridgeAttached) {
    return httpServer
  }

  httpServer.__domSnapshotBridgeAttached = true
  setupDomSnapshotBridge(httpServer, options)
  return httpServer
}

export const domSnapshotWebSocketPlugin = (options = {}) => {
  const mergedOptions = {
    path: options.path || DEFAULT_PATH,
    requestTimeout: options.requestTimeout ?? DEFAULT_TIMEOUT_MS
  }

  const desiredPort =
    typeof options.port === 'number' && Number.isFinite(options.port)
      ? options.port
      : undefined
  const desiredHost = options.host

  let standaloneServer = null
  let closeStandalone = null

  return {
    name: 'dom-snapshot-websocket-plugin',
    configureServer(server) {
      const viteHttpServer = server.httpServer
      const serverHost =
        desiredHost || server.config.server?.host || DEFAULT_HOST

      if (desiredPort && desiredPort !== server.config.server?.port) {
        if (!standaloneServer) {
          standaloneServer = createServer((req, res) => {
            res.statusCode = 404
            res.end('Not Found')
          })

          standaloneServer.on('error', (error) => {
            console.error('[DomSnapshotServer] Standalone server error:', error)
          })

          attachDomSnapshotBridge(standaloneServer, mergedOptions)

          standaloneServer.listen(desiredPort, serverHost, () => {
            console.log(
              `[DomSnapshotServer] Listening on ws://${serverHost}:${desiredPort}${mergedOptions.path}`
            )
          })

          closeStandalone = () => {
            if (!standaloneServer) return
            standaloneServer.close(() => {
              console.log('[DomSnapshotServer] Standalone server closed')
            })
            standaloneServer = null
          }

          if (viteHttpServer) {
            viteHttpServer.once('close', () => {
              closeStandalone?.()
            })
          }
        }
        return
      }

      attachDomSnapshotBridge(viteHttpServer, mergedOptions)
    },
    async closeBundle() {
      closeStandalone?.()
    }
  }
}

const setupDomSnapshotBridge = (httpServer, options) => {
  const path = options.path || DEFAULT_PATH
  const requestTimeout = options.requestTimeout ?? DEFAULT_TIMEOUT_MS

  const clients = new Set()
  const frontends = new Set()
  const backends = new Set()
  const pendingRequests = new Map()

  const cleanupPendingRequests = (connection) => {
    for (const [requestId, pending] of pendingRequests.entries()) {
      if (pending.backend === connection) {
        clearTimeout(pending.timeout)
        pendingRequests.delete(requestId)
      } else if (pending.frontend === connection) {
        clearTimeout(pending.timeout)
        pendingRequests.delete(requestId)
        if (!pending.backend.isClosed) {
          pending.backend.sendJson({
            type: 'dom_snapshot_error',
            requestId,
            error: 'frontend_disconnected'
          })
        }
      }
    }
  }

  const broadcastStatus = () => {
    const payload = {
      type: 'status',
      timestamp: Date.now(),
      frontendCount: frontends.size,
      backendCount: backends.size
    }
    for (const client of clients) {
      client.sendJson(payload)
    }
  }

  const resolveFrontendTarget = (preferredId) => {
    if (preferredId) {
      for (const client of frontends) {
        if (client.id === preferredId) {
          return client
        }
      }
    }
    const iterator = frontends.values()
    return iterator.next().value
  }

  const handleDomSnapshotRequest = (backend, message) => {
    const target = resolveFrontendTarget(message.targetClientId)
    if (!target) {
      backend.sendJson({
        type: 'dom_snapshot_error',
        requestId: message.requestId || null,
        error: 'no_frontend_connected'
      })
      return
    }

    const requestId = message.requestId || createRequestId()
    if (pendingRequests.has(requestId)) {
      backend.sendJson({
        type: 'dom_snapshot_error',
        requestId,
        error: 'duplicate_request_id'
      })
      return
    }

    const timeout = setTimeout(() => {
      pendingRequests.delete(requestId)
      if (!backend.isClosed) {
        backend.sendJson({
          type: 'dom_snapshot_error',
          requestId,
          error: 'frontend_timeout'
        })
      }
    }, requestTimeout)

    pendingRequests.set(requestId, {
      backend,
      frontend: target,
      timeout
    })

    target.sendJson({
      type: 'dom_snapshot_request',
      requestId,
      metadata: message.metadata || null
    })
  }

  const handleDomSnapshotResponse = (frontend, message) => {
    const requestId = message.requestId
    if (!requestId || !pendingRequests.has(requestId)) {
      return
    }

    const pending = pendingRequests.get(requestId)
    if (pending.frontend !== frontend) {
      return
    }

    pendingRequests.delete(requestId)
    clearTimeout(pending.timeout)

    if (!pending.backend.isClosed) {
      pending.backend.sendJson({
        type: 'dom_snapshot_response',
        requestId,
        snapshot: message.snapshot || null,
        error: message.error || null,
        timestamp: message.timestamp || Date.now()
      })
    }
  }

  const handleTtsBroadcast = (backend, message) => {
    const target = resolveFrontendTarget(message.targetClientId)
    const requestId = message.requestId || createRequestId()

    if (!target) {
      backend.sendJson({
        type: 'tts_ack',
        requestId,
        delivered: false,
        error: 'no_frontend_connected'
      })
      return
    }

    target.sendJson({
      type: 'tts_speak',
      requestId,
      text: message.text || '',
      sessionId: message.sessionId || null,
      stepId: message.stepId || null,
      metadata: message.metadata || null,
      timestamp: Date.now()
    })

    backend.sendJson({
      type: 'tts_ack',
      requestId,
      delivered: true,
      targetClientId: target.id
    })
  }

  const handleRegister = (connection, message) => {
    if (message.role !== 'frontend' && message.role !== 'backend') {
      connection.sendJson({ type: 'error', error: 'invalid_role' })
      return
    }

    frontends.delete(connection)
    backends.delete(connection)

    if (message.role === 'frontend') {
      frontends.add(connection)
      connection.role = 'frontend'
    } else {
      backends.add(connection)
      connection.role = 'backend'
    }

    connection.sendJson({
      type: 'register_ack',
      role: connection.role,
      clientId: connection.id
    })

    broadcastStatus()
  }

  const handleMessage = (connection, raw) => {
    let message
    try {
      message = JSON.parse(raw)
    } catch (error) {
      connection.sendJson({ type: 'error', error: 'invalid_json' })
      return
    }

    switch (message.type) {
      case 'register':
        handleRegister(connection, message)
        break
      case 'get_dom_snapshot':
        if (connection.role !== 'backend') {
          connection.sendJson({ type: 'error', error: 'unauthorized' })
          break
        }
        handleDomSnapshotRequest(connection, message)
        break
      case 'dom_snapshot_response':
        if (connection.role === 'frontend') {
          handleDomSnapshotResponse(connection, message)
        }
        break
      case 'tts_broadcast':
        if (connection.role !== 'backend') {
          connection.sendJson({ type: 'error', error: 'unauthorized' })
          break
        }
        handleTtsBroadcast(connection, message)
        break
      case 'pong':
        connection.isAlive = true
        break
      default:
        connection.sendJson({ type: 'error', error: 'unknown_message_type' })
        break
    }
  }

  httpServer.on('upgrade', (request, socket, head) => {
    const requestPath = (request.url || '').split('?')[0]
    if (requestPath !== path) {
      return
    }

    if (request.headers?.upgrade?.toLowerCase() !== 'websocket') {
      socket.destroy()
      return
    }

    const webSocketKey = request.headers['sec-websocket-key']
    if (!webSocketKey) {
      socket.write('HTTP/1.1 400 Bad Request\r\n\r\n')
      socket.destroy()
      return
    }

    const acceptKey = createHash('sha1')
      .update(webSocketKey + HANDSHAKE_GUID)
      .digest('base64')

    const protocols = request.headers['sec-websocket-protocol']
    const responseHeaders = [
      'HTTP/1.1 101 Switching Protocols',
      'Upgrade: websocket',
      'Connection: Upgrade',
      `Sec-WebSocket-Accept: ${acceptKey}`
    ]

    if (protocols) {
      const selected = protocols
        .split(',')
        .map((entry) => entry.trim())
        .find(Boolean)
      if (selected) {
        responseHeaders.push(`Sec-WebSocket-Protocol: ${selected}`)
      }
    }

    socket.write(responseHeaders.join('\r\n') + '\r\n\r\n')

    const connection = new RawWebSocketConnection(socket)
    clients.add(connection)

    connection.onClose(() => {
      clients.delete(connection)
      frontends.delete(connection)
      backends.delete(connection)
      cleanupPendingRequests(connection)
      broadcastStatus()
    })

    connection.onMessage((raw) => handleMessage(connection, raw))

    if (head && head.length) {
      connection.handleData(head)
    }

    broadcastStatus()
  })
}


