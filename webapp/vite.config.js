import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { domSnapshotWebSocketPlugin } from './server/domSnapshotWebSocketPlugin.js'

const parseNumber = (value, fallback) => {
  if (value === undefined || value === null || value === '') {
    return fallback
  }
  const parsed = Number(value)
  return Number.isNaN(parsed) ? fallback : parsed
}

const parseBoolean = (value, fallback) => {
  if (value === undefined || value === null || value === '') {
    return fallback
  }
  return value === 'true'
}

const resolveDomSnapshotOptions = (env) => {
  const options = {}

  const DOM_SNAPSHOT_WS_PATH = env.DOM_SNAPSHOT_WS_PATH
  const DOM_SNAPSHOT_WS_PORT = env.DOM_SNAPSHOT_WS_PORT
  const DOM_SNAPSHOT_WS_HOST = env.DOM_SNAPSHOT_WS_HOST
  const DOM_SNAPSHOT_WS_TIMEOUT_MS = env.DOM_SNAPSHOT_WS_TIMEOUT_MS

  if (DOM_SNAPSHOT_WS_PATH) {
    options.path = DOM_SNAPSHOT_WS_PATH
  }

  if (DOM_SNAPSHOT_WS_PORT && DOM_SNAPSHOT_WS_PORT !== '') {
    options.port = parseNumber(DOM_SNAPSHOT_WS_PORT, undefined)
  }

  if (DOM_SNAPSHOT_WS_HOST) {
    options.host = DOM_SNAPSHOT_WS_HOST
  }

  if (DOM_SNAPSHOT_WS_TIMEOUT_MS && DOM_SNAPSHOT_WS_TIMEOUT_MS !== '') {
    options.requestTimeout = parseNumber(
      DOM_SNAPSHOT_WS_TIMEOUT_MS,
      undefined
    )
  }

  return options
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const serverPort = parseNumber(env.WEBAPP_PORT, 5173)
  const serverHost = env.WEBAPP_HOST || '0.0.0.0'
  const openBrowser = parseBoolean(env.WEBAPP_OPEN_BROWSER, true)

  return {
    plugins: [
      react(),
      domSnapshotWebSocketPlugin(resolveDomSnapshotOptions(env))
    ],
    server: {
      host: serverHost,
      port: serverPort,
      open: openBrowser
    }
  }
})

