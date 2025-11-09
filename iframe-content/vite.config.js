import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const rawPort = env.IFRAME_PORT
  const rawHost = env.IFRAME_HOST

  const port =
    rawPort && rawPort !== '' && !Number.isNaN(Number(rawPort))
      ? Number(rawPort)
      : 5174

  return {
    plugins: [vue()],
    server: {
      host: rawHost || '0.0.0.0',
      port
    }
  }
})

