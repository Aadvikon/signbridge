import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    historyApiFallback: true,
    middleware: true
  },
  optimizeDeps: {
    include: ['hls.js']
  },
  root: '.'
})