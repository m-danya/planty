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

    // User preferences default to auto-archive and are stored locally.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    const autoArchive = page.getByLabel('Автоматически переносить выполненные задачи в архив');
    await expect(autoArchive).toBeChecked();
    await autoArchive.uncheck();
    expect(await page.evaluate(() => localStorage.getItem('planty.autoArchive'))).toBe('false');

    // The profile setting switches the whole shell immediately.
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
    await page.getByRole('button', { name: 'Profile settings' }).click();
    await expect(page.getByLabel('Automatically move completed tasks to the archive')).not.toBeChecked();
  });
});
