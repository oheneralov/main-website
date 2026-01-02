import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/contacts': 'http://localhost:3001',
      '/auth': 'http://localhost:3001',
    },
  },
  build: {
    outDir: path.join(__dirname, '../public/dist'),
    emptyOutDir: true,
  },
});
