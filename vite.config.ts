import { defineConfig } from 'vite'

export default defineConfig({
  // GitHub Pages project site: https://plicerin.github.io/Swords-and-Serpents/
  base: process.env.GITHUB_ACTIONS ? '/Swords-and-Serpents/' : '/',
  server: {
    port: 4040
  },
  build: {
    target: 'es2020'
  }
})
