<script lang="ts">
  import { CalendarDays, ChevronLeft, ChevronRight, X } from '@lucide/svelte';
  import { untrack } from 'svelte';
  import { getLocale, t } from '$lib/i18n.svelte';

  let { value, x, y, onSelect, onClose }: {
    value: string | null;
    x: number;
    y: number;
    onSelect: (value: string) => void;
    onClose: () => void;
  } = $props();

  const initial = untrack(() => value ? new Date(`${value}T12:00:00`) : new Date());
  let visibleYear = $state(initial.getFullYear());
  let visibleMonth = $state(initial.getMonth());
  const locale = $derived(getLocale() === 'ru' ? 'ru-RU' : 'en-US');
  const monthLabel = $derived(formatMonth());
  const weekdayLabels = $derived(buildWeekdayLabels());
  const days = $derived(buildDays());
  const today = localIso(new Date());

  function localIso(date: Date): string {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }

  function formatMonth(): string {
    const label = new Date(visibleYear, visibleMonth, 1).toLocaleDateString(locale, {
      month: 'long', year: 'numeric'
    });
    return label.charAt(0).toLocaleUpperCase(locale) + label.slice(1);
  }

  function buildWeekdayLabels(): string[] {
    return Array.from({ length: 7 }, (_, index) =>
      new Date(2024, 0, index + 1).toLocaleDateString(locale, { weekday: 'short' }).replace('.', '')
    );
  }

  function buildDays(): { date: Date; iso: string; outside: boolean; label: string }[] {
    const first = new Date(visibleYear, visibleMonth, 1, 12);
    const mondayOffset = (first.getDay() + 6) % 7;
    const gridStart = new Date(visibleYear, visibleMonth, 1 - mondayOffset, 12);
    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(gridStart);
      date.setDate(gridStart.getDate() + index);
      return {
        date,
        iso: localIso(date),
        outside: date.getMonth() !== visibleMonth,
        label: date.toLocaleDateString(locale, {
          weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
        })
      };
    });
  }

  function changeMonth(delta: number) {
    const next = new Date(visibleYear, visibleMonth + delta, 1);
    visibleYear = next.getFullYear();
    visibleMonth = next.getMonth();
  }
</script>

<div class="calendar-picker" role="dialog" aria-modal="false" aria-label={t('chooseDueDate')} tabindex="-1" style={`left:${x}px;top:${y}px`}>
  <header class="calendar-picker-header">
    <span class="calendar-picker-icon"><CalendarDays size={18} /></span>
    <h3>{monthLabel}</h3>
    <div class="calendar-picker-nav">
      <button type="button" aria-label={t('previousMonth')} onclick={() => changeMonth(-1)}><ChevronLeft size={18} /></button>
      <button type="button" aria-label={t('nextMonth')} onclick={() => changeMonth(1)}><ChevronRight size={18} /></button>
      <button type="button" aria-label={t('closeCalendar')} onclick={onClose}><X size={18} /></button>
    </div>
  </header>
  <div class="calendar-weekdays" aria-hidden="true">
    {#each weekdayLabels as weekday}<span>{weekday}</span>{/each}
  </div>
  <div class="calendar-days">
    {#each days as day (day.iso)}
      <button
        type="button"
        class:outside={day.outside}
        class:today={day.iso === today}
        class:selected={day.iso === value}
        aria-label={day.label}
        aria-current={day.iso === today ? 'date' : undefined}
        aria-pressed={day.iso === value}
        onclick={() => onSelect(day.iso)}
      >{day.date.getDate()}</button>
    {/each}
  </div>
</div>
