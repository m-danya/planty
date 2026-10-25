import { expect, test, type Page, type Route } from '@playwright/test';

const rootId = '00000000-0000-4000-8000-000000000001';
const sectionId = '00000000-0000-4000-8000-000000000002';
const taskId = '00000000-0000-4000-8000-000000000003';

const task = {
  id: taskId, section_id: sectionId, parent_task_id: null, title: 'Разобрать GTD', description: 'Собрать всё в одном месте',
  content: null, is_completed: false, is_archived: false, added_at: '2026-10-25T10:00:00', due_to: '2026-10-25',
  recurrence: { period: 1, type: 'days', flexible_mode: false }
};
const secondTask = {
  ...task, id: '00000000-0000-4000-8000-000000000004', title: 'Сходить в зал',
  description: 'Силовая тренировка', due_to: '2026-10-26', recurrence: null
};
const leaf = { id: sectionId, title: '📥 Inbox', parent_id: rootId, added_at: '2026-10-25T10:00:00', subsections: [], tasks: [] };
const root = { id: rootId, title: '[System] Root section', parent_id: null, added_at: '2026-10-25T10:00:00', subsections: [leaf], tasks: [] };

async function json(route: Route, data: unknown, status = 200) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(data) });
}

async function mockApp(page: Page) {
  await page.route('**/api/auth/me', (route) => json(route, { id: 'u1', email: 'user@example.ru', is_active: true, is_superuser: false, is_verified: true }));
  await page.route('**/api/sections', (route) => json(route, [root]));
  await page.route(`**/api/section/${sectionId}`, (route) => json(route, { ...leaf, tasks: [task, secondTask] }));
  await page.route('**/api/task/**', (route) => json(route, { ...leaf, tasks: [task] }));
  await page.route('**/api/task/search**', (route) => json(route, [task]));
  await page.route('**/api/task/by_date**', (route) => json(route, { by_dates: [{ date: '2026-10-25', tasks: [task] }], overdue: [] }));
  await page.route('**/api/tasks/archived', (route) => json(route, { title: 'Archived tasks', tasks: [] }));
  await page.route('**/api/task', async (route) => {
    if (route.request().method() === 'POST') return json(route, { id: 'new-id' }, 201);
    if (route.request().method() === 'PATCH') return json(route, { task });
    return route.fulfill({ status: 204 });
  });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '📥 Inbox' })).toBeVisible();
}

test('login screen is usable and switches to registration', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => json(route, { detail: 'Unauthorized' }, 401));
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: 'С возвращением' })).toBeVisible();
  await expect(page.getByLabel('Email')).toBeVisible();
  await page.getByRole('button', { name: 'Создать аккаунт' }).click();
  await expect(page.getByRole('heading', { name: 'Создать аккаунт' })).toBeVisible();
});

test('Q shortcut opens the unified task composer', async ({ page }) => {
  await mockApp(page);
  await page.keyboard.press('q');
  await expect(page.getByTestId('new-task')).toBeVisible();
  await expect(page.getByLabel('Название задачи')).toBeFocused();
});

test('Russian Й shortcut also opens the composer', async ({ page }) => {
  await mockApp(page);
  await page.evaluate(() => document.body.dispatchEvent(new KeyboardEvent('keydown', { key: 'й', code: 'KeyQ', bubbles: true })));
  await expect(page.getByTestId('new-task')).toBeVisible();
});

test('date phrase is recognized and highlighted', async ({ page }) => {
  await mockApp(page);
  await page.keyboard.press('q');
  await page.getByLabel('Название задачи').fill('собраться с друзьями каждые 3 дня начиная завтра');
  await expect(page.locator('.composer-highlight mark')).toContainText('каждые 3 дня начиная завтра');
  await expect(page.locator('.date-chip')).toBeVisible();
});

test('Enter creates a task with parsed title, date and recurrence', async ({ page }) => {
  await mockApp(page);
  let payload: Record<string, unknown> | undefined;
  await page.route('**/api/task', async (route) => {
    payload = route.request().postDataJSON();
    await json(route, { id: 'new-id' }, 201);
  });
  await page.keyboard.press('q');
  await page.getByLabel('Название задачи').fill('полить цветы каждые 3 дня начиная завтра');
  await page.getByLabel('Название задачи').press('Enter');
  await expect.poll(() => payload).toMatchObject({
    title: 'полить цветы', due_to: expect.any(String),
    recurrence: { period: 3, type: 'days', flexible_mode: false }
  });
});

test('plain click does nothing and Alt-click opens editing', async ({ page }) => {
  await mockApp(page);
  const row = page.getByTestId('task-row').first();
  await row.click();
  await expect(page.getByTestId('edit-task')).toHaveCount(0);
  await row.click({ modifiers: ['Alt'] });
  await expect(page.getByTestId('edit-task')).toBeVisible();
  await expect(page.getByLabel('Название задачи')).toHaveValue('Разобрать GTD');
});

test('context menu contains move and archive actions', async ({ page }) => {
  await mockApp(page);
  await page.getByTestId('task-row').first().click({ button: 'right' });
  await expect(page.getByRole('menuitem', { name: 'В другой раздел' })).toBeVisible();
  await expect(page.getByRole('menuitem', { name: 'В архив' })).toBeVisible();
});

test('dragging onto a task sends a subtask move', async ({ page }) => {
  await mockApp(page);
  let payload: Record<string, unknown> | undefined;
  await page.route('**/api/task/move', async (route) => {
    payload = route.request().postDataJSON();
    await route.fulfill({ status: 204 });
  });
  const rows = page.getByTestId('task-row');
  await rows.nth(1).dragTo(rows.nth(0));
  await expect.poll(() => payload).toMatchObject({
    task_id: secondTask.id, section_to_id: sectionId, parent_task_id: task.id
  });
});

test('dragging to the top edge reorders beside a task', async ({ page }) => {
  await mockApp(page);
  let payload: Record<string, unknown> | undefined;
  await page.route('**/api/task/move', async (route) => {
    payload = route.request().postDataJSON();
    await route.fulfill({ status: 204 });
  });
  const rows = page.getByTestId('task-row');
  const targetBox = await rows.nth(0).boundingBox();
  if (!targetBox) throw new Error('Target task is not visible');
  const transfer = await page.evaluateHandle(() => new DataTransfer());
  await rows.nth(1).dispatchEvent('dragstart', { dataTransfer: transfer });
  await rows.nth(0).dispatchEvent('dragover', {
    dataTransfer: transfer,
    clientY: targetBox.y + 1
  });
  await rows.nth(0).dispatchEvent('drop', {
    dataTransfer: transfer,
    clientY: targetBox.y + 1
  });
  await expect.poll(() => payload).toMatchObject({
    task_id: secondTask.id, section_to_id: sectionId, parent_task_id: null
  });
});

test('a section can be created from the sidebar', async ({ page }) => {
  await mockApp(page);
  let payload: Record<string, unknown> | undefined;
  await page.route('**/api/section', async (route) => {
    payload = route.request().postDataJSON();
    await json(route, { id: 'new-section' }, 201);
  });
  await page.getByRole('button', { name: 'Добавить раздел' }).click();
  await page.getByLabel('Название').fill('Новый проект');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await expect.poll(() => payload).toMatchObject({ title: 'Новый проект', parent_id: rootId });
});

test('section actions open from the visible ellipsis button', async ({ page }) => {
  await mockApp(page);
  const sectionLink = page.locator('.section-link', { hasText: 'Inbox' });
  await sectionLink.hover();
  await sectionLink.locator('.section-more').click();
  await expect(page.getByRole('menuitem', { name: 'Переименовать' })).toBeVisible();
  await expect(page.getByRole('menuitem', { name: 'Переместить' })).toBeVisible();
  await expect(page.getByRole('menuitem', { name: 'Удалить' })).toBeVisible();
});

test('search and calendar navigation load their views', async ({ page }) => {
  await mockApp(page);
  await page.getByRole('button', { name: /Поиск/ }).click();
  await page.getByLabel('Поиск по задачам').fill('GTD');
  await expect(page.getByText('Разобрать GTD')).toBeVisible();
  await page.getByRole('button', { name: 'Календарь' }).click();
  await expect(page.getByRole('heading', { name: 'Календарь' })).toBeVisible();
});

test('mobile layout exposes the sidebar from the menu button', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockApp(page);
  await page.getByRole('button', { name: 'Открыть меню' }).click();
  await expect(page.locator('.sidebar')).toHaveClass(/open/);
});
