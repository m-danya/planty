import { expect, ids, test } from './fixtures';

test.describe('Special Views', () => {
  test('calendar-task-actions', async ({ page, mockApi }) => {
    await mockApi.open('/');
    await page.getByRole('button', { name: 'Календарь' }).click();

    const tomorrowGroup = page.getByTestId('calendar-date-group').filter({
      has: page.getByRole('heading', { name: /26 октября/ })
    });

    // 1. The shared composer defaults new tasks to the calendar group's date.
    await tomorrowGroup.getByRole('button', { name: 'Добавить задачу' }).click();
    await tomorrowGroup.getByLabel('Название задачи').fill('Подготовить форму');
    await tomorrowGroup.getByLabel('Название задачи').press('Enter');
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      section_id: ids.inbox,
      title: 'Подготовить форму',
      due_to: '2026-10-26'
    });
    await expect(tomorrowGroup.getByText('Подготовить форму', { exact: true })).toBeVisible();

    // An explicit parsed date still takes precedence over the group's default.
    await tomorrowGroup.getByRole('button', { name: 'Добавить задачу' }).click();
    await tomorrowGroup.getByLabel('Название задачи').fill('Проверить планы 1 ноября');
    await tomorrowGroup.getByLabel('Название задачи').press('Enter');
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      title: 'Проверить планы',
      due_to: '2026-11-01'
    });

    // 2. Shift+Enter carries the edited calendar task's date into its sibling.
    const gym = tomorrowGroup.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await gym.click({ modifiers: ['Alt'] });
    await tomorrowGroup.getByLabel('Название задачи').press('Shift+Enter');
    const continuation = tomorrowGroup.getByTestId('new-task');
    await expect(continuation).toBeVisible();
    await continuation.getByLabel('Название задачи').fill('Собрать спортивную сумку');
    await continuation.getByLabel('Название задачи').press('Enter');
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      title: 'Собрать спортивную сумку',
      due_to: '2026-10-26'
    });
    await expect(tomorrowGroup.getByText('Собрать спортивную сумку', { exact: true })).toBeVisible();

    // 3. Calendar DnD changes only due_to and leaves recurrence and hierarchy intact.
    const recurring = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const targetGroup = tomorrowGroup;
    const sourceBox = await recurring.boundingBox();
    const targetBox = await targetGroup.boundingBox();
    const dragAreaBox = await recurring.locator('.task-title').boundingBox();
    if (!sourceBox || !targetBox || !dragAreaBox) throw new Error('Calendar drag endpoints must be visible');
    const startX = dragAreaBox.x + dragAreaBox.width / 2;
    const startY = dragAreaBox.y + dragAreaBox.height / 2;
    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX, startY + 8, { steps: 2 });
    await page.mouse.move(targetBox.x + 100, targetBox.y + 20, { steps: 5 });
    await expect(recurring).toHaveClass(/dragging/);
    await expect(targetGroup).toHaveClass(/calendar-drop/);
    await page.mouse.up();

    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.todayTask)?.due_to)
      .toBe('2026-10-26');
    expect(mockApi.requests('PATCH', '/api/task').at(-1)?.body).toEqual({
      id: ids.todayTask,
      due_to: '2026-10-26'
    });
    expect(mockApi.state.tasks.find((task) => task.id === ids.todayTask)).toMatchObject({
      section_id: ids.inbox,
      parent_task_id: null,
      recurrence: { period: 1, type: 'days', flexible_mode: false }
    });
    await expect(targetGroup.getByText('Разобрать GTD', { exact: true })).toBeVisible();
  });
});
