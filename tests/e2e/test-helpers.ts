/**
 * Test helpers for E2E tests
 */

import type { Page } from '@playwright/test';

export async function loginAndSetToken(page: Page, email: string = 'disruption.mgr@tmna.com', password: string = 'Manager123!'): Promise<string> {
  const backendPort = process.env.BACKEND_PORT || '9420';
  const frontendPort = process.env.FRONTEND_PORT || '5220';
  
  const response = await page.request.post(`http://127.0.0.1:${backendPort}/api/v1/auth/login`, {
    data: { email, password }
  });
  const { access_token } = await response.json();
  
  // Navigate to login page first to establish context
  await page.goto(`http://127.0.0.1:${frontendPort}/login`);
  
  // Set token in localStorage
  await page.evaluate((token) => {
    localStorage.setItem('access_token', token);
  }, access_token);
  
  return access_token;
}
