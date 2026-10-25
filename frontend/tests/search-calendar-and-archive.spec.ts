import { expect, test } from './fixtures';

test.describe('Special Views', () => {
  test('search-calendar-and-archive', async ({ page, mockApi }) => {
    await mockApi.open('/');

    // 1. Search titles and descriptions through the debounced endpoint.
    await page.keyboard.press('/');
    const search = page.getByLabel('Поиск по задачам');
    await search.fill('GTD');
    await expect(page.getByText('Разобрать GTD', { exact: true })).toBeVisible();
    await expect(page.getByText('Сходить в зал', { exact: true })).toHaveCount(0);

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
    const calendarRequest = mockApi.requests('GET', '/api/task/by_date').at(-1);
    expect(calendarRequest?.query.get('not_before')).toBe('2026-10-25');
    expect(calendarRequest?.query.get('not_after')).toBe('2026-11-24');
    expect(calendarRequest?.query.get('with_overdue')).toBe('true');

    await page.getByRole('button', { name: 'Архив' }).click();
    await expect(page.getByText('Архивная задача', { exact: true })).toBeVisible();
    await expect(page.getByText('Разобрать GTD', { exact: true })).toHaveCount(0);
  });
});
