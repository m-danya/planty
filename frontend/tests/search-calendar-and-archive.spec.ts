import { expect, test } from './fixtures';

test.describe('Special Views', () => {
  test('search-calendar-and-archive', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Search titles and descriptions through the debounced endpoint.
    await page.keyboard.press('f');
    const search = page.getByLabel('Поиск по задачам');
    await search.fill('GTD');
    await expect(page.getByText('Разобрать GTD', { exact: true })).toBeVisible();
    await expect(page.getByText('Сходить в зал', { exact: true })).toHaveCount(0);

    const searchResult = page.getByTestId('task-row').filter({ hasText: 'Разобрать GTD' });
    await searchResult.click({ modifiers: ['Alt'] });
    await expect(page.locator('.inline-edit > [data-testid="edit-task"]')).toBeVisible();
    await page.getByRole('button', { name: 'Отменить' }).click();

    await search.fill('Силовая');
    await expect(page.getByText('Сходить в зал', { exact: true })).toBeVisible();
    await search.fill('ничего такого нет');
    await expect(page.getByText('Ничего не найдено')).toBeVisible();
    expect(mockApi.requests('GET', '/api/task/search').at(-1)?.query.get('query'))
      .toBe('ничего такого нет');

    // 2. Calendar groups and archive contents come from independent endpoints.
    await page.getByRole('button', { name: 'Календарь' }).click();
    await expect(page.getByRole('heading', { name: 'Просрочено' })).toBeVisible();
    await expect(page.getByText('Просроченная задача', { exact: true })).toBeVisible();
    await expect(page.getByText('Разобрать GTD', { exact: true })).toBeVisible();
    await expect(page.getByText('Сходить в зал', { exact: true })).toBeVisible();
    const calendarTask = page.getByTestId('task-row').filter({ hasText: 'Сходить в зал' });
    await calendarTask.click({ modifiers: ['Alt'] });
    await expect(page.locator('.calendar-group .inline-edit > [data-testid="edit-task"]')).toBeVisible();
    await page.getByLabel('Название задачи').fill('Сходить в зал вечером');
    await page.getByLabel('Название задачи').press('Enter');
    await expect(page.getByText('Сходить в зал вечером', { exact: true })).toBeVisible();
    const calendarRequest = mockApi.requests('GET', '/api/task/by_date').at(-1);
    expect(calendarRequest?.query.get('not_before')).toBe('2026-10-25');
    expect(calendarRequest?.query.get('not_after')).toBe('2026-11-24');
    expect(calendarRequest?.query.get('with_overdue')).toBe('true');

    await page.getByRole('button', { name: 'Архив' }).click();
    await expect(page.getByText('Архивная задача', { exact: true })).toBeVisible();
    await expect(page.getByText('Разобрать GTD', { exact: true })).toHaveCount(0);
    await page.getByTestId('task-row').filter({ hasText: 'Архивная задача' }).click({ modifiers: ['Alt'] });
    await expect(page.locator('.inline-edit > [data-testid="edit-task"]')).toBeVisible();
  });
});
