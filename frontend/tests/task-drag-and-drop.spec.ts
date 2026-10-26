import type { Locator, Page } from '@playwright/test';
import { expect, ids, test } from './fixtures';

async function dragWithHorizontalOffset(
  page: Page,
  source: Locator,
  target: Locator,
  horizontalOffset: number
) {
  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  if (!sourceBox || !targetBox) throw new Error('Drag source and target must be visible');
  const localStartX = Math.min(100, sourceBox.width / 2);
  const startX = sourceBox.x + localStartX;
  const transfer = await page.evaluateHandle(() => new DataTransfer());
  await source.dispatchEvent('dragstart', {
    dataTransfer: transfer,
    clientX: startX,
    clientY: sourceBox.y + sourceBox.height / 2
  });
  await target.dispatchEvent('dragover', {
    dataTransfer: transfer,
    clientX: targetBox.x + localStartX + horizontalOffset,
    clientY: targetBox.y + targetBox.height / 2
  });
  await page.evaluate(() => new Promise<void>((resolve) => requestAnimationFrame(() => resolve())));
  await target.dispatchEvent('dragover', {
    dataTransfer: transfer,
    clientX: targetBox.x + localStartX + horizontalOffset,
    clientY: targetBox.y + targetBox.height / 2
  });
  await target.dispatchEvent('drop', {
    dataTransfer: transfer,
    clientX: targetBox.x + localStartX + horizontalOffset,
    clientY: targetBox.y + targetBox.height / 2
  });
}

test.describe('Tasks', () => {
  test('task-drag-and-drop', async ({ page, mockApi }) => {
    mockApi.state.tasks.push({
      ...mockApi.state.tasks.find((task) => task.id === ids.projectTask)!,
      id: '10000000-0000-4000-8000-000000000008',
      title: 'Проверить доску'
    });
    await mockApi.open('/');

    const parent = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const child = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });

    // The action is available before a task has any existing subtasks.
    await parent.click({ button: 'right' });
    await expect(page.getByRole('menuitem', { name: 'Создать подзадачу' })).toBeVisible();
    await page.getByRole('button', { name: 'Закрыть меню' }).click();

    // 1. A near-vertical drag preserves depth; 40 px to the right nests the task.
    await dragWithHorizontalOffset(page, child, parent, 39);
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBeNull();
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      task_id: ids.tomorrowTask,
      parent_task_id: null
    });

    await dragWithHorizontalOffset(
      page,
      page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }),
      page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' }),
      40
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBe(ids.todayTask);
    await expect(page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }))
      .toHaveCSS('padding-left', '29px');

    // 2. A horizontal nesting gesture cannot create a parent/child cycle.
    const movesBeforeCycle = mockApi.requests('POST', '/api/task/move').length;
    await dragWithHorizontalOffset(
      page,
      page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' }),
      page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }),
      40
    );
    await expect(page.getByRole('status')).toHaveText('Нельзя перенести задачу внутрь её подзадачи');
    expect(mockApi.requests('POST', '/api/task/move')).toHaveLength(movesBeforeCycle);

    // 3. A near-vertical child drag preserves its parent; 40 px left extracts it.
    await dragWithHorizontalOffset(
      page,
      page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }),
      page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' }),
      -39
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBe(ids.todayTask);

    await dragWithHorizontalOffset(
      page,
      page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }),
      page.getByTestId('task-row').filter({ hasText: 'Просроченная задача' }),
      -40
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBeNull();
    await expect(page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }))
      .toHaveCSS('padding-left', '1px');

    // 4. Create another subtask through the parent's context menu.
    await parent.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'Создать подзадачу' }).click();
    const composer = page.getByTestId('new-task');
    await expect(composer).toBeVisible();
    await expect(composer.getByLabel('Раздел задачи')).toHaveCount(0);
    await composer.getByLabel('Название задачи').fill('Новая подзадача');
    await composer.getByRole('button', { name: 'Сохранить задачу' }).click();
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      section_id: ids.inbox,
      parent_task_id: ids.todayTask,
      title: 'Новая подзадача'
    });
    await expect(page.getByTestId('task-row').filter({ hasText: 'Новая подзадача' }))
      .toHaveCSS('padding-left', '29px');

    // 5. Board columns use local card coordinates and destination-local indices.
    await mockApi.open(`/?section=${ids.projects}`);
    await page.getByRole('button', { name: 'Показать как доску' }).click();
    const board = page.getByTestId('section-board');
    const plantyColumn = board.getByTestId('section-group').filter({
      has: page.getByRole('heading', { name: '☘️ Planty' })
    });
    const homeColumn = board.getByTestId('section-group').filter({
      has: page.getByRole('heading', { name: 'Дом' })
    });

    // Crossing a whole column at the same local X must not count as indenting.
    await dragWithHorizontalOffset(
      page,
      plantyColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }),
      homeColumn.getByTestId('task-row').filter({ hasText: 'Купить растения' }),
      0
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.projectTask))
      .toMatchObject({ section_id: ids.home, parent_task_id: null });
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      task_id: ids.projectTask,
      section_to_id: ids.home,
      index: 0,
      parent_task_id: null
    });

    // The same card still nests when its local pointer moves exactly 40 px right.
    await dragWithHorizontalOffset(
      page,
      homeColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }),
      homeColumn.getByTestId('task-row').filter({ hasText: 'Купить растения' }),
      40
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.projectTask)?.parent_task_id)
      .toBe(ids.homeTask);
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      section_to_id: ids.home,
      index: 1,
      parent_task_id: ids.homeTask
    });
    await expect(homeColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }))
      .toHaveCSS('padding-left', '36px');

    // A neutral cross-section move cannot retain a parent from the old column.
    await dragWithHorizontalOffset(
      page,
      homeColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }),
      plantyColumn.getByTestId('task-row').filter({ hasText: 'Проверить доску' }),
      0
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.projectTask))
      .toMatchObject({ section_id: ids.planty, parent_task_id: null });
    expect(mockApi.requests('POST', '/api/task/move').at(-1)?.body).toMatchObject({
      section_to_id: ids.planty,
      index: 0,
      parent_task_id: null
    });
    await expect(plantyColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }))
      .toHaveCSS('padding-left', '8px');

    // Local horizontal intent also works while crossing from one column to another.
    await dragWithHorizontalOffset(
      page,
      plantyColumn.getByTestId('task-row').filter({ hasText: 'Допилить интерфейс' }),
      homeColumn.getByTestId('task-row').filter({ hasText: 'Купить растения' }),
      40
    );
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.projectTask))
      .toMatchObject({ section_id: ids.home, parent_task_id: ids.homeTask });
  });
});
