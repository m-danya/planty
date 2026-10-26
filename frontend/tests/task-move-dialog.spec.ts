import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-move-dialog', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Move a task through the context menu and verify both sections.
    const row = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await row.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'В другой раздел' }).click();
    await expect(page.getByRole('heading', { name: 'Переместить задачу' })).toBeVisible();
    const sectionSelect = page.getByLabel('Новый раздел');
    await expect(sectionSelect).toHaveValue(ids.inbox);
    await sectionSelect.selectOption(ids.planty);
    await page.getByRole('button', { name: 'Переместить' }).click();

    await expect(page.getByText('Разобрать GTD', { exact: true })).toHaveCount(0);
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      task_id: ids.todayTask,
      section_to_id: ids.planty,
      index: 0,
      parent_task_id: null
    });

    await page.getByRole('button', { name: '☘️ Planty' }).click();
    await expect(page.getByText('Разобрать GTD', { exact: true })).toBeVisible();

    // Clicking the backdrop closes a subsequently opened move dialog.
    const movedRow = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await movedRow.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'В другой раздел' }).click();
    await page.locator('.dialog-shield').click({ position: { x: 5, y: 5 } });
    await expect(page.getByRole('heading', { name: 'Переместить задачу' })).toHaveCount(0);
  });
});
