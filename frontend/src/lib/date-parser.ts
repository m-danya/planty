import type { RecurrenceInfo, RecurrenceType, TaskDraft } from './types';

export interface ParsedDate {
  cleanTitle: string;
  phrase: string | null;
  dueTo: string | null;
  recurrence: RecurrenceInfo | null;
  label: string | null;
}

const ruMonths: Record<string, number> = {
  января: 0, февраля: 1, марта: 2, апреля: 3, мая: 4, июня: 5,
  июля: 6, августа: 7, сентября: 8, октября: 9, ноября: 10, декабря: 11
};
const enMonths: Record<string, number> = {
  january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
  july: 6, august: 7, september: 8, october: 9, november: 10, december: 11,
  jan: 0, feb: 1, mar: 2, apr: 3, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11
};
const weekdays: Record<string, number> = {
  sunday: 0, понедельник: 1, понедельникам: 1, monday: 1,
  вторник: 2, вторникам: 2, tuesday: 2, среда: 3, средам: 3, wednesday: 3,
  четверг: 4, четвергам: 4, thursday: 4, пятница: 5, пятницам: 5, friday: 5,
  суббота: 6, субботам: 6, saturday: 6, воскресенье: 0, воскресеньям: 0
};

function localIso(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function plusDays(base: Date, amount: number): Date {
  const result = new Date(base);
  result.setHours(12, 0, 0, 0);
  result.setDate(result.getDate() + amount);
  return result;
}

function nextWeekday(base: Date, day: number): Date {
  let delta = (day - base.getDay() + 7) % 7;
  if (delta === 0) delta = 7;
  return plusDays(base, delta);
}

function nextBusinessDay(base: Date, includeToday = true): Date {
  let result = new Date(base);
  if (!includeToday) result = plusDays(result, 1);
  while (result.getDay() === 0 || result.getDay() === 6) result = plusDays(result, 1);
  return result;
}

function plusPeriod(base: Date, amount: number, type: RecurrenceType): Date {
  if (type === 'days' || type === 'weekdays') return plusDays(base, amount);
  if (type === 'weeks') return plusDays(base, amount * 7);
  const result = new Date(base);
  if (type === 'months') result.setMonth(result.getMonth() + amount);
  if (type === 'years') result.setFullYear(result.getFullYear() + amount);
  return result;
}

const unitMap: Record<string, RecurrenceType> = {
  day: 'days', days: 'days', день: 'days', дня: 'days', дней: 'days',
  week: 'weeks', weeks: 'weeks', неделю: 'weeks', недели: 'weeks', недель: 'weeks',
  month: 'months', months: 'months', месяц: 'months', месяца: 'months', месяцев: 'months',
  year: 'years', years: 'years', год: 'years', года: 'years', лет: 'years'
};

export function parseTaskText(input: string, now = new Date()): ParsedDate {
  const text = input.trim();
  const lower = text.toLocaleLowerCase('ru-RU');
  let match: RegExpMatchArray | null = null;
  let start = -1;
  let end = -1;
  let due: Date | null = null;
  let recurrence: RecurrenceInfo | null = null;
  let label: string | null = null;

  const choose = (candidate: RegExpMatchArray | null) => {
    if (!candidate || candidate.index === undefined) return false;
    match = candidate;
    start = candidate.index;
    end = start + candidate[0].length;
    return true;
  };

  const recurring = lower.match(/(?:кажд(?:ый|ую|ые|ую)\s+|every\s+)(?:(\d+)\s+)?(days|day|weeks|week|months|month|years|year|дней|день|дня|недель|неделю|недели|месяцев|месяц|месяца|лет|год|года)(?:\s+(?:начиная\s+|с\s+|starting\s+)?(сегодня|завтра|today|tomorrow))?/u);
  const recurringAdverb = lower.match(/(?<!\p{L})(ежедневно|еженедельно|ежемесячно|ежегодно|daily|weekly|monthly|yearly)(?!\p{L})/u);
  const recurringWeekday = lower.match(/(?:кажд(?:ый|ую|ую)|every)\s+(понедельник|понедельникам|вторник|вторникам|среду|средам|четверг|четвергам|пятницу|пятницам|субботу|субботам|воскресенье|воскресеньям|monday|tuesday|wednesday|thursday|friday|saturday|sunday)/u);
  const recurringBusinessDay = lower.match(/(?<!\p{L})(каждый\s+будний\s+день|по\s+будням|every\s+weekday|weekdays)(?!\p{L})/u);
  const relative = lower.match(/(?<!\p{L})(?:через|in)\s+(\d+)\s+(days|day|weeks|week|months|month|years|year|дней|дня|день|недель|недели|неделю|месяцев|месяца|месяц|лет|года|год)(?!\p{L})/u);
  const nextPeriod = lower.match(/(?<!\p{L})((?:на\s+)?следующ(?:ая|ую|ей|ий)\s+(?:неделя|неделю|неделе|месяц|год)|next\s+(?:week|month|year))(?!\p{L})/u);

  if (choose(recurringBusinessDay)) {
    recurrence = { period: 1, type: 'weekdays', flexible_mode: false };
    due = nextBusinessDay(now);
    label = match![0];
  } else if (choose(recurring)) {
    const period = Number(match![1] ?? 1);
    const type = unitMap[match![2]];
    recurrence = { period, type, flexible_mode: false };
    due = match![3] === 'tomorrow' || match![3] === 'завтра' ? plusDays(now, 1) : new Date(now);
    label = match![0];
  } else if (choose(recurringAdverb)) {
    const value = match![1];
    const type: RecurrenceType = value.includes('month') || value.includes('месяч') ? 'months'
      : value.includes('year') || value.includes('год') ? 'years'
      : value.includes('week') || value.includes('недель') ? 'weeks' : 'days';
    recurrence = { period: 1, type, flexible_mode: false };
    due = new Date(now);
    label = match![0];
  } else if (choose(recurringWeekday)) {
    const normalized = match![1].replace('среду', 'среда').replace('пятницу', 'пятница').replace('субботу', 'суббота');
    due = nextWeekday(now, weekdays[normalized]);
    recurrence = { period: 1, type: 'weeks', flexible_mode: false };
    label = match![0];
  } else if (choose(relative)) {
    const amount = Number(match![1]);
    const type = unitMap[match![2]];
    due = plusPeriod(now, amount, type);
    label = match![0];
  } else if (choose(nextPeriod)) {
    const phrase = match![0];
    const type: RecurrenceType = phrase.includes('month') || phrase.includes('месяц') ? 'months'
      : phrase.includes('year') || phrase.includes('год') ? 'years' : 'weeks';
    due = plusPeriod(now, 1, type);
    label = match![0];
  } else if (choose(lower.match(/(?<!\p{L})(сегодня|today)(?!\p{L})/u))) {
    due = new Date(now);
    label = 'Сегодня';
  } else if (choose(lower.match(/(?<!\p{L})(завтра|tomorrow)(?!\p{L})/u))) {
    due = plusDays(now, 1);
    label = 'Завтра';
  } else if (choose(lower.match(/(?<!\p{L})(послезавтра|day after tomorrow)(?!\p{L})/u))) {
    due = plusDays(now, 2);
    label = 'Послезавтра';
  } else if (choose(lower.match(/(?:в |on )?(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?/u))) {
    const year = match![3] ? Number(match![3].length === 2 ? `20${match![3]}` : match![3]) : now.getFullYear();
    due = new Date(year, Number(match![2]) - 1, Number(match![1]), 12);
    label = match![0];
  } else if (choose(lower.match(/(?:в |on )?(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)(?:\s+(\d{4}))?/u))) {
    const month = ruMonths[match![2]] ?? enMonths[match![2]];
    due = new Date(Number(match![3] ?? now.getFullYear()), month, Number(match![1]), 12);
    label = match![0];
  } else if (choose(lower.match(/(?:в следующий |next |в ближайший )?(понедельник|вторник|среду|четверг|пятницу|субботу|воскресенье|monday|tuesday|wednesday|thursday|friday|saturday|sunday)/u))) {
    const normalized = match![1].replace('среду', 'среда').replace('пятницу', 'пятница').replace('субботу', 'суббота');
    due = nextWeekday(now, weekdays[normalized]);
    label = match![0];
  }

  if (!match || !due) return { cleanTitle: text, phrase: null, dueTo: null, recurrence: null, label: null };

  const phrase = text.slice(start, end);
  const cleanTitle = `${text.slice(0, start)} ${text.slice(end)}`.replace(/\s+/g, ' ').trim();
  return { cleanTitle, phrase, dueTo: localIso(due), recurrence, label: label ?? phrase };
}

export function toDraft(input: string, description = '', now = new Date()): TaskDraft {
  const parsed = parseTaskText(input, now);
  return {
    title: parsed.cleanTitle || input.trim(),
    description,
    due_to: parsed.dueTo,
    recurrence: parsed.recurrence
  };
}

export function recurrenceLabel(recurrence: RecurrenceInfo | null): string {
  if (!recurrence) return '';
  const names: Record<RecurrenceType, [string, string]> = {
    days: ['день', 'дн.'], weekdays: ['будний день', 'будн. дн.'], weeks: ['неделю', 'нед.'], months: ['месяц', 'мес.'], years: ['год', 'г.']
  };
  return recurrence.period === 1 ? `каждый ${names[recurrence.type][0]}` : `каждые ${recurrence.period} ${names[recurrence.type][1]}`;
}
