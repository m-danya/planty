import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-scheduling-menu', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Schedule from the colored today and tomorrow shortcuts.
    let row = page.getByTestId('task-row').filter({ hasText: 'Задача на будущее' });
    await row.click({ button: 'right' });
    const today = page.getByRole('menuitem', { name: 'Назначить на: сегодня' });
    const tomorrow = page.getByRole('menuitem', { name: 'Назначить на: завтра' });
    await expect(today.locator('.date-today')).toHaveCSS('color', 'rgb(7, 147, 46)');
    await expect(tomorrow.locator('.date-tomorrow')).toHaveCSS('color', 'rgb(182, 98, 0)');
    await today.click();
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.futureTask)?.due_to)
      .toBe('2026-10-25');
    row = page.getByTestId('task-row').filter({ hasText: 'Задача на будущее' });
    await expect(row.locator('.task-date.today')).toContainText('Сегодня');

    await row.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'Назначить на: завтра' }).click();
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.futureTask)?.due_to)
      .toBe('2026-10-26');
    row = page.getByTestId('task-row').filter({ hasText: 'Задача на будущее' });
    await expect(row.locator('.task-date.tomorrow')).toContainText('Завтра');

    // 2. Navigate the custom calendar and pick an arbitrary local date.
    await row.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'Назначить на другой день' }).click();
    const calendar = page.getByRole('dialog', { name: 'Выбрать дату' });
    await expect(calendar).toBeVisible();
    await expect(calendar.getByRole('heading')).toContainText('Октябрь 2026');
    await calendar.getByRole('button', { name: 'Следующий месяц' }).click();
    await calendar.getByRole('button', { name: 'Следующий месяц' }).click();
    await expect(calendar.getByRole('heading')).toContainText('Декабрь 2026');
    await calendar.getByRole('button', { name: /24 декабря 2026/ }).click();

    await expect.poll(() => mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      id: ids.futureTask,
      due_to: '2026-12-24'
    });
    row = page.getByTestId('task-row').filter({ hasText: 'Задача на будущее' });
    await expect(row.locator('.task-date.future')).toContainText('24 декабря');
  });
});
