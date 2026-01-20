import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const ragProxyTarget = process.env.RAG_API_PROXY ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/contacts': 'http://localhost:3001',
      '/auth': 'http://localhost:3001',
      '/rag': {
        target: ragProxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/rag/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
