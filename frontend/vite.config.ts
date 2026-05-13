import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  preview: {
    host: '0.0.0.0', // Accessible to everyone on the local network
    port: 4173,
    strictPort: true,
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
})
