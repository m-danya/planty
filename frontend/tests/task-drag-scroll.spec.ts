import { expect, ids, test } from './fixtures';

test.describe('Tasks', () => {
  test('task-drag-scroll', async ({ page, mockApi }) => {
    const template = mockApi.state.tasks.find((task) => task.id === ids.projectTask)!;
    for (let index = 0; index < 30; index += 1) {
      mockApi.state.tasks.push({
        ...template,
        id: `70000000-0000-4000-8000-${String(index).padStart(12, '0')}`,
        section_id: ids.inbox,
        title: `Длинный список ${index}`
      });
    }
    await mockApi.open('/');
    await page.evaluate(() => window.scrollTo(0, 0));

    const source = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    const handleBox = await source.getByRole('button', { name: 'Перетащить задачу' }).boundingBox();
    if (!handleBox) throw new Error('Drag source must be visible');
    const x = handleBox.x + handleBox.width / 2;
    const y = handleBox.y + handleBox.height / 2;
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x, y + 12, { steps: 4 });
    await page.mouse.wheel(0, 480);

    await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(0);

    await page.mouse.up();
    const afterDrag = await page.evaluate(() => window.scrollY);
    await page.locator('main').dispatchEvent('wheel', { deltaY: 480, deltaMode: 0 });
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(afterDrag);
  });
});
