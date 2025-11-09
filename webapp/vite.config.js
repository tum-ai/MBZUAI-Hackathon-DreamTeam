import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { domSnapshotWebSocketPlugin } from './server/domSnapshotWebSocketPlugin.js'

const resolveDomSnapshotOptions = () => {
  const options = {}
  const {
    DOM_SNAPSHOT_WS_PATH,
    DOM_SNAPSHOT_WS_PORT,
    DOM_SNAPSHOT_WS_HOST,
    DOM_SNAPSHOT_WS_TIMEOUT_MS
  } = process.env

  if (DOM_SNAPSHOT_WS_PATH) {
    options.path = DOM_SNAPSHOT_WS_PATH
  }

  if (DOM_SNAPSHOT_WS_PORT && DOM_SNAPSHOT_WS_PORT !== '') {
    const parsedPort = Number(DOM_SNAPSHOT_WS_PORT)
    if (!Number.isNaN(parsedPort)) {
      options.port = parsedPort
    }
  }

  if (DOM_SNAPSHOT_WS_HOST) {
    options.host = DOM_SNAPSHOT_WS_HOST
  }

  if (DOM_SNAPSHOT_WS_TIMEOUT_MS && DOM_SNAPSHOT_WS_TIMEOUT_MS !== '') {
    const parsedTimeout = Number(DOM_SNAPSHOT_WS_TIMEOUT_MS)
    if (!Number.isNaN(parsedTimeout)) {
      options.requestTimeout = parsedTimeout
    }
  }

  return options
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    domSnapshotWebSocketPlugin(resolveDomSnapshotOptions())
  ],
  server: {
    port: 5173,
    open: true
  }
})

