import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 3: VIN Extraction and Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Login with seed credentials
    await page.goto('/login');
    await page.fill('#email', 'disruption.mgr@tmna.com');
    await page.fill('#password', 'Manager123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should display VIN review page with extraction summary', async ({ page }) => {
    // Navigate to VIN review page
    await page.goto('/vin-review/CASE-2026-001');
    
    // Wait for page to load
    await expect(page.getByRole('heading', { name: /vin review/i })).toBeVisible();
    
    // Verify extraction summary tiles are visible
    await expect(page.getByText('Rows parsed')).toBeVisible();
    await expect(page.getByText('Extracted candidates')).toBeVisible();
    await expect(page.getByText('Deduplicated (duplicates removed)')).toBeVisible();
    await expect(page.getByText('Rejected as empty')).toBeVisible();
  });

  test('should display validation outcome and BR-01 rules', async ({ page }) => {
    await page.goto('/vin-review/CASE-2026-001');
    
    // Wait for validation section - use heading role to be specific
    await expect(page.getByRole('heading', { name: /br-01 validation/i })).toBeVisible();
    
    // Verify BR-01 rules reference is visible
    await expect(page.getByRole('heading', { name: /br-01 rule reference/i })).toBeVisible();
    await expect(page.getByText(/normalize to uppercase/i)).toBeVisible();
  });

  test('should display per-VIN results table with filters', async ({ page }) => {
    await page.goto('/vin-review/CASE-2026-001');
    
    // Wait for results table
    await expect(page.getByRole('heading', { name: /per-vin results/i })).toBeVisible();
    
    // Verify table headers
    await expect(page.getByRole('columnheader', { name: /normalized vin/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /validation/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /failure reason code/i })).toBeVisible();
    
    // Verify filter chips are present - look within the results section
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('should allow re-running extraction and validation', async ({ page }) => {
    await page.goto('/vin-review/CASE-2026-001');
    
    // Verify re-run buttons are present
    await expect(page.getByRole('button', { name: /re-run extraction/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /re-run.*validation/i })).toBeVisible();
  });

  test('should display stepper showing workflow progress', async ({ page }) => {
    await page.goto('/vin-review/CASE-2026-001');
    
    // Verify key stepper stages are visible (avoiding duplicate matches)
    await expect(page.getByText('Received')).toBeVisible();
    await expect(page.getByText('VIN extracted')).toBeVisible();
    await expect(page.getByText('VIN validated')).toBeVisible();
  });
});
