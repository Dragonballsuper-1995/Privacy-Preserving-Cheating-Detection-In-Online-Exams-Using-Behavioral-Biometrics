import { test, expect, Page } from '@playwright/test';

test.describe('E2E Cheater Simulations', () => {

    const navigateToExam = async (page: Page) => {
        await page.goto('/');

        try {
            await expect(page.locator('text=INITIATE_SEQUENCE').first()).toBeVisible({ timeout: 5000 });
        } catch (e) {
            console.error('INITIATE_SEQUENCE not found. Page text:', await page.content());
            await page.screenshot({ path: 'frontend-error-state.png' });
            throw e;
        }

        // Click the first exam's "INITIATE_SEQUENCE" button
        await page.locator('text=INITIATE_SEQUENCE').first().click();

        // Wait for the Pre-exam start screen
        await expect(page.locator('text=INITIATE_PROTOCOL')).toBeVisible();

        // Start the exam
        await page.locator('text=INITIATE_PROTOCOL').click();

        // Wait for the exam UI to load
        await expect(page.locator('text=NODE_ID:')).toBeVisible();
    };

    const getSessionId = async (page: Page) => {
        // Session ID is not natively exposed in the UI right now, but we don't necessarily need it to assert the cheat,
        // Alternatively, we can intercept the POST /api/events/log or /api/sessions/:id
        let sessionId = null;
        page.on('request', (request: any) => {
            if (request.url().includes('/api/events/log')) {
                const postData = request.postDataJSON();
                if (postData && postData.session_id) {
                    sessionId = postData.session_id;
                }
            }
        });
        return sessionId;
    };

    test('The Copy-Paster: triggers high paste score', async ({ page }) => {
        await navigateToExam(page);

        // Find a textarea (assuming the first question is a coding question or has a textarea)
        const editor = page.locator('textarea').first();
        await editor.waitFor({ state: 'visible' });

        // Focus and clear
        await editor.click();
        await editor.fill('');

        // Simulate pasting a large block of code
        const largeCodeBlock = `
      function calculateFibonacci(n) {
          if (n <= 1) return n;
          return calculateFibonacci(n - 1) + calculateFibonacci(n - 2);
      }
      console.log(calculateFibonacci(10));
    `.repeat(5);

        // Playwright page.fill doesn't trigger 'paste' event, so we dispatch it manually
        await editor.evaluate((node, text) => {
            const pasteEvent = new ClipboardEvent('paste', {
                clipboardData: new DataTransfer()
            });
            if (pasteEvent.clipboardData) {
                pasteEvent.clipboardData.setData('text/plain', text);
            }
            node.dispatchEvent(pasteEvent);
            // Also update the value so React picks it up
            (node as HTMLTextAreaElement).value = text;
            node.dispatchEvent(new Event('input', { bubbles: true }));
        }, largeCodeBlock);

        // Wait a bit to ensure event is batched
        await page.waitForTimeout(2000);

        // Submit the exam
        await page.locator('text=FINAL_TRANSMIT').click();
        await expect(page.locator('text=CONFIRM_TRANSMIT')).toBeVisible();
        await page.locator('button', { hasText: 'TRANSMIT' }).click();

        // Verify successful submission
        await expect(page.locator('text=TRANSMISSION_COMPLETE')).toBeVisible();
    });

    test('The Collaborator: types irregularly with unnatural pauses', async ({ page }) => {
        await navigateToExam(page);

        const editor = page.locator('textarea').first();
        await editor.waitFor({ state: 'visible' });
        await editor.click();

        // Type with long pauses
        const chunks = ['function ', 'foo() ', '{ ', 'return ', 'true; ', '}'];
        for (const chunk of chunks) {
            await editor.type(chunk, { delay: 50 });
            // Pause for 4 seconds to simulate taking advice/looking at another screen
            await page.waitForTimeout(4000);
        }

        await page.locator('text=FINAL_TRANSMIT').click();
        await expect(page.locator('text=CONFIRM_TRANSMIT')).toBeVisible();
        await page.locator('button', { hasText: 'TRANSMIT' }).click();
        await expect(page.locator('text=TRANSMISSION_COMPLETE')).toBeVisible();
    });

    test('The Searcher: frequently blurs the window to check external resources', async ({ page }) => {
        await navigateToExam(page);

        await page.waitForTimeout(1000);

        // Simulate window blur/focus multiple times
        for (let i = 0; i < 5; i++) {
            // Dispatch blur on window
            await page.evaluate(() => window.dispatchEvent(new Event('blur')));
            await page.waitForTimeout(2000); // stay away for 2 seconds

            // Dispatch focus on window
            await page.evaluate(() => window.dispatchEvent(new Event('focus')));
            await page.waitForTimeout(1000); // came back
        }

        await page.locator('text=FINAL_TRANSMIT').click();
        await expect(page.locator('text=CONFIRM_TRANSMIT')).toBeVisible();
        await page.locator('button', { hasText: 'TRANSMIT' }).click();
        await expect(page.locator('text=TRANSMISSION_COMPLETE')).toBeVisible();
    });

});
