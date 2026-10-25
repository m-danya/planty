import type { Section, Task, TaskDraft, User } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set('Content-Type', 'application/json');
  }
  const response = await fetch(`/api${path}`, {
    ...options,
    headers,
    credentials: 'include'
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    } catch {
      // Keep the HTTP status text for non-JSON errors.
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return undefined as T;
  }
  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const api = {
  me: () => request<User>('/auth/me'),
  login: (email: string, password: string) =>
    request<void>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password })
    }),
  register: (email: string, password: string) =>
    request<User>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) }),
  logout: () => request<void>('/auth/logout', { method: 'POST' }),
  sections: () => request<Section[]>('/sections'),
  section: (id: string) => request<Section>(`/section/${id}`),
  createSection: (title: string, parent_id: string) =>
    request<{ id: string }>('/section', { method: 'POST', body: JSON.stringify({ title, parent_id }) }),
  updateSection: (id: string, title: string) =>
    request<{ section: Section }>('/section', { method: 'PATCH', body: JSON.stringify({ id, title }) }),
  moveSection: (section_id: string, to_parent_id: string, index: number) =>
    request<void>('/section/move', { method: 'POST', body: JSON.stringify({ section_id, to_parent_id, index }) }),
  deleteSection: (section_id: string) =>
    request<void>('/section', { method: 'DELETE', body: JSON.stringify({ section_id }) }),
  createTask: (section_id: string, draft: TaskDraft, parent_task_id: string | null = null) =>
    request<{ id: string }>('/task', {
      method: 'POST',
      body: JSON.stringify({ section_id, parent_task_id, ...draft })
    }),
  updateTask: (id: string, draft: TaskDraft) =>
    request<{ task: Task }>('/task', { method: 'PATCH', body: JSON.stringify({ id, ...draft }) }),
  deleteTask: (task_id: string) =>
    request<void>('/task', { method: 'DELETE', body: JSON.stringify({ task_id }) }),
  moveTask: (task_id: string, section_to_id: string, index: number, parent_task_id: string | null) =>
    request<void>('/task/move', {
      method: 'POST',
      body: JSON.stringify({ task_id, section_to_id, index, parent_task_id })
    }),
  toggleTask: (task_id: string) =>
    request<Section>('/task/toggle_completed', {
      method: 'POST',
      body: JSON.stringify({ task_id, auto_archive: false })
    }),
  archiveTask: (task_id: string) =>
    request<Section>('/task/toggle_archived', { method: 'POST', body: JSON.stringify({ task_id }) }),
  search: (query: string) => request<Task[]>(`/task/search?query=${encodeURIComponent(query)}`),
  calendar: (from: string, to: string) =>
    request<{ by_dates: { date: string; tasks: Task[] }[]; overdue: Task[] }>(
      `/task/by_date?not_before=${from}&not_after=${to}&with_overdue=true`
    ),
  archived: () => request<{ title: string; tasks: Task[] }>('/tasks/archived')
};
