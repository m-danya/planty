import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-errors', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Failed writes show their API details and preserve local UI state.
    mockApi.failOnce('POST', '/api/task', {
      status: 422,
      detail: 'Название задачи запрещено'
    });
    await page.keyboard.press('q');
    await page.getByLabel('Название задачи').fill('Запрещённая задача');
    await page.getByLabel('Название задачи').press('Enter');

    await expect(page.getByRole('status')).toHaveText('Название задачи запрещено');
    await expect(page.getByTestId('new-task')).toBeVisible();
    expect(mockApi.state.tasks.some((task) => task.title === 'Запрещённая задача')).toBe(false);

    mockApi.failOnce('POST', '/api/task', {
      status: 500,
      detail: 'not json',
      contentType: 'text/plain'
    });
    await page.getByLabel('Название задачи').press('Enter');
    await expect(page.getByRole('status')).toHaveText('Что-то пошло не так');
    await page.keyboard.press('Escape');

    mockApi.failOnce('POST', '/api/task/toggle_completed', {
      status: 503,
      detail: 'Сервис задач недоступен'
    });
    const row = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await row.getByRole('button', { name: 'Выполнить задачу' }).click();

    await expect(page.getByRole('status')).toHaveText('Сервис задач недоступен');
    await expect(row).not.toHaveClass(/completed/);
    expect(mockApi.state.tasks.find((task) => task.id === ids.todayTask)?.is_completed).toBe(false);
  });
});
