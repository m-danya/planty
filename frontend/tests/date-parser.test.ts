import { describe, expect, it } from 'vitest';
import { parseTaskText, recurrenceLabel, toDraft } from '../src/lib/date-parser';

const now = new Date(2026, 9, 25, 12);

describe('natural-language date parser', () => {
  it.each([
    ['Позвонить маме завтра', 'Позвонить маме', '2026-10-26'],
    ['call Alex tomorrow', 'call Alex', '2026-10-26'],
    ['Закончить отчёт сегодня', 'Закончить отчёт', '2026-10-25'],
    ['Подготовиться послезавтра', 'Подготовиться', '2026-10-27'],
    ['prepare day after tomorrow', 'prepare', '2026-10-27'],
    ['Встреча 03.11.2026', 'Встреча', '2026-11-03'],
    ['Встреча 03/11', 'Встреча', '2026-11-03'],
    ['Встреча 03-11-27', 'Встреча', '2027-11-03'],
    ['День рождения 7 ноября', 'День рождения', '2026-11-07'],
    ['release 7 nov 2027', 'release', '2027-11-07'],
    ['deploy next monday', 'deploy', '2026-10-26'],
    ['созвон в следующий четверг', 'созвон', '2026-10-29'],
    ['Ответить через 3 дня', 'Ответить', '2026-10-28'],
    ['review in 2 weeks', 'review', '2026-11-08'],
    ['renew через 2 месяца', 'renew', '2026-12-25'],
    ['renew in 1 year', 'renew', '2027-10-25'],
    ['план на следующую неделю', 'план', '2026-11-01'],
    ['budget next month', 'budget', '2026-11-25'],
    ['цели на следующий год', 'цели', '2027-10-25']
  ])('parses %s', (input, title, dueTo) => {
    expect(parseTaskText(input, now)).toMatchObject({ cleanTitle: title, dueTo });
  });

  it.each([
    ['читать каждый день начиная завтра', 'читать', '2026-10-26', 1, 'days'],
    ['сделать уборку каждые 3 дня начиная завтра', 'сделать уборку', '2026-10-26', 3, 'days'],
    ['plan review every 2 weeks starting tomorrow', 'plan review', '2026-10-26', 2, 'weeks'],
    ['читать every day', 'читать', '2026-10-25', 1, 'days'],
    ['отчёт еженедельно', 'отчёт', '2026-10-25', 1, 'weeks'],
    ['оплатить счета ежемесячно', 'оплатить счета', '2026-10-25', 1, 'months'],
    ['check monthly', 'check', '2026-10-25', 1, 'months'],
    ['annual check yearly', 'annual check', '2026-10-25', 1, 'years'],
    ['осмотр ежегодно', 'осмотр', '2026-10-25', 1, 'years'],
    ['стендап каждый понедельник', 'стендап', '2026-10-26', 1, 'weeks'],
    ['итоги каждую пятницу', 'итоги', '2026-10-30', 1, 'weeks'],
    ['разобрать почту каждый будний день', 'разобрать почту', '2026-10-26', 1, 'weekdays'],
    ['standup every weekday', 'standup', '2026-10-26', 1, 'weekdays']
  ])('parses recurrence %s', (input, title, dueTo, period, type) => {
    expect(parseTaskText(input, now)).toMatchObject({
      cleanTitle: title,
      dueTo,
      recurrence: { period, type, flexible_mode: false }
    });
  });

  it('does not invent a date for ordinary text', () => {
    expect(parseTaskText('Купить хлеб', now)).toEqual({
      cleanTitle: 'Купить хлеб', phrase: null, dueTo: null, recurrence: null, label: null
    });
  });

  it('converts parsed text to an API draft', () => {
    expect(toDraft('Снять завтра видеоролики', 'камера заряжена', now)).toEqual({
      title: 'Снять видеоролики', description: 'камера заряжена', due_to: '2026-10-26', recurrence: null
    });
  });

  it('keeps a date-only input as a non-empty task title', () => {
    expect(toDraft('завтра', '', now)).toMatchObject({
      title: 'завтра',
      due_to: '2026-10-26'
    });
  });

  it.each([
    ['days', 'каждый день', 'каждые 3 дн.'],
    ['weekdays', 'каждый будний день', 'каждые 3 будн. дн.'],
    ['weeks', 'каждую неделю', 'каждые 3 нед.'],
    ['months', 'каждый месяц', 'каждые 3 мес.'],
    ['years', 'каждый год', 'каждые 3 г.']
  ] as const)('formats %s recurrence labels', (type, singular, plural) => {
    expect(recurrenceLabel({ period: 1, type, flexible_mode: false })).toBe(singular);
    expect(recurrenceLabel({ period: 3, type, flexible_mode: true })).toBe(plural);
  });

  it('formats an absent recurrence as an empty label', () => {
    expect(recurrenceLabel(null)).toBe('');
  });
});
