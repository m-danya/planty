import { expect, test } from './fixtures';

const backup = 'tests/data/todoist-backup.zip';

test.describe('Settings', () => {
  test('todoist-import', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Append imported data to the current sections.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    const settings = page.getByRole('dialog', { name: 'Настройки профиля' });
    await expect(settings.getByText('Импорт из Todoist')).toBeVisible();
    await settings.locator('input[type="file"]').setInputFiles(backup);
    await expect(settings.getByText('todoist-backup.zip')).toBeVisible();
    await settings.getByLabel('Стереть все текущие данные').uncheck();
    await settings.getByRole('button', { name: 'Импортировать данные из Todoist' }).click();

    await expect(page.getByRole('button', { name: '📥 Входящие' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Todoist Входящие' })).toBeVisible();
    expect(mockApi.requests('POST', '/api/import/todoist').at(-1)?.body).toMatchObject({
      erase_existing: false,
      filename: 'todoist-backup.zip'
    });

    // 2. Replace all current data on the next import.
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    await settings.locator('input[type="file"]').setInputFiles(backup);
    await expect(settings.getByLabel('Стереть все текущие данные')).toBeChecked();
    await settings.getByRole('button', { name: 'Импортировать данные из Todoist' }).click();

    await expect(page.getByRole('button', { name: '📥 Входящие' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Todoist Входящие' })).toBeVisible();
    await expect(page.getByRole('status')).toHaveText('Импортировано проектов: 1, задач: 1');
    expect(mockApi.requests('POST', '/api/import/todoist').at(-1)?.body).toMatchObject({
      erase_existing: true,
      filename: 'todoist-backup.zip'
    });
  });
});
