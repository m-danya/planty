import { expect, ids, test, type MockApi } from './fixtures';
import type { Page } from '@playwright/test';

async function openSectionAction(page: Page, title: string, action: 'Переименовать' | 'Переместить' | 'Удалить') {
  const link = page.locator('.section-link').filter({ hasText: title }).first();
  await link.hover();
  await link.locator('.section-more').click();
  await page.getByRole('menuitem', { name: action }).click();
}

test.describe('Sections', () => {
  test('section-lifecycle', async ({ page, mockApi }: { page: Page; mockApi: MockApi }) => {
    await mockApi.open('/');

    // Reorder top-level sections with the sidebar drag handle.
    await page.getByRole('button', { name: 'Когда-нибудь' }).dragTo(page.getByRole('button', { name: '📥 Входящие' }));
    expect(mockApi.requests('POST', '/api/section/move').at(-1)?.body).toMatchObject({
      section_id: ids.someday,
      to_parent_id: ids.root,
      index: 0
    });
    const topLevelLabels = await page.locator('.sections-list > .section-node > .section-link').allTextContents();
    expect(topLevelLabels[0]).toContain('Когда-нибудь');

    // 1. Create and rename an empty top-level section.
    await page.getByRole('button', { name: 'Добавить раздел' }).click();
    await page.getByLabel('Название').fill('Черновики');
    await page.getByRole('button', { name: 'Сохранить' }).click();
    await expect(page.getByRole('button', { name: 'Черновики' })).toBeVisible();
    expect(mockApi.requests('POST', '/api/section').at(-1)?.body).toEqual({
      title: 'Черновики',
      parent_id: ids.root
    });

    await openSectionAction(page, 'Черновики', 'Переименовать');
    await page.getByLabel('Название').fill('Идеи');
    await page.getByRole('button', { name: 'Сохранить' }).click();
    await expect(page.getByRole('button', { name: 'Идеи' })).toBeVisible();

    // Move it under Projects, then collapse and expand that branch.
    await openSectionAction(page, 'Идеи', 'Переместить');
    await page.getByLabel('Родительский раздел').selectOption(ids.projects);
    await page.getByRole('button', { name: 'Сохранить' }).click();
    expect(mockApi.requests('POST', '/api/section/move').at(-1)?.body).toMatchObject({
      to_parent_id: ids.projects,
      index: 0
    });

    const projects = page.locator('.section-link').filter({ hasText: 'Проекты' }).first();
    await projects.locator('.section-toggle').click();
    await expect(page.getByRole('button', { name: 'Идеи' })).toHaveCount(0);
    await projects.locator('.section-toggle').click();
    await expect(page.getByRole('button', { name: 'Идеи' })).toBeVisible();

    // Delete the selected section and fall back to the first remaining leaf.
    await page.getByRole('button', { name: 'Идеи' }).click();
    await expect(page.getByRole('heading', { name: 'Идеи' })).toBeVisible();
    await openSectionAction(page, 'Идеи', 'Удалить');
    await expect(page.getByText('Можно удалить только пустой раздел без подразделов.')).toBeVisible();
    await page.getByRole('button', { name: 'Удалить' }).click();

    await expect(page.getByRole('button', { name: 'Идеи' })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Когда-нибудь' })).toBeVisible();
  });
});
