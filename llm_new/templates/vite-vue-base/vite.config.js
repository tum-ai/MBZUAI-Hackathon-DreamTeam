import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    server: {
        port: process.env.VITE_PORT || 3000,
        cors: true,
        strictPort: false,
        hmr: {
            overlay: false
        }
    }
})
