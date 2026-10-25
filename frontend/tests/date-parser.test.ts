import { describe, expect, it } from 'vitest';
import { parseTaskText, recurrenceLabel, toDraft } from '../src/lib/date-parser';

const now = new Date(2026, 9, 25, 12);

describe('natural-language date parser', () => {
  it.each([
    ['Позвонить маме завтра', 'Позвонить маме', '2026-10-26'],
    ['call Alex tomorrow', 'call Alex', '2026-10-26'],
    ['Закончить отчёт сегодня', 'Закончить отчёт', '2026-10-25'],
    ['Встреча 03.11.2026', 'Встреча', '2026-11-03'],
    ['День рождения 7 ноября', 'День рождения', '2026-11-07'],
    ['deploy next monday', 'deploy', '2026-10-26'],
    ['Ответить через 3 дня', 'Ответить', '2026-10-28'],
    ['review in 2 weeks', 'review', '2026-11-08'],
    ['план на следующую неделю', 'план', '2026-11-01'],
    ['budget next month', 'budget', '2026-11-25']
  ])('parses %s', (input, title, dueTo) => {
    expect(parseTaskText(input, now)).toMatchObject({ cleanTitle: title, dueTo });
  });

  it.each([
    ['читать каждый день начиная завтра', 'читать', '2026-10-26', 1, 'days'],
    ['сделать уборку каждые 3 дня начиная завтра', 'сделать уборку', '2026-10-26', 3, 'days'],
    ['plan review every 2 weeks starting tomorrow', 'plan review', '2026-10-26', 2, 'weeks'],
    ['оплатить счета ежемесячно', 'оплатить счета', '2026-10-25', 1, 'months'],
    ['annual check yearly', 'annual check', '2026-10-25', 1, 'years'],
    ['стендап каждый понедельник', 'стендап', '2026-10-26', 1, 'weeks'],
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

  it('formats recurrence labels', () => {
    expect(recurrenceLabel({ period: 3, type: 'days', flexible_mode: false })).toBe('каждые 3 дн.');
  });
});
