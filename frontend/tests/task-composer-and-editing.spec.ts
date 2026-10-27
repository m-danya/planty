import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-composer-and-editing', async ({ page, mockApi }) => {
    mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)!.parent_task_id = ids.todayTask;
    await mockApi.open('/');

    // 1. Save an edited child with Shift+Enter and create its next sibling.
    const child = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await child.click({ modifiers: ['Alt'] });
    await page.getByLabel('Название задачи').fill('Сходить в зал после работы');
    await page.getByLabel('Название задачи').press('Shift+Enter');
    const continuation = page.getByTestId('new-task');
    await expect(continuation).toBeVisible();
    await expect(continuation.getByRole('button', { name: 'Флаг' })).toHaveCount(0);
    await expect(continuation.locator('..')).toHaveCSS('padding-left', '28px');
    await continuation.getByLabel('Название задачи').fill('Купить воду для тренировки');
    await continuation.getByLabel('Название задачи').press('Enter');

    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toMatchObject({
      id: ids.tomorrowTask,
      title: 'Сходить в зал после работы'
    });
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      parent_task_id: ids.todayTask,
      title: 'Купить воду для тренировки',
      due_to: '2026-10-26'
    });
    await expect.poll(() => mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      index: 2,
      parent_task_id: ids.todayTask
    });
    await expect(page.getByTestId('task-row').filter({ hasText: 'Купить воду для тренировки' }))
      .toHaveCSS('padding-left', '29px');

    // 2. Create a recurring task from natural-language input.
    await page.keyboard.press('q');
    await page.getByLabel('Название задачи').fill('полить цветы каждые! 3 дня начиная завтра в 18:30');
    await page.getByLabel('Описание задачи').fill('не забыть удобрение');
    await expect(page.locator('.composer-highlight mark')).toHaveText('каждые! 3 дня начиная завтра в 18:30');
    await expect(page.locator('.date-chip')).toContainText('каждые! 3 дня начиная завтра в 18:30');
    await page.getByRole('button', { name: 'Параметры срока' }).click();
    const datePopover = page.getByLabel('Параметры срока').filter({ has: page.getByText('Расчёт следующей даты') });
    await expect(datePopover).toContainText('26 октября 2026 г.');
    await expect(datePopover).toContainText('каждые 3 дн.');
    await expect(datePopover.getByLabel('Время')).toHaveValue('18:30');
    await expect(datePopover.getByLabel('Время')).toHaveAttribute('type', 'text');
    await expect(datePopover.locator('.time-field svg')).toHaveCount(1);
    await expect(datePopover).toContainText('Гибко — от дня выполнения');
    await expect(datePopover).toContainText('каждые! 3 дня начиная завтра в 18:30');
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
      due_time: '18:30',
      recurrence: { period: 3, type: 'days', flexible_mode: true }
    });

    // 3. Edit the title, preserve its parsed date, and move it to Planty.
    const createdRow = page.getByTestId('task-row').filter({ hasText: 'полить цветы' });
    await createdRow.click();
    await expect(page.getByTestId('edit-task')).toBeVisible();
    await expect(page.locator('.inline-edit > [data-testid="edit-task"]')).toBeVisible();
    await page.getByRole('button', { name: 'Параметры срока' }).click();
    const editDatePopover = page.getByLabel('Параметры срока').filter({ has: page.getByText('Расчёт следующей даты') });
    await expect(editDatePopover).toContainText('Гибко — от дня выполнения');
    await editDatePopover.getByLabel('Время').fill('19:45');
    await editDatePopover.getByLabel('Время').press('Tab');
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
      due_time: '19:45',
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
