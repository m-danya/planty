import { expect, test } from './fixtures';

test.describe('Localization', () => {
  test('localization-and-settings', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // Russian is the default and server-provided system names are localized too.
    await expect(page.getByRole('button', { name: 'Поиск' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Календарь' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Архив' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '📥 Входящие' })).toBeVisible();
    await expect(page.getByText('Inbox', { exact: true })).toHaveCount(0);
    const inbox = page.getByRole('button', { name: '📥 Входящие' });
    await expect(inbox).toHaveAttribute('title', '4 задачи');
    await expect(inbox).not.toContainText('4');
    await expect(page.locator('.page-heading .heading-actions button')).toHaveCount(1);

    // The profile setting switches the whole shell immediately.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    await page.getByLabel('Язык интерфейса').selectOption('en');
    await expect(page.getByRole('button', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Calendar' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '📥 Inbox' })).toBeVisible();
    await page.getByRole('button', { name: 'Done' }).click();

    // The preference is local-only and survives navigation/reload.
    await page.reload();
    await expect(page.getByRole('button', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '📥 Inbox' })).toBeVisible();
    expect(await page.evaluate(() => localStorage.getItem('planty.locale'))).toBe('en');
  });
});
