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
    ['план на следующую неделю', 'план', '2026-10-26'],
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

  it.each([
    ['поливать каждый! день', 'days'],
    ['проверка каждые! 2 недели', 'weeks'],
    ['оплачивать каждый месяц!', 'months'],
    ['отчёт еженедельно!', 'weeks'],
    ['созвон каждый! понедельник', 'weeks'],
    ['почта каждый! будний день', 'weekdays']
  ])('parses completion-based recurrence %s', (input, type) => {
    expect(parseTaskText(input, now)).toMatchObject({
      recurrence: { type, flexible_mode: true }
    });
  });

  it.each([
    ['обновить отчёт каждые две недели начиная с 7 ноября', '2026-11-07', 2, 'weeks', false],
    ['проверить отчёт каждый квартал', '2026-10-25', 3, 'months', false],
    ['проверить отчёт ежеквартально!', '2026-10-25', 3, 'months', true],
    ['уборка каждый день с 3 ноября', '2026-11-03', 1, 'days', false],
    ['созвон каждую пт', '2026-10-30', 1, 'weeks', false],
    ['проверка каждый! 3 рабочих дня', '2026-10-26', 3, 'weekdays', true]
  ])('parses richer Russian recurrence %s', (input, dueTo, period, type, flexibleMode) => {
    expect(parseTaskText(input, now)).toMatchObject({
      dueTo,
      recurrence: { period, type, flexible_mode: flexibleMode }
    });
  });

  it.each([
    ['Ответить через неделю', '2026-11-01'],
    ['Оплатить через месяц', '2026-11-25'],
    ['Созвон след пн', '2026-10-26']
  ])('parses Russian shorthand %s', (input, dueTo) => {
    expect(parseTaskText(input, now)).toMatchObject({ dueTo });
  });

  it('localizes normalized date labels', () => {
    expect(parseTaskText('call tomorrow', now, 'en').label).toBe('Tomorrow');
    expect(parseTaskText('позвонить завтра', now, 'ru').label).toBe('Завтра');
  });

  it('moves a yearless past calendar date to its next occurrence', () => {
    expect(parseTaskText('Поздравить 7 мая', now)).toMatchObject({ dueTo: '2027-05-07' });
  });

  it('rejects impossible calendar dates', () => {
    expect(parseTaskText('Оплатить 31.02.2027', now).dueTo).toBeNull();
  });

  it('counts relative business days without weekends', () => {
    expect(parseTaskText('Ответить через 5 будних дней', now)).toMatchObject({ dueTo: '2026-10-30' });
  });

  it('does not invent a date for ordinary text', () => {
    expect(parseTaskText('Купить хлеб', now)).toEqual({
      cleanTitle: 'Купить хлеб', phrase: null, dueTo: null, dueTime: null, recurrence: null, label: null
    });
  });

  it.each([
    ['каждый день качаться без срока', 'каждый день качаться', 'без срока'],
    ['work out every day no date', 'work out every day', 'no date'],
    ['позвонить завтра нет срока', 'позвонить завтра', 'нет срока'],
    ['call tomorrow no due date', 'call tomorrow', 'no due date']
  ])('lets a trailing no-date phrase override earlier scheduling in %s', (input, cleanTitle, phrase) => {
    expect(parseTaskText(input, now)).toEqual({
      cleanTitle,
      phrase,
      dueTo: null,
      dueTime: null,
      recurrence: null,
      label: null
    });
  });

  it('lets a later date override an earlier no-date phrase', () => {
    expect(parseTaskText('позвонить без срока завтра', now)).toMatchObject({
      cleanTitle: 'позвонить без срока',
      phrase: 'завтра',
      dueTo: '2026-10-26'
    });
  });

  it.each([
    ['Позвонить завтра в 16:00', 'Позвонить', '2026-10-26', '16:00'],
    ['Buy milk tomorrow 9am', 'Buy milk', '2026-10-26', '09:00'],
    ['Созвон пт 19:30', 'Созвон', '2026-10-30', '19:30'],
    ['Call Alex Fri at 7pm', 'Call Alex', '2026-10-30', '19:00'],
    ['Ужин 6pm', 'Ужин', '2026-10-25', '18:00'],
    ['Завтрак 9am', 'Завтрак', '2026-10-26', '09:00'],
    ['Отчёт сегодня в 10', 'Отчёт', '2026-10-25', '10:00'],
    ['Стендап каждый понедельник в 09:15', 'Стендап', '2026-10-26', '09:15'],
    ['Перезвонить через 2 часа', 'Перезвонить', '2026-10-25', '14:00'],
    ['Follow up in 90 minutes', 'Follow up', '2026-10-25', '13:30'],
    ['Почитать вечером', 'Почитать', '2026-10-25', '19:00'],
    ['Plan tomorrow in the morning', 'Plan', '2026-10-26', '09:00'],
    ['Начать в полночь', 'Начать', '2026-10-26', '00:00']
  ])('parses Todoist-style due time in %s', (input, title, dueTo, dueTime) => {
    expect(parseTaskText(input, now)).toMatchObject({ cleanTitle: title, dueTo, dueTime });
  });

  it.each(['24:00', '12:60', 'at 13pm'])('rejects invalid time %s', (input) => {
    expect(parseTaskText(`Задача ${input}`, now).dueTime).toBeNull();
  });

  it('converts parsed text to an API draft', () => {
    expect(toDraft('Снять завтра видеоролики', 'камера заряжена', now)).toEqual({
      title: 'Снять видеоролики', description: 'камера заряжена', due_to: '2026-10-26',
      due_time: null, recurrence: null
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
