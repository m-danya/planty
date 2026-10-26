import { expect, ids, test } from './fixtures';
import type { Locator } from '@playwright/test';

async function expectTooltipToTheRight(title: Locator, tooltip: Locator) {
  const titleBox = await title.boundingBox();
  const tooltipBox = await tooltip.boundingBox();
  expect(titleBox).not.toBeNull();
  expect(tooltipBox).not.toBeNull();
  expect(tooltipBox!.x - (titleBox!.x + titleBox!.width)).toBeGreaterThanOrEqual(6);
  expect(tooltipBox!.x - (titleBox!.x + titleBox!.width)).toBeLessThanOrEqual(11);
  const centerDelta = tooltipBox!.y + tooltipBox!.height / 2 - (titleBox!.y + titleBox!.height / 2);
  expect(centerDelta).toBeGreaterThanOrEqual(1);
  expect(centerDelta).toBeLessThanOrEqual(4);
}

test.describe('Sections', () => {
  test('section-aggregate-views', async ({ page, mockApi }) => {
    await mockApi.open(`/?section=${ids.projects}`);

    // 1. A parent section collects tasks from every descendant leaf section.
    await expect(page.getByRole('heading', { name: 'Проекты', exact: true })).toBeVisible();
    const subsectionView = page.getByTestId('section-subsections');
    await expect(subsectionView).toBeVisible();
    await expect(subsectionView.getByTestId('section-group')).toHaveCount(2);
    await expect(subsectionView.getByRole('heading', { name: '☘️ Planty' })).toBeVisible();
    await expect(subsectionView.getByRole('heading', { name: 'Дом' })).toBeVisible();
    await expect(subsectionView.getByText('Допилить интерфейс', { exact: true })).toBeVisible();
    await expect(subsectionView.getByText('Купить растения', { exact: true })).toBeVisible();
    await expect(subsectionView.locator('.subsection-task-count')).toHaveCount(0);

    const sectionTooltip = page.getByTestId('section-task-tooltip');
    await expect(sectionTooltip).toBeHidden();
    await page.locator('.page-title').hover();
    await expect(sectionTooltip).toBeVisible();
    await expect(sectionTooltip).toHaveText('2 задачи');
    await expectTooltipToTheRight(page.locator('.page-title h1'), sectionTooltip);

    // Editing stays in the task's own descendant section instead of jumping above the page.
    const homeGroup = subsectionView.getByTestId('section-group').filter({ has: page.getByRole('heading', { name: 'Дом' }) });
    await homeGroup.getByTestId('task-row').click({ modifiers: ['Alt'] });
    await expect(homeGroup.locator('.inline-edit > [data-testid="edit-task"]')).toBeVisible();
    await page.getByRole('button', { name: 'Отменить' }).click();

    // 2. Board mode uses the same task component and persists per parent section.
    await page.getByRole('button', { name: 'Показать как доску' }).click();
    const board = page.getByTestId('section-board');
    await expect(board).toBeVisible();
    await expect(board.getByTestId('section-group')).toHaveCount(2);
    await expect(board.locator('.task-card')).toHaveCount(2);
    const plantyColumn = board.getByTestId('section-group').filter({ has: page.getByRole('heading', { name: '☘️ Planty' }) });
    const plantyTooltip = plantyColumn.locator('.task-count-tooltip');
    await expect(plantyTooltip).toBeHidden();
    await plantyColumn.locator('.subsection-title').hover();
    await expect(plantyTooltip).toBeVisible();
    await expect(plantyTooltip).toHaveText('1 задача');
    await expectTooltipToTheRight(plantyColumn.locator('.subsection-title h2'), plantyTooltip);
    await expect.poll(() => page.evaluate((sectionId) => {
      const layouts = JSON.parse(localStorage.getItem('planty.sectionLayouts') ?? '{}');
      return layouts[sectionId];
    }, ids.projects)).toBe('board');

    const homeColumn = board.getByTestId('section-group').filter({ has: page.getByRole('heading', { name: 'Дом' }) });
    await homeColumn.getByRole('button', { name: 'Добавить задачу' }).click();
    await homeColumn.getByLabel('Название задачи').fill('Пересадить фикус');
    await homeColumn.getByLabel('Название задачи').press('Enter');
    expect(mockApi.requests('POST', '/api/task').at(-1)?.body).toMatchObject({
      section_id: ids.home,
      title: 'Пересадить фикус'
    });
    await expect(homeColumn.getByText('Пересадить фикус', { exact: true })).toBeVisible();

    await page.reload();
    await expect(page.getByTestId('section-board')).toBeVisible();
    await page.getByRole('button', { name: 'Показать подразделами' }).click();
    await expect(page.getByTestId('section-subsections')).toBeVisible();

    // 3. Parent sections remember opposite layouts independently.
    await page.getByRole('button', { name: 'Сферы' }).click();
    await expect(page.getByTestId('section-subsections')).toBeVisible();
    await page.getByRole('button', { name: 'Показать как доску' }).click();
    await expect(page.getByTestId('section-board')).toBeVisible();

    await page.getByRole('button', { name: 'Проекты' }).click();
    await expect(page.getByTestId('section-subsections')).toBeVisible();
    await page.reload();
    await expect(page.getByTestId('section-subsections')).toBeVisible();

    await page.getByRole('button', { name: 'Сферы' }).click();
    await expect(page.getByTestId('section-board')).toBeVisible();
    await page.reload();
    await expect(page.getByTestId('section-board')).toBeVisible();
    expect(await page.evaluate(() => JSON.parse(localStorage.getItem('planty.sectionLayouts') ?? '{}'))).toMatchObject({
      [ids.projects]: 'subsections',
      [ids.areas]: 'board'
    });
  });
});
