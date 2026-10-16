import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
    server: {
    port: 3000,
    open: false,
    proxy: {
      // Flask API - 所有请求统一代理到 localhost:5001
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/videos': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/init-isolated': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => `/api${path}`
      },
      '/predict-isolated': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => `/api${path}`
      },
      '/predict-isolated-webcam': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => `/api${path}`
      },
      '/predict-isolated-jpg': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => `/api${path}`
      },
      '/vocabulary': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => `/api${path}`
      }
    }
  }
})
