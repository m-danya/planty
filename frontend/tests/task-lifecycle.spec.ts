import { expect, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-lifecycle', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Complete and restore a task.
    let todayRow = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await todayRow.getByRole('button', { name: 'Выполнить задачу' }).click();
    todayRow = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await expect(todayRow).toHaveClass(/completed/);
    await todayRow.getByRole('button', { name: 'Вернуть задачу' }).click();
    await expect(page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' })).not.toHaveClass(/completed/);

    // Archive from the section and restore from the archive view.
    let gymRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
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
    let overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
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
