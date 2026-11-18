/**
 * E2E test: Login flow through the form
 * This test MUST go through the actual form submission, not just API calls.
 */

import { test, expect } from './_pipeline_guard';

test.describe('Authentication', () => {
  test('should login through the form and access protected pages', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Verify we're on the login page
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator('h1').filter({ hasText: 'Disruption Manager RIM' })).toBeVisible();
    
    // Fill in the login form with seed credentials
    await page.fill('input[type="email"], input[name="email"]', 'disruption.mgr@tmna.com');
    await page.fill('input[type="password"], input[name="password"]', 'Manager123!');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for navigation away from login page
    await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 });
    
    // Verify we're now on a protected page (Intake Cases)
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible({ timeout: 10000 });
  });

  test('should reject invalid credentials', async ({ page, apiGuard }) => {
    // Allow 401 for this specific test
    apiGuard.allow(401, '/api/v1/auth/login');
    
    await page.goto('/login');
    
    await page.fill('input[type="email"], input[name="email"]', 'wrong@example.com');
    await page.fill('input[type="password"], input[name="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Should stay on login page - the login should not succeed
    await page.waitForTimeout(2000);  // Wait for any redirect attempt
    await expect(page).toHaveURL(/\/login/);
    
    // Verify the Sign in button is still there (didn't navigate away)
    await expect(page.locator('button:has-text("Sign in")')).toBeVisible();
  });

  test('should logout and redirect to login', async ({ page }) => {
    const backendPort = process.env.BACKEND_PORT || '9420';
    
    // First login via API to save time
    const response = await page.request.post(`http://127.0.0.1:${backendPort}/api/v1/auth/login`, {
      data: {
        email: 'disruption.mgr@tmna.com',
        password: 'Manager123!'
      }
    });
    const { access_token } = await response.json();
    
    // Navigate to a page first, then set token
    await page.goto('/login');
    
    // Set token in localStorage
    await page.evaluate((token) => {
      localStorage.setItem('access_token', token);
    }, access_token);
    
    // Navigate to protected page
    await page.goto('/');
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible({ timeout: 15000 });
    
    // Find and click logout button
    await page.click('button:has-text("Sign out")');
    
    // Should redirect to login
    await page.waitForURL(/\/login/, { timeout: 5000 });
    await expect(page.locator('h1').filter({ hasText: 'Disruption Manager RIM' })).toBeVisible();
  });
});
