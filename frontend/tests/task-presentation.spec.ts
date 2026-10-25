import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-presentation', async ({ page, mockApi }) => {
    const today = mockApi.state.tasks.find((task) => task.id === ids.todayTask)!;
    const tomorrow = mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)!;
    today.is_completed = true;
    tomorrow.parent_task_id = today.id;
    mockApi.state.tasks.push({
      ...tomorrow,
      id: '10000000-0000-4000-8000-000000000099',
      parent_task_id: '10000000-0000-4000-8000-999999999999',
      title: 'Осиротевшая подзадача',
      description: null,
      due_to: null
    });

    // 1. Render every task state and hierarchy fallback.
    await mockApi.open('/');

    const todayRow = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await expect(todayRow).toHaveClass(/completed/);
    await expect(todayRow.locator('.task-date.today')).toHaveText(/Сегодня/);
    await expect(todayRow.getByLabel('каждый день')).toBeVisible();
    await expect(todayRow.locator('.task-chevron')).toBeVisible();
    await expect(todayRow.getByText('Собрать всё в одном месте')).toBeVisible();

    const chevron = todayRow.getByRole('button', { name: 'Свернуть подзадачи' });
    await expect(chevron).toHaveAttribute('aria-expanded', 'true');

    const tomorrowRow = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await expect(tomorrowRow.locator('.task-date.tomorrow')).toHaveText(/Завтра/);
    await expect(tomorrowRow).toHaveCSS('padding-left', '29px');

    // 2. Collapse and expand the parent through the chevron button.
    await chevron.click();
    await expect(tomorrowRow).toHaveCount(0);
    const expandedChevron = todayRow.getByRole('button', { name: 'Раскрыть подзадачи' });
    await expect(expandedChevron).toHaveAttribute('aria-expanded', 'false');
    await expandedChevron.click();
    await expect(tomorrowRow).toBeVisible();

    const overdueRow = page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' });
    await expect(overdueRow.locator('.task-date.overdue')).toContainText('24 окт.');

    const futureRow = page.getByTestId('task-row').filter({ hasText: 'Задача на будущее' });
    await expect(futureRow.locator('.task-date.future')).toContainText('1 нояб.');

    const orphanRow = page.getByTestId('task-row').filter({ hasText: 'Осиротевшая подзадача' });
    await expect(orphanRow).toBeVisible();
    await expect(orphanRow).toHaveCSS('padding-left', '1px');
  });
});
