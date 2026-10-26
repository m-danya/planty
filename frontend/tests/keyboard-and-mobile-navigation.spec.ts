import { expect, test } from './fixtures';

test.describe('Startup and Navigation', () => {
  test('keyboard-and-mobile-navigation', async ({ page, mockApi }) => {
    await mockApi.open('/');
    await expect(page.getByRole('heading', { name: '📥 Входящие' })).toBeVisible();

    // 1. Exercise keyboard shortcuts and their editable-field guard.
    await page.keyboard.press('q');
    await expect(page.getByTestId('new-task')).toBeVisible();
    await expect(page.getByLabel('Название задачи')).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(page.getByTestId('new-task')).toHaveCount(0);

    await page.evaluate(() => {
      document.body.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'й',
        code: 'KeyQ',
        bubbles: true
      }));
    });
    await expect(page.getByTestId('new-task')).toBeVisible();
    await page.keyboard.press('Escape');

    await page.keyboard.press('/');
    await expect(page.getByRole('heading', { name: '📥 Входящие' })).toBeVisible();

    await page.keyboard.press('f');
    const search = page.getByLabel('Поиск по задачам');
    await expect(search).toBeFocused();
    await search.fill('q');
    await search.press('q');
    await expect(page.getByTestId('new-task')).toHaveCount(0);

    await page.getByRole('button', { name: 'Добавить раздел' }).click();
    await expect(page.getByRole('heading', { name: 'Новый раздел' })).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('heading', { name: 'Новый раздел' })).toHaveCount(0);

    // 2. Open and close the responsive sidebar.
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole('button', { name: 'Открыть меню' }).click();
    await expect(page.locator('.sidebar')).toHaveClass(/open/);
    await page.getByRole('button', { name: 'Закрыть боковую панель' }).click();
    await expect(page.locator('.sidebar')).not.toHaveClass(/open/);

    await page.getByRole('button', { name: 'Открыть меню' }).click();
    await page.getByRole('button', { name: '📥 Входящие' }).click();
    await expect(page.locator('.sidebar')).not.toHaveClass(/open/);
  });
});
