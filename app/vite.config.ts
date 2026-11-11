/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

// Duas páginas (ADR 0011):
// - captura.html: página do celular, publicada na Vercel
// - escritorio.html: aplicação do escritório, servida pelo motor local
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        captura: resolve(__dirname, 'captura.html'),
        escritorio: resolve(__dirname, 'escritorio.html'),
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/teste-setup.ts'],
  },
});
