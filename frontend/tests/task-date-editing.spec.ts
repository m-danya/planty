import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-date-editing', async ({ page, mockApi }) => {
    await mockApi.open('/');

    const recurring = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });

    // 1. A task click opens editing; its due date also expands date details.
    await recurring.click();
    await expect(page.getByTestId('edit-task')).toBeVisible();
    await page.getByRole('button', { name: 'Отменить' }).click();

    await recurring.locator('.task-date').click();
    const editor = page.getByTestId('edit-task');
    const dateDetails = editor.getByLabel('Параметры срока').filter({
      has: page.getByText('Расчёт следующей даты')
    });
    await expect(dateDetails).toBeVisible();

    // 2. The explanation is tucked behind a delayed tooltip and the shared calendar is embedded.
    const help = dateDetails.getByRole('button', {
      name: 'Поставьте ! после слова «каждый», например «каждый! день», чтобы отсчитывать новый срок от дня выполнения.'
    });
    const tooltip = dateDetails.getByRole('tooltip');
    await expect(tooltip).toBeHidden();
    await help.hover();
    await expect(tooltip).toBeVisible();

    const calendar = dateDetails.getByRole('group', { name: 'Выбрать дату' });
    await expect(calendar).toBeVisible();
    await calendar.getByRole('button', { name: /30 октября 2026/ }).click();
    await expect(dateDetails).toContainText('30 октября 2026 г.');

    // 3. Saving changes the date without altering recurrence settings.
    await editor.getByLabel('Название задачи').press('Enter');
    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      id: ids.todayTask,
      due_to: '2026-10-30',
      recurrence: { period: 1, type: 'days', flexible_mode: false }
    });
  });
});
