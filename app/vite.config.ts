/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

// Duas páginas (ADR 0011):
// - captura.html: página do celular, publicada na Vercel
// - escritorio.html: aplicação do escritório, servida pelo motor local
// PAGINA=captura gera só a página do celular (para a Vercel), sem a aplicação do escritório.
const paginas = {
  captura: resolve(__dirname, 'captura.html'),
  escritorio: resolve(__dirname, 'escritorio.html'),
};
const so = process.env.PAGINA as keyof typeof paginas | undefined;

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: so ? `dist-${so}` : 'dist',
    rollupOptions: { input: so ? { [so]: paginas[so] } : paginas },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/teste-setup.ts'],
  },
});
