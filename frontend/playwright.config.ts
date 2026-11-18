import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for E2E tests.
 * Starts backend (migrate, seed, uvicorn) and frontend dev server.
 * Uses free ports from E2E_BACKEND_PORT and E2E_FRONTEND_PORT env vars.
 */

const backendPort = process.env.E2E_BACKEND_PORT ?? '9001';
const frontendPort = process.env.E2E_FRONTEND_PORT ?? '5174';
const pythonCmd = process.env.E2E_PYTHON ?? 'python';
const databaseUrl = process.env.E2E_DATABASE_URL ?? 'sqlite:///./e2e_test.db';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'html',
  
  timeout: Number(process.env.E2E_TEST_TIMEOUT ?? 30_000),
  
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    trace: 'on-first-retry',
    actionTimeout: Number(process.env.E2E_ACTION_TIMEOUT ?? 10_000),
    navigationTimeout: Number(process.env.E2E_NAVIGATION_TIMEOUT ?? 15_000),
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: [
    {
      // Backend: migrate, seed, start uvicorn
      command: `cd ../backend && ${pythonCmd} -m alembic upgrade head && SEED_DATA=true ${pythonCmd} -m app.seed && ${pythonCmd} -m uvicorn app.main:app --host 127.0.0.1 --port ${backendPort}`,
      port: Number(backendPort),
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'pipe',
      stderr: 'pipe',
      env: {
        DATABASE_URL: databaseUrl,
      },
    },
    {
      // Frontend: vite dev server with proxy to backend
      command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
      port: Number(frontendPort),
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'pipe',
      stderr: 'pipe',
      env: {
        BACKEND_PORT: backendPort,
      },
    },
  ],
});
