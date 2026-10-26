export type RecurrenceType = 'days' | 'weekdays' | 'weeks' | 'months' | 'years';

export interface RecurrenceInfo {
  period: number;
  type: RecurrenceType;
  flexible_mode: boolean;
}

export interface Task {
  id: string;
  section_id: string;
  parent_task_id: string | null;
  title: string;
  description: string | null;
  content: string | null;
  is_completed: boolean;
  is_archived: boolean;
  added_at: string;
  due_to: string | null;
  due_time: string | null;
  recurrence: RecurrenceInfo | null;
}

export interface Section {
  id: string;
  title: string;
  parent_id: string | null;
  added_at: string;
  subsections: Section[];
  tasks: Task[];
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface TaskDraft {
  title: string;
  description: string;
  due_to: string | null;
  due_time: string | null;
  recurrence: RecurrenceInfo | null;
}
