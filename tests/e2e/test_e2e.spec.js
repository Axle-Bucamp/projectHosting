import { test, expect } from '@playwright/test';

test.describe('ProjectHosting E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(process.env.BASE_URL || 'http://localhost:3000');
  });

  test.describe('Frontend Application', () => {
    test('should load homepage successfully', async ({ page }) => {
      await expect(page).toHaveTitle(/ProjectHosting/);
      await expect(page.locator('h1')).toContainText('Welcome');
    });

    test('should navigate between pages', async ({ page }) => {
      // Test navigation to Projects page
      await page.click('a[href="/projects"]');
      await expect(page).toHaveURL(/.*projects/);
      await expect(page.locator('h1')).toContainText('Projects');

      // Test navigation to Store page
      await page.click('a[href="/store"]');
      await expect(page).toHaveURL(/.*store/);
      await expect(page.locator('h1')).toContainText('Store');

      // Test navigation back to Home
      await page.click('a[href="/"]');
      await expect(page).toHaveURL(/.*\//);
    });

    test('should display projects list', async ({ page }) => {
      await page.goto('/projects');
      
      // Wait for projects to load
      await page.waitForSelector('[data-testid="projects-list"]', { timeout: 10000 });
      
      // Check if projects are displayed
      const projectCards = page.locator('[data-testid="project-card"]');
      const count = await projectCards.count();
      
      if (count > 0) {
        // If projects exist, verify they have required elements
        await expect(projectCards.first()).toContainText(/.*/)
        await expect(projectCards.first().locator('.status-badge')).toBeVisible();
      }
    });

    test('should display store items', async ({ page }) => {
      await page.goto('/store');
      
      // Wait for store items to load
      await page.waitForSelector('[data-testid="store-grid"]', { timeout: 10000 });
      
      // Check if store items are displayed
      const storeItems = page.locator('[data-testid="store-item"]');
      const count = await storeItems.count();
      
      if (count > 0) {
        // If items exist, verify they have required elements
        await expect(storeItems.first()).toContainText(/.*/)
        await expect(storeItems.first().locator('.price')).toBeVisible();
      }
    });

    test('should submit contact form', async ({ page }) => {
      await page.goto('/');
      
      // Scroll to contact form
      await page.locator('#contact-form').scrollIntoViewIfNeeded();
      
      // Fill out contact form
      await page.fill('input[name="name"]', 'Test User');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="subject"]', 'Test Subject');
      await page.fill('textarea[name="message"]', 'This is a test message from E2E tests.');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Wait for success message
      await expect(page.locator('.success-message')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.success-message')).toContainText('Thank you');
    });
  });

  test.describe('Admin Interface', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to admin interface
      await page.goto('/admin');
    });

    test('should require authentication', async ({ page }) => {
      // Should redirect to login or show login form
      await expect(page.locator('input[name="username"]')).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
    });

    test('should login with valid credentials', async ({ page }) => {
      // Fill login form
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      
      // Submit login
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('h1')).toContainText('Dashboard');
    });

    test('should display dashboard metrics', async ({ page }) => {
      // Login first
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      
      // Wait for dashboard to load
      await page.waitForSelector('[data-testid="metrics-grid"]', { timeout: 10000 });
      
      // Check for metric cards
      const metricCards = page.locator('[data-testid="metric-card"]');
      await expect(metricCards).toHaveCountGreaterThan(0);
      
      // Verify metric cards have values
      await expect(metricCards.first().locator('.metric-value')).toContainText(/\d+/);
    });

    test('should manage projects', async ({ page }) => {
      // Login
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      
      // Navigate to projects management
      await page.click('a[href="/admin/projects"]');
      await expect(page).toHaveURL(/.*projects/);
      
      // Test creating a new project
      await page.click('button:has-text("Add Project")');
      
      // Fill project form
      await page.fill('input[name="name"]', 'E2E Test Project');
      await page.fill('textarea[name="description"]', 'Project created by E2E tests');
      await page.fill('input[name="url"]', 'https://e2e-test.example.com');
      await page.selectOption('select[name="status"]', 'online');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Verify project was created
      await expect(page.locator('text=E2E Test Project')).toBeVisible();
    });

    test('should view system logs', async ({ page }) => {
      // Login
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      
      // Navigate to logs
      await page.click('a[href="/admin/logs"]');
      await expect(page).toHaveURL(/.*logs/);
      
      // Wait for logs to load
      await page.waitForSelector('[data-testid="logs-table"]', { timeout: 10000 });
      
      // Check if logs are displayed
      const logRows = page.locator('[data-testid="log-row"]');
      const count = await logRows.count();
      
      if (count > 0) {
        // Verify log entries have required fields
        await expect(logRows.first().locator('.timestamp')).toBeVisible();
        await expect(logRows.first().locator('.level')).toBeVisible();
        await expect(logRows.first().locator('.message')).toBeVisible();
      }
      
      // Test log filtering
      await page.fill('input[placeholder="Search logs..."]', 'health');
      await page.keyboard.press('Enter');
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
    });

    test('should manage settings', async ({ page }) => {
      // Login
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      
      // Navigate to settings
      await page.click('a[href="/admin/settings"]');
      await expect(page).toHaveURL(/.*settings/);
      
      // Test updating application settings
      await page.fill('input[name="app_name"]', 'E2E Test App');
      await page.fill('textarea[name="app_description"]', 'Updated by E2E tests');
      
      // Save settings
      await page.click('button:has-text("Save Settings")');
      
      // Verify success message
      await expect(page.locator('.success-message')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('API Health Checks', () => {
    test('should have healthy backend API', async ({ request }) => {
      const response = await request.get('/api/health');
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.status).toBe('healthy');
    });

    test('should have healthy bridge service', async ({ request }) => {
      const response = await request.get('/api/bridge/health');
      expect(response.status()).toBe(200);
    });

    test('should have metrics endpoint', async ({ request }) => {
      const response = await request.get('/metrics');
      expect(response.status()).toBe(200);
      
      const text = await response.text();
      expect(text).toContain('http_requests_total');
    });
  });

  test.describe('Performance Tests', () => {
    test('should load homepage within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000); // 5 seconds max
    });

    test('should handle multiple concurrent users', async ({ browser }) => {
      const contexts = await Promise.all([
        browser.newContext(),
        browser.newContext(),
        browser.newContext()
      ]);
      
      const pages = await Promise.all(
        contexts.map(context => context.newPage())
      );
      
      // Navigate all pages simultaneously
      await Promise.all(
        pages.map(page => page.goto('/'))
      );
      
      // Verify all pages loaded successfully
      for (const page of pages) {
        await expect(page.locator('h1')).toBeVisible();
      }
      
      // Cleanup
      await Promise.all(contexts.map(context => context.close()));
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should work on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.goto('/');
      
      // Check mobile navigation
      const mobileMenu = page.locator('[data-testid="mobile-menu-button"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      }
      
      // Test responsive layout
      await expect(page.locator('main')).toBeVisible();
      
      // Test touch interactions
      await page.goto('/projects');
      const projectCard = page.locator('[data-testid="project-card"]').first();
      if (await projectCard.isVisible()) {
        await projectCard.tap();
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should meet basic accessibility requirements', async ({ page }) => {
      await page.goto('/');
      
      // Check for proper heading structure
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check for alt text on images
      const images = page.locator('img');
      const imageCount = await images.count();
      
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        expect(alt).toBeTruthy();
      }
      
      // Check for form labels
      const inputs = page.locator('input[type="text"], input[type="email"], textarea');
      const inputCount = await inputs.count();
      
      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const id = await input.getAttribute('id');
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          await expect(label).toBeVisible();
        }
      }
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.goto('/');
      
      // Test tab navigation
      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();
      
      // Test Enter key on buttons
      const button = page.locator('button').first();
      if (await button.isVisible()) {
        await button.focus();
        await page.keyboard.press('Enter');
      }
    });
  });
});

