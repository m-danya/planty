<script lang="ts">
  import { Archive, CalendarDays, ChevronRight, GripVertical, MoveRight, Plus, Repeat2, Trash2 } from '@lucide/svelte';
  import type { Task, TaskDropMode } from '$lib/types';
  import { recurrenceLabel } from '$lib/date-parser';
  import { taskDatePresentation } from '$lib/task-date-presentation';
  import { getLocale, t } from '$lib/i18n.svelte';
  import DatePicker from './DatePicker.svelte';

  let {
    task,
    depth = 0,
    variant = 'list',
    childCount = 0,
    onToggle,
    onEdit,
    onArchive,
    onDelete,
    onMove,
    onDragStart,
    dropMode = null,
    dragging = false,
    collapsed = false,
    onCollapseToggle,
    onAddSubtask,
    onSchedule
  }: {
    task: Task;
    depth?: number;
    variant?: 'list' | 'card';
    childCount?: number;
    onToggle: (task: Task) => void;
    onEdit: (task: Task) => void;
    onArchive: (task: Task) => void;
    onDelete: (task: Task) => void;
    onMove: (task: Task) => void;
    onDragStart: (task: Task, event: PointerEvent) => void;
    dropMode?: TaskDropMode | null;
    dragging?: boolean;
    collapsed?: boolean;
    onCollapseToggle?: (task: Task) => void;
    onAddSubtask?: (task: Task) => void;
    onSchedule?: (task: Task, dueTo: string) => void;
  } = $props();

  let menuOpen = $state(false);
  let menuPos = $state<{ x: number; y: number } | null>(null);
  let customDateOpen = $state(false);
  let pointerId = $state<number | null>(null);

  function clickRow(event: MouseEvent) {
    if (event.altKey) onEdit(task);
  }

  function pointerDown(event: PointerEvent) {
    if (event.button !== 0) return;
    pointerId = event.pointerId;
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
    onDragStart(task, event);
  }

  function pointerEnd(event: PointerEvent) {
    if (pointerId !== event.pointerId) return;
    pointerId = null;
    const row = event.currentTarget as HTMLElement;
    if (row.hasPointerCapture(event.pointerId)) row.releasePointerCapture(event.pointerId);
  }

  function closeMenu() {
    menuOpen = false;
    menuPos = null;
    customDateOpen = false;
  }

  function localDate(offset: number): string {
    const value = new Date();
    value.setDate(value.getDate() + offset);
    return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
  }

  function schedule(dueTo: string) {
    closeMenu();
    onSchedule?.(task, dueTo);
  }

  function openDatePicker() {
    customDateOpen = !customDateOpen;
  }

  function calendarPosition(): { x: number; y: number } {
    if (!menuPos) return { x: 8, y: 8 };
    const width = 310;
    const height = 390;
    const right = menuPos.x + 268;
    const x = right + width <= innerWidth - 8 ? right : Math.max(8, menuPos.x - width - 8);
    return { x, y: Math.max(8, Math.min(menuPos.y, innerHeight - height - 8)) };
  }

</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
  class:completed={task.is_completed}
  class:task-card={variant === 'card'}
  class:bare={!task.due_to && !task.description}
  class:dragging
  class:drop-before={dropMode === 'preserve' || dropMode === 'outdent'}
  class:drop-child={dropMode === 'child'}
  class="task-row"
  style={`--depth: ${depth}`}
  data-task-id={task.id}
  data-testid="task-row"
  role="listitem"
  draggable="false"
  onclick={clickRow}
  oncontextmenu={(event) => { event.preventDefault(); menuOpen = true; menuPos = { x: event.clientX, y: event.clientY }; }}
>
  <button class="drag-handle" aria-label={t('dragTask')} onpointerdown={pointerDown} onpointerup={pointerEnd} onpointercancel={pointerEnd} onclick={(event) => event.stopPropagation()}><GripVertical size={16} /></button>
  <div class="task-chevron-slot">
    {#if childCount > 0}
      {#if onCollapseToggle}
        <button class="task-chevron" class:expanded={!collapsed} aria-label={collapsed ? t('expandSubtasks') : t('collapseSubtasks')} aria-expanded={!collapsed} onclick={(event) => { event.stopPropagation(); onCollapseToggle(task); }}><ChevronRight size={16} /></button>
      {:else}
        <span class="task-chevron"><ChevronRight size={16} /></span>
      {/if}
    {/if}
  </div>
  <button class="complete-button" aria-label={task.is_completed ? t('restoreTask') : t('completeTask')} onclick={(event) => { event.stopPropagation(); onToggle(task); }}></button>
  <div class="task-copy">
    <div class="task-title">{task.title}</div>
    {#if task.description}<div class="task-description">{task.description}</div>{/if}
    {#if task.due_to}
      {@const due = taskDatePresentation(task.due_to)}
      <div class={`task-date ${due.className}`}><CalendarDays size={15} />{due.text}{#if task.due_time}<span class="task-time">· {task.due_time.slice(0, 5)}</span>{/if}{#if task.recurrence}<Repeat2 size={14} aria-label={recurrenceLabel(task.recurrence, getLocale())} />{/if}</div>
    {/if}
  </div>
  {#if menuOpen}
    <button class="menu-shield" aria-label={t('closeMenu')} onclick={(event) => { event.stopPropagation(); closeMenu(); }}></button>
    {#if menuPos}
    <div class="context-menu task-menu" role="menu" tabindex="-1" style={`left:${Math.max(8, Math.min(menuPos.x, innerWidth - 260))}px;top:${Math.max(8, Math.min(menuPos.y, innerHeight - 340))}px`}>
      <button role="menuitem" onclick={() => { closeMenu(); onMove(task); }}><MoveRight size={18} />{t('otherSection')}</button>
      {#if onAddSubtask}
        <button role="menuitem" onclick={() => { closeMenu(); onAddSubtask(task); }}><Plus size={18} />{t('addSubtask')}</button>
      {/if}
      {#if onSchedule}
        <div class="menu-separator"></div>
        <button role="menuitem" onclick={() => schedule(localDate(0))}><CalendarDays size={18} />{t('assignTo')} <span class="date-today">{t('todayLower')}</span></button>
        <button role="menuitem" onclick={() => schedule(localDate(1))}><CalendarDays size={18} />{t('assignTo')} <span class="date-tomorrow">{t('tomorrowLower')}</span></button>
        <button role="menuitem" aria-expanded={customDateOpen} onclick={openDatePicker}><CalendarDays size={18} />{t('assignOtherDay')}</button>
        <div class="menu-separator"></div>
      {/if}
      <button role="menuitem" onclick={() => { closeMenu(); onArchive(task); }}>
        <Archive size={18} />{task.is_archived ? t('restoreArchive') : t('toArchive')}
      </button>
      <button class="danger" role="menuitem" onclick={() => { closeMenu(); onDelete(task); }}><Trash2 size={18} />{t('delete')}</button>
    </div>
    {#if customDateOpen}
      {@const calendar = calendarPosition()}
      <DatePicker value={task.due_to} x={calendar.x} y={calendar.y} onSelect={schedule} onClose={() => customDateOpen = false} />
    {/if}
    {/if}
  {/if}
</div>
