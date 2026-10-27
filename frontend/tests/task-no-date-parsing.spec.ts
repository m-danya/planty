import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-no-date-parsing', async ({ page, mockApi }) => {
    await mockApi.open('/');

    const recurring = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await recurring.click({ modifiers: ['Alt'] });
    const editor = page.getByTestId('edit-task');
    await editor.getByLabel('Название задачи').fill('каждый день качаться без срока');

    await expect(editor.locator('.composer-highlight mark')).toHaveText('без срока');
    await expect(editor.locator('.date-chip')).toHaveCount(0);
    await editor.getByLabel('Название задачи').press('Enter');

    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      id: ids.todayTask,
      title: 'каждый день качаться',
      due_to: null,
      due_time: null,
      recurrence: null
    });
    const saved = page.getByTestId('task-row').filter({ hasText: 'каждый день качаться' });
    await expect(saved).toBeVisible();
    await expect(saved.locator('.task-date')).toHaveCount(0);
  });
});
