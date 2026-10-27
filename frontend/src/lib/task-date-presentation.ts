import { getLocale, t } from './i18n.svelte';

export interface TaskDatePresentation {
  text: string;
  className: 'overdue' | 'today' | 'tomorrow' | 'weekday' | 'future';
}

function absoluteDate(value: string, now: Date, weekday = false): string {
  const due = new Date(`${value}T12:00:00`);
  const locale = getLocale() === 'ru' ? 'ru-RU' : 'en-US';
  const text = due.toLocaleDateString(locale, {
    ...(weekday ? { weekday: 'long' as const } : {}),
    day: 'numeric',
    month: 'long',
    ...(due.getFullYear() === now.getFullYear() ? {} : { year: 'numeric' as const })
  });
  return locale === 'ru-RU' ? text.replace(/\s+г\.$/u, '') : text;
}

export function calendarDateHeading(value: string, now = new Date()): string {
  return absoluteDate(value, now, true);
}

export function taskDatePresentation(value: string, now = new Date()): TaskDatePresentation {
  const due = new Date(`${value}T12:00:00`);
  const today = new Date(now);
  today.setHours(12, 0, 0, 0);
  const diff = Math.round((due.getTime() - today.getTime()) / 86400000);
  const locale = getLocale() === 'ru' ? 'ru-RU' : 'en-US';
  if (diff < 0) return { text: absoluteDate(value, now), className: 'overdue' };
  if (diff === 0) return { text: t('today'), className: 'today' };
  if (diff === 1) return { text: t('tomorrow'), className: 'tomorrow' };
  if (diff < 7) return { text: due.toLocaleDateString(locale, { weekday: 'long' }), className: 'weekday' };
  return { text: absoluteDate(value, now), className: 'future' };
}
