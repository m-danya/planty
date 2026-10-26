<script lang="ts">
  import { onMount } from 'svelte';
  import { CalendarDays, Check, Flag, Info, Plus, Repeat2, X } from '@lucide/svelte';
  import { parseTaskText, recurrenceLabel, toDraft } from '$lib/date-parser';
  import { getLocale, localizedSectionTitle, t } from '$lib/i18n.svelte';
  import type { Section, Task, TaskDraft } from '$lib/types';

  let {
    task = null, section, sections = [], onSave, onSaveAndContinue, onCancel
  }: {
    task?: Task | null;
    section: string;
    sections?: Section[];
    onSave: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onSaveAndContinue?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancel: () => void;
  } = $props();

  let value = $state('');
  let description = $state('');
  let selectedSection = $state('');
  let saving = $state(false);
  let dateOpen = $state(false);
  let suggestionIndex = $state(0);
  let textarea: HTMLTextAreaElement;
  const parsed = $derived(parseTaskText(value, new Date(), getLocale()));
  const parts = $derived(highlightParts());
  const sectionMention = $derived(parseSectionMention());
  const sectionQuery = $derived(sectionMention?.query ?? null);
  const sectionMarker = $derived(sectionMention?.marker ?? '#');
  const matchingSections = $derived(sectionQuery === null ? [] : sections.filter((candidate) =>
    localizedSectionTitle(candidate.title).replace(/^[^\p{L}\p{N}]+/u, '').toLocaleLowerCase('ru-RU')
      .startsWith(sectionQuery.toLocaleLowerCase('ru-RU'))
  ).slice(0, 7));
  const effectiveDate = $derived(parsed.dueTo ?? task?.due_to ?? null);
  const effectiveRecurrence = $derived(parsed.phrase ? parsed.recurrence : task?.recurrence ?? null);

  onMount(() => {
    value = task?.title ?? '';
    description = task?.description ?? '';
    selectedSection = section;
    queueMicrotask(() => textarea?.focus());
  });

  $effect(() => {
    sectionQuery;
    suggestionIndex = 0;
  });

  function parseSectionMention(): { marker: string; query: string } | null {
    const candidate = value.match(/(?:^|\s)([#№])([^#№\s]*)$/u);
    return candidate ? { marker: candidate[1], query: candidate[2] } : null;
  }

  function chooseSection(chosen: Section) {
    selectedSection = chosen.id;
    value = value.replace(/(?:^|\s)[#№][^#№\s]*$/u, '').trimEnd();
    suggestionIndex = 0;
    queueMicrotask(() => textarea?.focus());
  }

  async function submit(continueWithSibling = false) {
    if (!value.trim() || saving) return;
    saving = true;
    try {
      const draft = toDraft(value, description);
      if (task && parsed.phrase === null) {
        draft.due_to = task.due_to;
        draft.recurrence = task.recurrence;
      }
      await (continueWithSibling && onSaveAndContinue
        ? onSaveAndContinue(draft, selectedSection)
        : onSave(draft, selectedSection));
    } finally {
      saving = false;
    }
  }

  function onKeydown(event: KeyboardEvent) {
    if (matchingSections.length && sectionQuery !== null) {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        const direction = event.key === 'ArrowDown' ? 1 : -1;
        suggestionIndex = (suggestionIndex + direction + matchingSections.length) % matchingSections.length;
        return;
      }
      if ((event.key === 'Enter' || event.key === 'Tab') && !event.shiftKey) {
        event.preventDefault();
        chooseSection(matchingSections[suggestionIndex] ?? matchingSections[0]);
        return;
      }
    }
    if (event.key === 'Enter' && event.shiftKey && task && onSaveAndContinue) {
      event.preventDefault();
      void submit(true);
    } else if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void submit();
    }
    if (event.key === 'Escape') onCancel();
  }

  function highlightParts() {
    if (!parsed.phrase) return { before: value, phrase: '', after: '' };
    const index = value.toLocaleLowerCase('ru-RU').indexOf(parsed.phrase.toLocaleLowerCase('ru-RU'));
    return { before: value.slice(0, index), phrase: value.slice(index, index + parsed.phrase.length), after: value.slice(index + parsed.phrase.length) };
  }

  function formatDate(valueToFormat: string): string {
    return new Date(`${valueToFormat}T12:00:00`).toLocaleDateString(getLocale() === 'ru' ? 'ru-RU' : 'en-US', {
      weekday: 'short', day: 'numeric', month: 'long', year: 'numeric'
    });
  }
</script>

<div class="composer" data-testid={task ? 'edit-task' : 'new-task'}>
  <div class="composer-input-wrap">
    <div class="composer-highlight" aria-hidden="true">
      <span>{parts.before}</span>{#if parts.phrase}<mark>{parts.phrase}</mark>{/if}<span>{parts.after}</span>
    </div>
    <textarea bind:this={textarea} bind:value onkeydown={onKeydown} rows="1" aria-label={t('taskTitle')} placeholder={t('taskPlaceholder')}></textarea>
    {#if sectionQuery !== null && matchingSections.length}
      <div class="section-suggestions" role="listbox" aria-label={t('sectionSuggestions')}>
        <div class="suggestions-hint">{t('selectSectionHint')}</div>
        {#each matchingSections as option, index (option.id)}
          <button type="button" role="option" aria-selected={index === suggestionIndex} class:active={index === suggestionIndex} onmousedown={(event) => event.preventDefault()} onclick={() => chooseSection(option)}>
            <span class="section-hash">{sectionMarker}</span><span>{localizedSectionTitle(option.title)}</span>
          </button>
        {/each}
      </div>
    {/if}
  </div>
  <input class="composer-description" bind:value={description} placeholder={t('description')} aria-label={t('taskDescription')} />
  <div class="composer-actions">
    <button type="button" class="icon-soft" title={t('moreOptions')} aria-label={t('moreOptions')}><Plus size={20} /></button>
    {#if effectiveDate}
      <button type="button" class="date-chip" onclick={() => dateOpen = !dateOpen} aria-expanded={dateOpen} aria-label={t('dateDetails')}>
        <CalendarDays size={17} /> {parsed.label ?? formatDate(effectiveDate)}
        {#if effectiveRecurrence}<Repeat2 size={14} aria-label={recurrenceLabel(effectiveRecurrence, getLocale())} />{/if}
      </button>
    {/if}
    <button type="button" class="chip-button" title={t('flag')} aria-label={t('flag')}><Flag size={18} /></button>
    {#if sections.length > 0}
      <select bind:value={selectedSection} aria-label={t('taskSection')}>
        {#each sections as option}<option value={option.id}>{localizedSectionTitle(option.title)}</option>{/each}
      </select>
    {/if}
    <span class="composer-spacer"></span>
    <button type="button" class="cancel-button" onclick={onCancel} aria-label={t('dismiss')}><X size={27} /></button>
    <button type="button" class="submit-button" onclick={() => void submit()} disabled={!value.trim() || saving} aria-label={t('saveTask')}><Check size={23} /></button>
  </div>
  {#if dateOpen && effectiveDate}
    <button type="button" class="popover-shield" aria-label={t('closeMenu')} onclick={() => dateOpen = false}></button>
    <section class="date-popover" aria-label={t('dateDetails')}>
      <header><CalendarDays size={19} /><strong>{t('dateDetails')}</strong><button type="button" onclick={() => dateOpen = false} aria-label={t('closeMenu')}><X size={17} /></button></header>
      <dl>
        <div><dt>{t('dueDate')}</dt><dd>{formatDate(effectiveDate)}</dd></div>
        <div><dt>{t('repeat')}</dt><dd>{effectiveRecurrence ? recurrenceLabel(effectiveRecurrence, getLocale()) : t('noRepeat')}</dd></div>
        {#if effectiveRecurrence}<div><dt>{t('schedule')}</dt><dd>{effectiveRecurrence.flexible_mode ? t('flexibleSchedule') : t('fixedSchedule')}</dd></div>{/if}
        {#if parsed.phrase}<div><dt>{t('sourcePhrase')}</dt><dd>«{parsed.phrase}»</dd></div>{/if}
      </dl>
      <p class="date-help"><Info size={16} />{t('flexibleHelp')}</p>
    </section>
  {/if}
</div>
