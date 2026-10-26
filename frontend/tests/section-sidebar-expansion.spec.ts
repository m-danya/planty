import { expect, ids, test } from './fixtures';

test.describe('Sections', () => {
  test('section-sidebar-expansion', async ({ page, mockApi }) => {
    await mockApi.open('/');

    const projectsToggle = page.locator(`[data-section-id="${ids.projects}"] > .section-link > .section-toggle`);
    const areasToggle = page.locator(`[data-section-id="${ids.areas}"] > .section-link > .section-toggle`);

    // 1. Nested expansion states are saved independently and survive reload.
    await areasToggle.click();
    await expect(areasToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(page.getByRole('button', { name: 'Дом' })).toHaveCount(0);

    await projectsToggle.click();
    await expect(projectsToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(page.getByRole('button', { name: 'Сферы' })).toHaveCount(0);
    await page.reload();
    await expect(page.locator(`[data-section-id="${ids.projects}"] > .section-link > .section-toggle`)).toHaveAttribute('aria-expanded', 'false');

    // 2. Expanding the parent does not expand its still-collapsed child.
    const reloadedProjectsToggle = page.locator(`[data-section-id="${ids.projects}"] > .section-link > .section-toggle`);
    await reloadedProjectsToggle.click();
    await expect(page.getByRole('button', { name: 'Сферы' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Дом' })).toHaveCount(0);

    const reloadedAreasToggle = page.locator(`[data-section-id="${ids.areas}"] > .section-link > .section-toggle`);
    await expect(reloadedAreasToggle).toHaveAttribute('aria-expanded', 'false');
    await reloadedAreasToggle.click();
    await expect(page.getByRole('button', { name: 'Дом' })).toBeVisible();

    await page.reload();
    await expect(page.locator(`[data-section-id="${ids.projects}"] > .section-link > .section-toggle`)).toHaveAttribute('aria-expanded', 'true');
    await expect(page.locator(`[data-section-id="${ids.areas}"] > .section-link > .section-toggle`)).toHaveAttribute('aria-expanded', 'true');
    await expect(page.getByRole('button', { name: 'Дом' })).toBeVisible();
    expect(await page.evaluate(() => JSON.parse(localStorage.getItem('planty.sectionExpansion') ?? '{}'))).toMatchObject({
      [ids.projects]: true,
      [ids.areas]: true
    });
  });
});
