import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-drag-and-drop', async ({ page, mockApi }) => {
    await mockApi.open('/');

    const parent = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const child = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });

    // 1. Nest a task and prevent moving its parent into the new child.
    await child.dragTo(parent);
    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBe(ids.todayTask);
    await expect(page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }))
      .toHaveCSS('padding-left', '29px');

    const movesBeforeCycle = mockApi.requests('POST', '/api/task/move').length;
    await parent.dragTo(page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }));
    await expect(page.getByRole('status')).toHaveText('Нельзя перенести задачу внутрь её подзадачи');
    expect(mockApi.requests('POST', '/api/task/move')).toHaveLength(movesBeforeCycle);

    // 2. Create another subtask through the parent's context menu.
    await parent.click({ button: 'right' });
    await page.getByRole('menuitem', { name: 'Добавить подзадачу' }).click();
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

    // 3. A top-edge drop makes the child a root-level sibling again.
    const currentParent = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const currentChild = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    const box = await currentParent.boundingBox();
    if (!box) throw new Error('Parent task is not visible');
    const transfer = await page.evaluateHandle(() => new DataTransfer());
    await currentChild.dispatchEvent('dragstart', { dataTransfer: transfer });
    await currentParent.dispatchEvent('dragover', {
      dataTransfer: transfer,
      clientY: box.y + 1
    });
    await currentParent.dispatchEvent('drop', {
      dataTransfer: transfer,
      clientY: box.y + 1
    });

    await expect.poll(() => mockApi.state.tasks.find((task) => task.id === ids.tomorrowTask)?.parent_task_id)
      .toBeNull();
    await expect(page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' }))
      .toHaveCSS('padding-left', '1px');
  });
});
