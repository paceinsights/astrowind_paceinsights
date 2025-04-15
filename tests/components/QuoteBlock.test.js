import { test, expect } from '@astrojs/test/playwright';

// Basic rendering test for QuoteBlock
// Note: This test assumes you have @astrojs/test and Playwright set up.
test.describe('QuoteBlock component', () => {
  test('renders quote and attribution', async ({ page }) => {
    await page.goto('/'); // homepage where QuoteBlock is used
    const quote = await page.locator('blockquote').textContent();
    const attribution = await page.locator('figcaption').textContent();
    expect(quote).toContain("No new headcount unless you can justify why the work CAN'T be done by AI Agents.");
    expect(attribution).toContain('Tobi Lütke');
  });

  test('is accessible', async ({ page }) => {
    await page.goto('/');
    // Check for semantic HTML
    await expect(page.locator('blockquote')).toBeVisible();
    await expect(page.locator('figcaption')).toBeVisible();
  });
});
