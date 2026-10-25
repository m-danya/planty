import { expect, ids, test } from './fixtures';

test.describe('Startup and Navigation', () => {
  test('startup-routing-and-failures', async ({ page, mockApi }) => {
    const pageErrors: Error[] = [];
    page.on('pageerror', (error) => pageErrors.push(error));

    // 1. Honor a nested section selected in the URL.
    await mockApi.open(`/?section=${ids.planty}`);
    await expect(page.getByRole('heading', { name: '☘️ Planty' })).toBeVisible();
    await expect(page.getByText('Допилить интерфейс')).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`section=${ids.planty}`));

    // 2. Surface a startup failure without leaking an unhandled exception.
    mockApi.failOnce('GET', '/api/sections', {
      status: 503,
      detail: 'Sections are temporarily unavailable'
    });
    await page.reload();

    await expect(page.getByRole('status')).toHaveText('Не удалось загрузить данные');
    await expect(page.getByText('Создайте раздел, чтобы добавить первую задачу.')).toBeVisible();
    expect(pageErrors).toEqual([]);
  });
});
