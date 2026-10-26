import type { RecurrenceInfo, RecurrenceType, TaskDraft } from './types';

export interface ParsedDate {
  cleanTitle: string;
  phrase: string | null;
  dueTo: string | null;
  recurrence: RecurrenceInfo | null;
  label: string | null;
}

const ruMonths: Record<string, number> = {
  январь: 0, января: 0, янв: 0, февраль: 1, февраля: 1, фев: 1, февр: 1,
  март: 2, марта: 2, мар: 2, апрель: 3, апреля: 3, апр: 3, май: 4, мая: 4,
  июнь: 5, июня: 5, июн: 5, июль: 6, июля: 6, июл: 6,
  август: 7, августа: 7, авг: 7, сентябрь: 8, сентября: 8, сен: 8, сент: 8,
  октябрь: 9, октября: 9, окт: 9, ноябрь: 10, ноября: 10, ноя: 10, нояб: 10,
  декабрь: 11, декабря: 11, дек: 11
};
const enMonths: Record<string, number> = {
  january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
  july: 6, august: 7, september: 8, october: 9, november: 10, december: 11,
  jan: 0, feb: 1, mar: 2, apr: 3, jun: 5, jul: 6, aug: 7, sep: 8, sept: 8,
  oct: 9, nov: 10, dec: 11
};
const weekdays: Record<string, number> = {
  sunday: 0, воскресенье: 0, воскресеньям: 0, monday: 1, понедельник: 1, понедельникам: 1,
  tuesday: 2, вторник: 2, вторникам: 2, wednesday: 3, среда: 3, среду: 3, средам: 3,
  thursday: 4, четверг: 4, четвергам: 4, friday: 5, пятница: 5, пятницу: 5, пятницам: 5,
  saturday: 6, суббота: 6, субботу: 6, субботам: 6,
  вс: 0, пн: 1, вт: 2, ср: 3, чт: 4, пт: 5, сб: 6
};
const unitMap: Record<string, RecurrenceType> = {
  day: 'days', days: 'days', день: 'days', дня: 'days', дней: 'days',
  week: 'weeks', weeks: 'weeks', неделя: 'weeks', неделю: 'weeks', недели: 'weeks', недель: 'weeks',
  month: 'months', months: 'months', месяц: 'months', месяца: 'months', месяцев: 'months',
  year: 'years', years: 'years', год: 'years', года: 'years', лет: 'years'
};
const numberWords: Record<string, number> = {
  один: 1, одна: 1, одну: 1, первый: 1, первую: 1, one: 1,
  два: 2, две: 2, второй: 2, вторую: 2, вторые: 2, two: 2, other: 2,
  три: 3, третий: 3, третью: 3, three: 3,
  четыре: 4, четвёртый: 4, четвертый: 4, four: 4
};

function amount(value: string | undefined): number {
  if (!value) return 1;
  return Number(value) || numberWords[value] || 1;
}

function localIso(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function atNoon(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 12);
}

function plusDays(base: Date, amount: number): Date {
  const result = atNoon(base);
  result.setDate(result.getDate() + amount);
  return result;
}

function nextWeekday(base: Date, day: number, forceNext = false): Date {
  let delta = (day - base.getDay() + 7) % 7;
  if (delta === 0 || (forceNext && base.getDay() !== 0 && day > base.getDay())) delta += 7;
  return plusDays(base, delta);
}

function startOfNextWeek(base: Date): Date {
  return plusDays(base, ((8 - base.getDay()) % 7) || 7);
}

function nextBusinessDay(base: Date): Date {
  let result = atNoon(base);
  while (result.getDay() === 0 || result.getDay() === 6) result = plusDays(result, 1);
  return result;
}

function plusPeriod(base: Date, amount: number, type: RecurrenceType): Date {
  if (type === 'days') return plusDays(base, amount);
  if (type === 'weekdays') {
    let result = atNoon(base);
    for (let left = amount; left > 0;) {
      result = plusDays(result, 1);
      if (result.getDay() !== 0 && result.getDay() !== 6) left -= 1;
    }
    return result;
  }
  if (type === 'weeks') return plusDays(base, amount * 7);
  const result = atNoon(base);
  const originalDay = result.getDate();
  result.setDate(1);
  if (type === 'months') result.setMonth(result.getMonth() + amount);
  if (type === 'years') result.setFullYear(result.getFullYear() + amount);
  result.setDate(Math.min(originalDay, new Date(result.getFullYear(), result.getMonth() + 1, 0).getDate()));
  return result;
}

function calendarDate(day: number, month: number, year: number | undefined, now: Date): Date | null {
  let result = new Date(year ?? now.getFullYear(), month, day, 12);
  if (result.getMonth() !== month || result.getDate() !== day) return null;
  if (year === undefined && result < atNoon(now)) result = new Date(now.getFullYear() + 1, month, day, 12);
  return result;
}

function displayDate(date: Date, now: Date, locale: 'ru' | 'en'): string {
  const delta = Math.round((atNoon(date).getTime() - atNoon(now).getTime()) / 86400000);
  if (delta === 0) return locale === 'ru' ? 'Сегодня' : 'Today';
  if (delta === 1) return locale === 'ru' ? 'Завтра' : 'Tomorrow';
  if (delta === 2) return locale === 'ru' ? 'Послезавтра' : 'Day after tomorrow';
  return date.toLocaleDateString(locale === 'ru' ? 'ru-RU' : 'en-US', { day: 'numeric', month: 'long', year: date.getFullYear() === now.getFullYear() ? undefined : 'numeric' });
}

function parseStartPhrase(value: string | undefined, now: Date): Date {
  if (!value) return atNoon(now);
  const normalized = value.replace(/^(?:начиная\s+(?:с\s+)?|starting\s+(?:on\s+)?|с\s+|from\s+)/u, '').trim();
  if (/^(?:завтра|tomorrow)$/u.test(normalized)) return plusDays(now, 1);
  if (/^(?:послезавтра|day after tomorrow)$/u.test(normalized)) return plusDays(now, 2);
  const parsed = parseTaskText(normalized, now);
  if (parsed.dueTo) return new Date(`${parsed.dueTo}T12:00:00`);
  return atNoon(now);
}

export function parseTaskText(input: string, now = new Date(), locale: 'ru' | 'en' = 'ru'): ParsedDate {
  const text = input.trim();
  const lower = text.toLocaleLowerCase('ru-RU');
  let match = [] as unknown as RegExpMatchArray;
  let due: Date | null = null;
  let recurrence: RecurrenceInfo | null = null;

  const choose = (candidate: RegExpMatchArray | null): boolean => {
    if (!candidate || candidate.index === undefined) return false;
    match = candidate;
    return true;
  };
  const recurringPrefix = '(?:кажд(?:ый|ую|ые|ое)(!?)|every(!?))';
  const amountPattern = '(\\d+|один|одна|одну|первый|первую|два|две|второй|вторую|вторые|три|третий|третью|четыре|четвёртый|четвертый|one|two|three|four|other)';
  const units = '(days|day|weeks|week|months|month|years|year|дней|день|дня|недель|неделю|недели|месяцев|месяц|месяца|лет|год|года)';
  const monthNames = '(?:января?|янв|февраля?|февр?|марта?|мар|апреля?|апр|мая?|июня?|июн|июля?|июл|августа?|авг|сентября?|сент|сен|октября?|окт|ноября?|нояб?|ноя|декабря?|дек|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)';
  const weekdayNames = '(?:понедельник|понедельникам|вторник|вторникам|среду|средам|четверг|четвергам|пятницу|пятницам|субботу|субботам|воскресенье|воскресеньям|пн\\.?|вт\\.?|ср\\.?|чт\\.?|пт\\.?|сб\\.?|вс\\.?|monday|tuesday|wednesday|thursday|friday|saturday|sunday)';
  const startDate = `(?:сегодня|завтра|послезавтра|today|tomorrow|day after tomorrow|\\d{1,2}[./-]\\d{1,2}(?:[./-]\\d{2,4})?|\\d{1,2}\\s+${monthNames}(?:\\s+\\d{4})?|(?:в\\s+)?(?:следующ(?:ий|ую)\\s+|next\\s+)?${weekdayNames})`;
  const start = `(?:\\s+((?:начиная\\s+(?:с\\s+)?|starting\\s+(?:on\\s+)?|с\\s+|from\\s+)${startDate}))?`;
  const recurring = lower.match(new RegExp(`${recurringPrefix}\\s+(?:${amountPattern}\\s+)?${units}(!?)${start}(?!\\p{L})`, 'u'));
  const recurringQuarter = lower.match(new RegExp(`${recurringPrefix}\\s+(?:${amountPattern}\\s+)?(?:квартал|квартала|кварталов|quarter|quarters)(!?)${start}(?!\\p{L})`, 'u'));
  const recurringAdverb = lower.match(/(?<!\p{L})(ежедневно|еженедельно|ежемесячно|ежеквартально|ежегодно|daily|weekly|monthly|quarterly|yearly)(!?)(?!\p{L})/u);
  const recurringWeekday = lower.match(new RegExp(`${recurringPrefix}\\s+(${weekdayNames})(!?)(?!\\p{L})`, 'u'));
  const recurringBusinessDay = lower.match(new RegExp(`(?<!\\p{L})(?:${recurringPrefix}\\s+(?:${amountPattern}\\s+)?(?:будн(?:ий|их)\\s+(?:день|дня|дней)|рабоч(?:ий|их)\\s+(?:день|дня|дней)|weekday(?:s)?)(!?)|по\\s+будням(!?)|weekdays(!?))(?!\\p{L})`, 'u'));
  const relative = lower.match(new RegExp(`(?<!\\p{L})(?:через|in)\\s+(?:${amountPattern}\\s+)?(days|day|weekdays|weekday|weeks|week|months|month|years|year|будн(?:их|ий)\\s+(?:дней|день)|рабоч(?:их|ий)\\s+(?:дней|день)|дней|дня|день|недель|недели|неделю|месяцев|месяца|месяц|лет|года|год)(?!\\p{L})`, 'u'));

  if (choose(recurringQuarter)) {
    recurrence = { period: amount(match[3]) * 3, type: 'months', flexible_mode: match[1] === '!' || match[2] === '!' || match[4] === '!' };
    due = parseStartPhrase(match[5], now);
  } else if (choose(recurringBusinessDay)) {
    recurrence = { period: amount(match[3]), type: 'weekdays', flexible_mode: match.slice(1).some((part) => part === '!') };
    due = nextBusinessDay(now);
  } else if (choose(recurring)) {
    recurrence = {
      period: amount(match[3]), type: unitMap[match[4]],
      flexible_mode: match[1] === '!' || match[2] === '!' || match[5] === '!'
    };
    due = parseStartPhrase(match[6], now);
  } else if (choose(recurringAdverb)) {
    const value = match[1];
    const type: RecurrenceType = value.includes('month') || value.includes('месяч') || value.includes('quarter') || value.includes('кварт') ? 'months'
      : value.includes('year') || value.includes('год') ? 'years'
      : value.includes('week') || value.includes('недель') ? 'weeks' : 'days';
    recurrence = { period: value.includes('quarter') || value.includes('кварт') ? 3 : 1, type, flexible_mode: match[2] === '!' };
    due = atNoon(now);
  } else if (choose(recurringWeekday)) {
    due = nextWeekday(now, weekdays[match[3].replace('.', '')]);
    recurrence = { period: 1, type: 'weeks', flexible_mode: match[1] === '!' || match[2] === '!' || match[4] === '!' };
  } else if (choose(relative)) {
    const rawUnit = match[2];
    const type = rawUnit.includes('будн') || rawUnit.includes('рабоч') || rawUnit.startsWith('weekday') ? 'weekdays' : unitMap[rawUnit];
    due = plusPeriod(now, amount(match[1]), type);
  } else if (choose(lower.match(/(?<!\p{L})((?:на\s+)?следующ(?:ая|ую|ей)\s+недел(?:я|ю|е)|next\s+week)(?!\p{L})/u))) {
    due = startOfNextWeek(now);
  } else if (choose(lower.match(/(?<!\p{L})((?:на\s+)?следующ(?:ий|ем)\s+месяц(?:е)?|next\s+month)(?!\p{L})/u))) {
    due = plusPeriod(now, 1, 'months');
  } else if (choose(lower.match(/(?<!\p{L})((?:на\s+)?следующ(?:ий|ем)\s+год(?:у)?|next\s+year)(?!\p{L})/u))) {
    due = plusPeriod(now, 1, 'years');
  } else if (choose(lower.match(/(?<!\p{L})(на\s+выходных|this\s+weekend)(?!\p{L})/u))) {
    due = nextWeekday(now, 6);
  } else if (choose(lower.match(/(?<!\p{L})(послезавтра|day after tomorrow)(?!\p{L})/u))) {
    due = plusDays(now, 2);
  } else if (choose(lower.match(/(?<!\p{L})(сегодня|today)(?!\p{L})/u))) {
    due = atNoon(now);
  } else if (choose(lower.match(/(?<!\p{L})(завтра|tomorrow)(?!\p{L})/u))) {
    due = plusDays(now, 1);
  } else if (choose(lower.match(/(?:^|\s)(?:в\s+|on\s+)?(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?(?=$|\s)/u))) {
    const year = match[3] ? Number(match[3].length === 2 ? `20${match[3]}` : match[3]) : undefined;
    due = calendarDate(Number(match[1]), Number(match[2]) - 1, year, now);
  } else if (choose(lower.match(/(?:^|\s)(?:в\s+|on\s+)?(\d{1,2})\s+(января?|янв|февраля?|февр?|марта?|мар|апреля?|апр|мая?|июня?|июн|июля?|июл|августа?|авг|сентября?|сент|сен|октября?|окт|ноября?|нояб?|ноя|декабря?|дек|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+(\d{4}))?(?=$|\s)/u))) {
    due = calendarDate(Number(match[1]), ruMonths[match[2]] ?? enMonths[match[2]], match[3] ? Number(match[3]) : undefined, now);
  } else if (choose(lower.match(new RegExp(`(?<!\\p{L})(?:(в\\s+следующ(?:ий|ую)|след(?:ующий|ующую)?|next)\\s+|в\\s+ближайш(?:ий|ую)\\s+|(?:в|on)\\s+)?(${weekdayNames})(?!\\p{L})`, 'u')))) {
    due = nextWeekday(now, weekdays[match[2].replace('.', '')], Boolean(match[1]));
  }

  if (!match.length || !due) return { cleanTitle: text, phrase: null, dueTo: null, recurrence: null, label: null };
  const startIndex = match.index ?? 0;
  const rawPhrase = text.slice(startIndex, startIndex + match[0].length);
  const leadingSpace = rawPhrase.length - rawPhrase.trimStart().length;
  const phrase = rawPhrase.trim();
  const cleanStart = startIndex + leadingSpace;
  const cleanTitle = `${text.slice(0, cleanStart)} ${text.slice(cleanStart + phrase.length)}`.replace(/\s+/g, ' ').trim();
  return { cleanTitle, phrase, dueTo: localIso(due), recurrence, label: recurrence ? phrase : displayDate(due, now, locale) };
}

export function toDraft(input: string, description = '', now = new Date()): TaskDraft {
  const parsed = parseTaskText(input, now);
  return { title: parsed.cleanTitle || input.trim(), description, due_to: parsed.dueTo, recurrence: parsed.recurrence };
}

export function recurrenceLabel(recurrence: RecurrenceInfo | null, locale: 'ru' | 'en' = 'ru'): string {
  if (!recurrence) return '';
  if (locale === 'en') {
    const names: Record<RecurrenceType, [string, string]> = {
      days: ['Every day', 'days'], weekdays: ['Every weekday', 'weekdays'], weeks: ['Every week', 'weeks'],
      months: ['Every month', 'months'], years: ['Every year', 'years']
    };
    return recurrence.period === 1 ? names[recurrence.type][0] : `Every ${recurrence.period} ${names[recurrence.type][1]}`;
  }
  const names: Record<RecurrenceType, [string, string]> = {
    days: ['каждый день', 'дн.'], weekdays: ['каждый будний день', 'будн. дн.'],
    weeks: ['каждую неделю', 'нед.'], months: ['каждый месяц', 'мес.'], years: ['каждый год', 'г.']
  };
  return recurrence.period === 1 ? names[recurrence.type][0] : `каждые ${recurrence.period} ${names[recurrence.type][1]}`;
}
