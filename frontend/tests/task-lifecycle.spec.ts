import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-lifecycle', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Auto-archive is enabled by default and removes a completed task.
    let gymRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await gymRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    await expect(gymRow).toHaveCount(0);
    expect(mockApi.requests('POST', '/api/task/toggle_completed').at(-1)?.body).toMatchObject({
      task_id: ids.tomorrowTask,
      auto_archive: true
    });

    await page.getByRole('button', { name: 'Архив' }).click();
    gymRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await expect(gymRow).toBeVisible();
    await gymRow.getByRole('button', { name: 'Вернуть задачу' }).click();
    await expect(gymRow).toHaveCount(0);

    // Disabling auto-archive keeps subsequently completed tasks in place.
    await page.getByRole('button', { name: '📥 Входящие' }).click();
    await page.getByRole('button', { name: 'Настройки профиля' }).click();
    await page.getByLabel('Автоматически переносить выполненные задачи в архив').uncheck();
    await page.getByRole('button', { name: 'Готово' }).click();
    let overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await overdueRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await expect(overdueRow).toHaveClass(/completed/);
    expect(mockApi.requests('POST', '/api/task/toggle_completed').at(-1)?.body).toMatchObject({
      task_id: ids.overdueTask,
      auto_archive: false
    });
    await overdueRow.getByRole('button', { name: 'Вернуть задачу' }).click();

    // Archive from the section and restore from the archive view.
    gymRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await gymRow.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'В архив' }).click();
    await expect(gymRow).toHaveCount(0);
    await expect(page.getByRole('status')).toHaveText('Задача перемещена в архив');

    await page.getByRole('button', { name: 'Архив' }).click();
    gymRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await expect(gymRow).toBeVisible();
    await gymRow.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'Вернуть из архива' }).click();
    await expect(gymRow).toHaveCount(0);

    await page.getByRole('button', { name: '📥 Входящие' }).click();
    await expect(page.getByText('Сходить в зал', { exact: true })).toBeVisible();

    // Dismiss deletion once, then accept it.
    overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await overdueRow.click({ button: 'right' });
    page.once('dialog', async (dialog) => dialog.dismiss());
    await page.getByRole('menuitem', { name: 'Удалить' }).click();
    await expect(overdueRow).toBeVisible();

    await overdueRow.click({ button: 'right' });
    page.once('dialog', async (dialog) => dialog.accept());
    await page.getByRole('menuitem', { name: 'Удалить' }).click();
    overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await expect(overdueRow).toHaveCount(0);
    expect(mockApi.requests('DELETE', '/api/task').at(-1)?.body).toMatchObject({
      task_id: expect.any(String)
    });
  });
});
