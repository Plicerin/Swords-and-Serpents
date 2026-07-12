import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 4040
  },
  build: {
    target: 'es2020'
  }
})
