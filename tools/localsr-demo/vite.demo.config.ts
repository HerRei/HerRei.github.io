import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// The browser demo: the real interface with a scripted host, built for a
// static site folder (relative paths, ES modules).
export default defineConfig({
  base: './',
  plugins: [svelte()],
  build: {
    outDir: 'dist-demo',
    emptyOutDir: true,
    target: 'es2020',
    rollupOptions: { input: 'tour.html' },
  },
});
