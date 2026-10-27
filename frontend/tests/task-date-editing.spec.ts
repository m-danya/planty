import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-date-editing', async ({ page, mockApi }) => {
    await mockApi.open('/');

    const recurring = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const plain = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });

    // 1. A task click opens editing; a plain due date expands only the fields that exist.
    await recurring.click();
    await expect(page.getByTestId('edit-task')).toBeVisible();
    await page.getByRole('button', { name: 'Отменить' }).click();

    await plain.locator('.task-date').click();
    const plainDetails = page.getByTestId('edit-task').locator('.date-popover');
    await expect(plainDetails).toHaveCSS('width', '273px');
    await expect(plainDetails.locator('.date-summary')).toContainText('26 октября 2026 г.');
    await expect(plainDetails.getByLabel('Время')).toHaveCount(0);
    await expect(plainDetails.locator('.recurrence-summary')).toHaveCount(0);
    await expect(plainDetails.getByText('Расчёт следующей даты', { exact: true })).toHaveCount(0);
    await plainDetails.getByRole('button', { name: 'Закрыть меню' }).click();
    await page.getByRole('button', { name: 'Отменить' }).click();

    // 2. Recurrence details keep the delayed help and shared calendar.
    await recurring.locator('.task-date').click();
    const editor = page.getByTestId('edit-task');
    const dateDetails = editor.locator('.date-popover');
    await expect(dateDetails).toBeVisible();
    await expect(dateDetails.getByLabel('Время')).toHaveCount(0);
    await expect(dateDetails.locator('.recurrence-value')).toHaveText('каждый день');
    await expect(dateDetails.locator('.recurrence-value')).not.toContainText('от дня выполнения');

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
