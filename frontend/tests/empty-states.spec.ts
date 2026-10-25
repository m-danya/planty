import { expect, test } from './fixtures';

test.describe('Special Views', () => {
  test('empty-states', async ({ page, mockApi }) => {
    mockApi.state.root.subsections = [];
    for (const task of mockApi.state.tasks) {
      task.due_to = null;
      task.is_archived = false;
    }

    // 1. Every view explains its empty state without backend fixtures.
    await mockApi.open('/');
    await expect(page.getByText('Создайте раздел, чтобы добавить первую задачу.')).toBeVisible();
    await page.keyboard.press('q');
    await expect(page.getByTestId('new-task')).toHaveCount(0);

    await page.getByRole('button', { name: /Поиск/ }).click();
    await page.getByLabel('Поиск по задачам').fill('missing');
    await expect(page.getByText('Ничего не найдено')).toBeVisible();

    await page.getByRole('button', { name: 'Календарь' }).click();
    await expect(page.getByText('На ближайший месяц задач нет.')).toBeVisible();

    await page.getByRole('button', { name: 'Архив' }).click();
    await expect(page.getByText('Архив пуст')).toBeVisible();
  });
});
