import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load all env vars ('' prefix) including BACKEND_PORT from shell
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        // Forward /api to backend without path rewrite
        '/api': {
          target: `http://127.0.0.1:${env.BACKEND_PORT || '9000'}`,
          changeOrigin: true,
        },
      },
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
      exclude: ['**/node_modules/**', '**/e2e/**'],
    },
  };
});
