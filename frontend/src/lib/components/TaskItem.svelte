<script lang="ts">
  import { Archive, CalendarDays, ChevronRight, GripVertical, MoveRight, Repeat2, Trash2 } from '@lucide/svelte';
  import type { Task } from '$lib/types';
  import { recurrenceLabel } from '$lib/date-parser';

  let {
    task,
    depth = 0,
    childCount = 0,
    onToggle,
    onEdit,
    onArchive,
    onDelete,
    onMove,
    onDragStart,
    onDropTask
  }: {
    task: Task;
    depth?: number;
    childCount?: number;
    onToggle: (task: Task) => void;
    onEdit: (task: Task) => void;
    onArchive: (task: Task) => void;
    onDelete: (task: Task) => void;
    onMove: (task: Task) => void;
    onDragStart: (task: Task) => void;
    onDropTask: (target: Task, mode: 'before' | 'child') => void;
  } = $props();

  let menuOpen = $state(false);
  let dragMode = $state<'before' | 'child' | null>(null);

  function dateLabel(value: string): { text: string; className: string } {
    const due = new Date(`${value}T12:00:00`);
    const today = new Date();
    today.setHours(12, 0, 0, 0);
    const diff = Math.round((due.getTime() - today.getTime()) / 86400000);
    if (diff < 0) return { text: due.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }), className: 'overdue' };
    if (diff === 0) return { text: 'Сегодня', className: 'today' };
    if (diff === 1) return { text: 'Завтра', className: 'tomorrow' };
    return { text: due.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }), className: 'future' };
  }

  function clickRow(event: MouseEvent) {
    if (event.altKey) onEdit(task);
  }

  function dragOver(event: DragEvent) {
    event.preventDefault();
    const target = event.currentTarget as HTMLElement;
    const rect = target.getBoundingClientRect();
    dragMode = event.clientY < rect.top + rect.height * 0.28 ? 'before' : 'child';
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
  class:completed={task.is_completed}
  class:drop-before={dragMode === 'before'}
  class:drop-child={dragMode === 'child'}
  class="task-row"
  style={`--depth: ${depth}`}
  data-task-id={task.id}
  data-testid="task-row"
  role="listitem"
  draggable="true"
  ondragstart={(event) => {
    event.dataTransfer?.setData('text/plain', task.id);
    if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move';
    onDragStart(task);
  }}
  ondragover={dragOver}
  ondragleave={() => (dragMode = null)}
  ondrop={(event) => {
    event.preventDefault();
    onDropTask(task, dragMode ?? 'before');
    dragMode = null;
  }}
  onclick={clickRow}
  oncontextmenu={(event) => { event.preventDefault(); menuOpen = true; }}
>
  <button class="drag-handle" aria-label="Перетащить задачу"><GripVertical size={16} /></button>
  {#if childCount > 0}<ChevronRight class="task-chevron" size={18} />{/if}
  <button class="complete-button" aria-label={task.is_completed ? 'Вернуть задачу' : 'Выполнить задачу'} onclick={(event) => { event.stopPropagation(); onToggle(task); }}></button>
  <div class="task-copy">
    <div class="task-title">{task.title}</div>
    {#if task.description}<div class="task-description">{task.description}</div>{/if}
    {#if task.due_to}
      {@const due = dateLabel(task.due_to)}
      <div class={`task-date ${due.className}`}><CalendarDays size={15} />{due.text}{#if task.recurrence}<Repeat2 size={14} aria-label={recurrenceLabel(task.recurrence)} />{/if}</div>
    {/if}
  </div>
  {#if menuOpen}
    <button class="menu-shield" aria-label="Закрыть меню" onclick={(event) => { event.stopPropagation(); menuOpen = false; }}></button>
    <div class="context-menu" role="menu" tabindex="-1">
      <button role="menuitem" onclick={() => { menuOpen = false; onMove(task); }}><MoveRight size={18} />В другой раздел</button>
      <button role="menuitem" onclick={() => { menuOpen = false; onArchive(task); }}><Archive size={18} />В архив</button>
      <button class="danger" role="menuitem" onclick={() => { menuOpen = false; onDelete(task); }}><Trash2 size={18} />Удалить</button>
    </div>
  {/if}
</div>
