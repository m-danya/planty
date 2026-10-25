import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-composer-and-editing', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Create a recurring task from natural-language input.
    await page.keyboard.press('q');
    await page.getByLabel('Название задачи').fill('полить цветы каждые! 3 дня начиная завтра');
    await page.getByLabel('Описание задачи').fill('не забыть удобрение');
    await expect(page.locator('.composer-highlight mark')).toHaveText('каждые! 3 дня начиная завтра');
    await expect(page.locator('.date-chip')).toContainText('каждые! 3 дня начиная завтра');
    await page.getByRole('button', { name: 'Параметры срока' }).click();
    const datePopover = page.getByLabel('Параметры срока').filter({ has: page.getByText('Расчёт следующей даты') });
    await expect(datePopover).toContainText('26 октября 2026 г.');
    await expect(datePopover).toContainText('каждые 3 дн.');
    await expect(datePopover).toContainText('Гибко — от дня выполнения');
    await expect(datePopover).toContainText('каждые! 3 дня начиная завтра');
    await page.getByRole('button', { name: 'Закрыть меню' }).last().click();
    await page.getByLabel('Название задачи').press('Enter');

    await expect(page.getByText('полить цветы', { exact: true })).toBeVisible();
    const created = mockApi.requests('POST', '/api/task').at(-1)?.body;
    expect(created).toMatchObject({
      section_id: ids.inbox,
      parent_task_id: null,
      title: 'полить цветы',
      description: 'не забыть удобрение',
      due_to: '2026-10-26',
      recurrence: { period: 3, type: 'days', flexible_mode: true }
    });

    // 2. Edit the title, preserve its parsed date, and move it to Planty.
    const createdRow = page.getByTestId('task-row').filter({ hasText: 'полить цветы' });
    await createdRow.click();
    await expect(page.getByTestId('edit-task')).toHaveCount(0);
    await createdRow.click({ modifiers: ['Alt'] });
    await expect(page.getByTestId('edit-task')).toBeVisible();
    await expect(page.locator('.inline-edit > [data-testid="edit-task"]')).toBeVisible();
    await page.getByRole('button', { name: 'Параметры срока' }).click();
    await expect(page.getByLabel('Параметры срока').filter({ has: page.getByText('Расчёт следующей даты') })).toContainText('Гибко — от дня выполнения');
    await page.getByRole('button', { name: 'Закрыть меню' }).last().click();
    await page.getByLabel('Название задачи').fill('полить цветы на балконе #lant');
    await expect(page.getByRole('listbox', { name: 'Разделы' })).toHaveCount(0);
    await page.getByLabel('Название задачи').fill('полить цветы на балконе #Plant');
    const suggestions = page.getByRole('listbox', { name: 'Разделы' });
    await expect(suggestions).toBeVisible();
    await expect(suggestions.getByRole('option')).toContainText('☘️ Planty');
    await page.getByLabel('Название задачи').fill('полить цветы на балконе №Plant');
    await expect(suggestions).toBeVisible();
    await expect(suggestions.getByRole('option')).toContainText('№☘️ Planty');
    await page.getByLabel('Название задачи').press('Enter');
    await expect(page.getByLabel('Название задачи')).toHaveValue('полить цветы на балконе');
    await page.getByLabel('Описание задачи').fill('вечером');
    await page.getByLabel('Название задачи').press('Enter');

    await expect(page.getByText('полить цветы', { exact: true })).toHaveCount(0);
    await expect(page.getByText('полить цветы на балконе', { exact: true })).toHaveCount(0);
    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      title: 'полить цветы на балконе',
      description: 'вечером',
      due_to: '2026-10-26',
      recurrence: { period: 3, type: 'days', flexible_mode: true }
    });
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      section_to_id: ids.planty,
      parent_task_id: null
    });

    await page.getByRole('button', { name: '☘️ Planty' }).click();
    await expect(page.getByText('полить цветы на балконе', { exact: true })).toBeVisible();
    await expect(page.getByText('вечером', { exact: true })).toBeVisible();
  });
});
