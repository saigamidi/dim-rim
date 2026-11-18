/**
 * E2E test: Navigation across all routes
 * Visits every route declared in the router and verifies content renders.
 */

import { test, expect } from './_pipeline_guard';
import { loginAndSetToken } from './test-helpers';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndSetToken(page);
  });

  test('should display Intake Cases page at root', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });

  test('should display Intake Cases page at /intake', async ({ page }) => {
    await page.goto('/intake');
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });

  test('should redirect /classification to /intake', async ({ page }) => {
    await page.goto('/classification');
    await page.waitForURL(/\/intake/, { timeout: 10000 });
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });

  test('should redirect /vin-review to /intake', async ({ page }) => {
    await page.goto('/vin-review');
    await page.waitForURL(/\/intake/, { timeout: 10000 });
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });

  test('should redirect /audit to /intake', async ({ page }) => {
    await page.goto('/audit');
    await page.waitForURL(/\/intake/, { timeout: 10000 });
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });

  test('should redirect unknown paths to root', async ({ page }) => {
    await page.goto('/nonexistent-path');
    await page.waitForURL(/\/$/, { timeout: 10000 });
    await expect(page.locator('h1').filter({ hasText: 'Intake Cases' })).toBeVisible();
  });
});
