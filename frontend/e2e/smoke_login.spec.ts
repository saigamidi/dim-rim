import { test, expect } from './_pipeline_guard';

/**
 * Smoke test: Login through the form and assert successful redirect.
 * Uses seed credentials from backend Task 1.
 */

test.describe('Smoke Login', () => {
  test('should login with seed credentials and redirect to homepage', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Verify login form is visible
    await expect(page.getByRole('heading', { name: /Disruption Manager RIM/i })).toBeVisible();
    await expect(page.locator('input#email')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();

    // Fill in seed credentials (Disruption Manager)
    await page.locator('input#email').fill('disruption.mgr@tmna.com');
    await page.locator('input#password').fill('Manager123!');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for navigation and assert redirect to homepage
    await page.waitForURL(/.*\/$|.*\/\?/);
    await expect(page).toHaveURL(/.*\/$/); // Ends with /

    // Verify authenticated content is visible (placeholder homepage text)
    await expect(page.getByText(/Infrastructure ready/i)).toBeVisible();
  });

  test('should remain on login page for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill in invalid credentials
    await page.locator('input#email').fill('invalid@example.com');
    await page.locator('input#password').fill('wrongpassword');

    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait a moment for any potential navigation
    await page.waitForTimeout(1000);

    // Verify we're still on the login page (not redirected)
    await expect(page).toHaveURL(/.*\/login$/);
  });
});
