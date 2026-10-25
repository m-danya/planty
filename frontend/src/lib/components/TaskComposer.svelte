<script lang="ts">
  import { onMount } from 'svelte';
  import { CalendarDays, Check, Flag, Plus, Repeat2, X } from '@lucide/svelte';
  import { parseTaskText, recurrenceLabel, toDraft } from '$lib/date-parser';
  import type { Section, Task, TaskDraft } from '$lib/types';

  let {
    task = null,
    section,
    sections = [],
    onSave,
    onCancel
  }: {
    task?: Task | null;
    section: string;
    sections?: Section[];
    onSave: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancel: () => void;
  } = $props();

  let value = $state('');
  let description = $state('');
  let selectedSection = $state('');
  let saving = $state(false);
  let textarea: HTMLTextAreaElement;
  const parsed = $derived(parseTaskText(value));
  const parts = $derived(highlightParts());

  onMount(() => {
    value = task?.title ?? '';
    description = task?.description ?? '';
    selectedSection = section;
    queueMicrotask(() => textarea?.focus());
  });

  async function submit() {
    if (!value.trim() || saving) return;
    saving = true;
    try {
      const draft = toDraft(value, description);
      if (task && parsed.phrase === null) {
        draft.due_to = task.due_to;
        draft.recurrence = task.recurrence;
      }
      await onSave(draft, selectedSection);
    } finally {
      saving = false;
    }
  }

  function onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void submit();
    }
    if (event.key === 'Escape') onCancel();
  }

  function highlightParts() {
    if (!parsed.phrase) return { before: value, phrase: '', after: '' };
    const index = value.toLocaleLowerCase('ru-RU').indexOf(parsed.phrase.toLocaleLowerCase('ru-RU'));
    return {
      before: value.slice(0, index),
      phrase: value.slice(index, index + parsed.phrase.length),
      after: value.slice(index + parsed.phrase.length)
    };
  }
</script>

<div class="composer" data-testid={task ? 'edit-task' : 'new-task'}>
  <div class="composer-input-wrap">
    <div class="composer-highlight" aria-hidden="true">
      <span>{parts.before}</span>{#if parts.phrase}<mark>{parts.phrase}</mark>{/if}<span>{parts.after}</span>
    </div>
    <textarea
      bind:this={textarea}
      bind:value
      onkeydown={onKeydown}
      rows="1"
      aria-label="Название задачи"
      placeholder="Что нужно сделать? Например: позвонить завтра"
    ></textarea>
  </div>
  <input class="composer-description" bind:value={description} placeholder="Описание" aria-label="Описание задачи" />
  <div class="composer-actions">
    <button class="icon-soft" title="Дополнительные параметры" aria-label="Дополнительные параметры"><Plus size={20} /></button>
    {#if parsed.dueTo}
      <span class:tomorrow={parsed.label?.toLocaleLowerCase('ru-RU').includes('завтра')} class="date-chip">
        <CalendarDays size={17} /> {parsed.label}
        {#if parsed.recurrence}<Repeat2 size={14} aria-label={recurrenceLabel(parsed.recurrence)} />{/if}
      </span>
    {:else if task?.due_to}
      <span class="date-chip"><CalendarDays size={17} /> {task.due_to}{#if task.recurrence}<Repeat2 size={14} />{/if}</span>
    {/if}
    <button class="chip-button" title="Флаг" aria-label="Флаг"><Flag size={18} /></button>
    {#if sections.length > 0}
      <select bind:value={selectedSection} aria-label="Раздел задачи">
        {#each sections as option}
          <option value={option.id}>{option.title}</option>
        {/each}
      </select>
    {/if}
    <span class="composer-spacer"></span>
    <button class="cancel-button" onclick={onCancel} aria-label="Отменить"><X size={27} /></button>
    <button class="submit-button" onclick={() => void submit()} disabled={!value.trim() || saving} aria-label="Сохранить задачу">
      <Check size={23} />
    </button>
  </div>
</div>
