import { expect, test as base, type Page, type Route } from '@playwright/test';
import type { Section, Task, User } from '../src/lib/types';

export { expect };

export const FIXED_NOW = new Date('2026-10-25T12:00:00+03:00');

export const ids = {
  root: '00000000-0000-4000-8000-000000000001',
  inbox: '00000000-0000-4000-8000-000000000002',
  projects: '00000000-0000-4000-8000-000000000003',
  planty: '00000000-0000-4000-8000-000000000004',
  someday: '00000000-0000-4000-8000-000000000005',
  todayTask: '10000000-0000-4000-8000-000000000001',
  tomorrowTask: '10000000-0000-4000-8000-000000000002',
  overdueTask: '10000000-0000-4000-8000-000000000003',
  futureTask: '10000000-0000-4000-8000-000000000004',
  archivedTask: '10000000-0000-4000-8000-000000000005',
  projectTask: '10000000-0000-4000-8000-000000000006'
} as const;

type JsonObject = Record<string, unknown>;

export interface RecordedRequest {
  method: string;
  path: string;
  query: URLSearchParams;
  body: JsonObject | null;
}

export interface MockFailure {
  status: number;
  detail?: string;
  contentType?: string;
}

export interface MockState {
  authenticated: boolean;
  user: User;
  root: Section;
  tasks: Task[];
  requests: RecordedRequest[];
  failures: Map<string, MockFailure[]>;
  nextSection: number;
  nextTask: number;
}

function section(id: string, title: string, parentId: string | null, subsections: Section[] = []): Section {
  return {
    id,
    title,
    parent_id: parentId,
    added_at: '2026-10-20T10:00:00',
    subsections,
    tasks: []
  };
}

function task(overrides: Partial<Task> & Pick<Task, 'id' | 'section_id' | 'title'>): Task {
  return {
    parent_task_id: null,
    description: null,
    content: null,
    is_completed: false,
    is_archived: false,
    added_at: '2026-10-20T10:00:00',
    due_to: null,
    recurrence: null,
    ...overrides
  };
}

function initialState(): MockState {
  const planty = section(ids.planty, '☘️ Planty', ids.projects);
  const projects = section(ids.projects, 'Проекты', ids.root, [planty]);
  const inbox = section(ids.inbox, '📥 Inbox', ids.root);
  const someday = section(ids.someday, 'Когда-нибудь', ids.root);

  return {
    authenticated: true,
    user: {
      id: '20000000-0000-4000-8000-000000000001',
      email: 'user@example.ru',
      is_active: true,
      is_superuser: false,
      is_verified: true
    },
    root: section(ids.root, '[System] Root section', null, [inbox, projects, someday]),
    tasks: [
      task({
        id: ids.todayTask,
        section_id: ids.inbox,
        title: 'Разобрать GTD',
        description: 'Собрать всё в одном месте',
        due_to: '2026-10-25',
        recurrence: { period: 1, type: 'days', flexible_mode: false }
      }),
      task({
        id: ids.tomorrowTask,
        section_id: ids.inbox,
        title: 'Сходить в зал',
        description: 'Силовая тренировка',
        due_to: '2026-10-26'
      }),
      task({
        id: ids.overdueTask,
        section_id: ids.inbox,
        title: 'Просроченная задача',
        due_to: '2026-10-24'
      }),
      task({
        id: ids.futureTask,
        section_id: ids.inbox,
        title: 'Задача на будущее',
        due_to: '2026-11-01'
      }),
      task({
        id: ids.archivedTask,
        section_id: ids.inbox,
        title: 'Архивная задача',
        is_completed: true,
        is_archived: true
      }),
      task({
        id: ids.projectTask,
        section_id: ids.planty,
        title: 'Допилить интерфейс'
      })
    ],
    requests: [],
    failures: new Map(),
    nextSection: 1,
    nextTask: 1
  };
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function allSections(root: Section): Section[] {
  return [root, ...root.subsections.flatMap(allSections)];
}

function findSection(root: Section, id: string): Section | undefined {
  return allSections(root).find((candidate) => candidate.id === id);
}

function removeSection(root: Section, id: string): Section | undefined {
  for (const parent of allSections(root)) {
    const index = parent.subsections.findIndex((candidate) => candidate.id === id);
    if (index >= 0) return parent.subsections.splice(index, 1)[0];
  }
  return undefined;
}

function publicSection(value: Section, tasks: Task[] = []): Section {
  return {
    ...clone(value),
    subsections: value.subsections.map((child) => publicSection(child)),
    tasks: clone(tasks)
  };
}

async function requestBody(route: Route): Promise<JsonObject | null> {
  const request = route.request();
  const data = request.postData();
  if (!data) return null;
  if (request.headers()['content-type']?.includes('application/x-www-form-urlencoded')) {
    return Object.fromEntries(new URLSearchParams(data));
  }
  return request.postDataJSON() as JsonObject;
}

async function fulfillJson(route: Route, data: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(data) });
}

async function fulfillEmpty(route: Route, status = 204): Promise<void> {
  await route.fulfill({ status, body: '' });
}

export class MockApi {
  readonly state = initialState();

  constructor(private readonly page: Page) {}

  async install(): Promise<void> {
    await this.page.route('**/api/**', async (route) => this.handle(route));
  }

  async open(path = '/'): Promise<void> {
    await this.page.goto(path);
    if (this.state.authenticated && !path.startsWith('/login')) {
      await this.page.getByRole('button', { name: 'Выйти' }).waitFor();
      await this.page.locator('.loading').waitFor({ state: 'detached' });
    }
  }

  failOnce(method: string, path: string, failure: MockFailure): void {
    const key = `${method.toUpperCase()} ${path}`;
    this.state.failures.set(key, [...(this.state.failures.get(key) ?? []), failure]);
  }

  requests(method: string, path: string): RecordedRequest[] {
    return this.state.requests.filter(
      (request) => request.method === method.toUpperCase() && request.path === path
    );
  }

  private async handle(route: Route): Promise<void> {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();
    const body = await requestBody(route);
    this.state.requests.push({ method, path: url.pathname, query: url.searchParams, body });

    const failureKey = `${method} ${url.pathname}`;
    const failures = this.state.failures.get(failureKey);
    const failure = failures?.shift();
    if (failure) {
      if (failure.contentType === 'text/plain') {
        await route.fulfill({ status: failure.status, contentType: 'text/plain', body: failure.detail ?? '' });
      } else {
        await fulfillJson(route, { detail: failure.detail ?? 'Mock API failure' }, failure.status);
      }
      return;
    }

    if (url.pathname === '/api/auth/me' && method === 'GET') {
      if (this.state.authenticated) await fulfillJson(route, this.state.user);
      else await fulfillJson(route, { detail: 'Unauthorized' }, 401);
      return;
    }
    if (url.pathname === '/api/auth/login' && method === 'POST') {
      this.state.authenticated = true;
      await fulfillEmpty(route);
      return;
    }
    if (url.pathname === '/api/auth/register' && method === 'POST') {
      await fulfillJson(route, this.state.user, 201);
      return;
    }
    if (url.pathname === '/api/auth/logout' && method === 'POST') {
      this.state.authenticated = false;
      await fulfillEmpty(route);
      return;
    }
    if (url.pathname === '/api/sections' && method === 'GET') {
      await fulfillJson(route, [publicSection(this.state.root)]);
      return;
    }

    const sectionMatch = url.pathname.match(/^\/api\/section\/([^/]+)$/);
    if (sectionMatch && method === 'GET') {
      const found = findSection(this.state.root, sectionMatch[1]);
      if (!found) {
        await fulfillJson(route, { detail: 'Section not found' }, 404);
        return;
      }
      const tasks = this.state.tasks.filter(
        (candidate) => candidate.section_id === found.id && !candidate.is_archived
      );
      await fulfillJson(route, publicSection(found, tasks));
      return;
    }

    if (url.pathname === '/api/section' && method === 'POST') {
      const id = `30000000-0000-4000-8000-${String(this.state.nextSection++).padStart(12, '0')}`;
      const parent = findSection(this.state.root, String(body?.parent_id));
      if (!parent) {
        await fulfillJson(route, { detail: 'Parent not found' }, 404);
        return;
      }
      parent.subsections.push(section(id, String(body?.title), parent.id));
      await fulfillJson(route, { id }, 201);
      return;
    }
    if (url.pathname === '/api/section' && method === 'PATCH') {
      const found = findSection(this.state.root, String(body?.id));
      if (!found) {
        await fulfillJson(route, { detail: 'Section not found' }, 404);
        return;
      }
      found.title = String(body?.title);
      await fulfillJson(route, { section: publicSection(found) });
      return;
    }
    if (url.pathname === '/api/section' && method === 'DELETE') {
      removeSection(this.state.root, String(body?.section_id));
      await fulfillEmpty(route);
      return;
    }
    if (url.pathname === '/api/section/move' && method === 'POST') {
      const moved = removeSection(this.state.root, String(body?.section_id));
      const parent = findSection(this.state.root, String(body?.to_parent_id));
      if (!moved || !parent) {
        await fulfillJson(route, { detail: 'Section not found' }, 404);
        return;
      }
      moved.parent_id = parent.id;
      parent.subsections.splice(Number(body?.index ?? 0), 0, moved);
      await fulfillEmpty(route);
      return;
    }

    if (url.pathname === '/api/task' && method === 'POST') {
      const id = `40000000-0000-4000-8000-${String(this.state.nextTask++).padStart(12, '0')}`;
      this.state.tasks.push(task({
        id,
        section_id: String(body?.section_id),
        parent_task_id: body?.parent_task_id ? String(body.parent_task_id) : null,
        title: String(body?.title),
        description: String(body?.description ?? ''),
        due_to: body?.due_to ? String(body.due_to) : null,
        recurrence: (body?.recurrence as Task['recurrence']) ?? null
      }));
      await fulfillJson(route, { id }, 201);
      return;
    }
    if (url.pathname === '/api/task' && method === 'PATCH') {
      const found = this.state.tasks.find((candidate) => candidate.id === body?.id);
      if (!found) {
        await fulfillJson(route, { detail: 'Task not found' }, 404);
        return;
      }
      Object.assign(found, body);
      await fulfillJson(route, { task: clone(found) });
      return;
    }
    if (url.pathname === '/api/task' && method === 'DELETE') {
      const index = this.state.tasks.findIndex((candidate) => candidate.id === body?.task_id);
      if (index >= 0) this.state.tasks.splice(index, 1);
      await fulfillEmpty(route);
      return;
    }
    if (url.pathname === '/api/task/move' && method === 'POST') {
      const currentIndex = this.state.tasks.findIndex((candidate) => candidate.id === body?.task_id);
      const moved = this.state.tasks[currentIndex];
      if (!moved) {
        await fulfillJson(route, { detail: 'Task not found' }, 404);
        return;
      }
      this.state.tasks.splice(currentIndex, 1);
      moved.section_id = String(body?.section_to_id);
      moved.parent_task_id = body?.parent_task_id ? String(body.parent_task_id) : null;
      const sectionTasks = this.state.tasks.filter(
        (candidate) => candidate.section_id === moved.section_id && !candidate.is_archived
      );
      const target = sectionTasks[Number(body?.index ?? 0)];
      const insertionIndex = target ? this.state.tasks.indexOf(target) : this.state.tasks.length;
      this.state.tasks.splice(insertionIndex, 0, moved);
      await fulfillEmpty(route);
      return;
    }
    if (url.pathname === '/api/task/toggle_completed' && method === 'POST') {
      const found = this.state.tasks.find((candidate) => candidate.id === body?.task_id);
      if (found) found.is_completed = !found.is_completed;
      await fulfillJson(route, {});
      return;
    }
    if (url.pathname === '/api/task/toggle_archived' && method === 'POST') {
      const found = this.state.tasks.find((candidate) => candidate.id === body?.task_id);
      if (found) found.is_archived = !found.is_archived;
      await fulfillJson(route, {});
      return;
    }
    if (url.pathname === '/api/task/search' && method === 'GET') {
      const query = (url.searchParams.get('query') ?? '').toLocaleLowerCase('ru-RU');
      const found = this.state.tasks.filter((candidate) =>
        !candidate.is_archived
        && `${candidate.title} ${candidate.description ?? ''}`.toLocaleLowerCase('ru-RU').includes(query)
      );
      await fulfillJson(route, found);
      return;
    }
    if (url.pathname === '/api/task/by_date' && method === 'GET') {
      const from = url.searchParams.get('not_before') ?? '';
      const to = url.searchParams.get('not_after') ?? '';
      const dated = this.state.tasks.filter((candidate) => candidate.due_to && !candidate.is_archived);
      const overdue = dated.filter((candidate) => candidate.due_to! < from);
      const dates = [...new Set(
        dated.filter((candidate) => candidate.due_to! >= from && candidate.due_to! <= to)
          .map((candidate) => candidate.due_to!)
      )].sort();
      await fulfillJson(route, {
        by_dates: dates.map((date) => ({
          date,
          tasks: dated.filter((candidate) => candidate.due_to === date)
        })),
        overdue
      });
      return;
    }
    if (url.pathname === '/api/tasks/archived' && method === 'GET') {
      await fulfillJson(route, {
        title: 'Archived tasks',
        tasks: this.state.tasks.filter((candidate) => candidate.is_archived)
      });
      return;
    }

    await fulfillJson(route, { detail: `Unhandled mock route: ${method} ${url.pathname}` }, 501);
  }
}

export const test = base.extend<{ mockApi: MockApi }>({
  mockApi: async ({ page }, use) => {
    await page.clock.setFixedTime(FIXED_NOW);
    const mockApi = new MockApi(page);
    await mockApi.install();
    await use(mockApi);
  }
});
