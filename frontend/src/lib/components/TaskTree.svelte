<script lang="ts">
  import TaskItem from './TaskItem.svelte';
  import TaskComposer from './TaskComposer.svelte';
  import TaskTree from './TaskTree.svelte';
  import type { Section, Task, TaskDraft, TaskDropMode } from '$lib/types';

  let {
    tasks,
    parentId = null,
    depth = 0,
    variant = 'list',
    onToggle,
    onEdit,
    onArchive,
    onDelete,
    onMove,
    onDragStart,
    dropTarget = null,
    draggedTaskId = null,
    collapsedIds,
    onCollapseToggle,
    onAddSubtask,
    newSubtaskParent = null,
    onSaveNewTask,
    onCancelNewTask,
    editingTask = null,
    editSections = [],
    onSaveEdit,
    onCancelEdit,
    onSaveAndContinue,
    continuationAfter = null,
    onSaveContinuation,
    onCancelContinuation,
    onSchedule
  }: {
    tasks: Task[];
    parentId?: string | null;
    depth?: number;
    variant?: 'list' | 'card';
    onToggle: (task: Task) => void;
    onEdit: (task: Task) => void;
    onArchive: (task: Task) => void;
    onDelete: (task: Task) => void;
    onMove: (task: Task) => void;
    onDragStart: (task: Task, event: PointerEvent) => void;
    dropTarget?: { taskId: string; mode: TaskDropMode } | null;
    draggedTaskId?: string | null;
    collapsedIds?: Set<string>;
    onCollapseToggle?: (task: Task) => void;
    onAddSubtask?: (task: Task) => void;
    newSubtaskParent?: Task | null;
    onSaveNewTask?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancelNewTask?: () => void;
    editingTask?: Task | null;
    editSections?: Section[];
    onSaveEdit?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancelEdit?: () => void;
    onSaveAndContinue?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    continuationAfter?: Task | null;
    onSaveContinuation?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancelContinuation?: () => void;
    onSchedule?: (task: Task, dueTo: string) => void;
  } = $props();

  const directTasks = $derived(tasks.filter((task) => task.parent_task_id === parentId || (parentId === null && task.parent_task_id && !tasks.some((candidate) => candidate.id === task.parent_task_id))));
</script>

{#each directTasks as task (task.id)}
  {@const children = tasks.filter((candidate) => candidate.parent_task_id === task.id)}
  {#if editingTask?.id === task.id && onSaveEdit && onCancelEdit}
    <div class:task-card={variant === 'card'} class="inline-edit" style={`--depth: ${depth}`} role="listitem">
      <TaskComposer {task} section={task.section_id} sections={editSections} onSave={onSaveEdit} {onSaveAndContinue} onCancel={onCancelEdit} />
    </div>
  {:else}
    <TaskItem {task} {depth} {variant} childCount={children.length} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} dropMode={dropTarget?.taskId === task.id ? dropTarget.mode : null} dragging={draggedTaskId === task.id} collapsed={collapsedIds?.has(task.id) ?? false} {onCollapseToggle} {onAddSubtask} {onSchedule} />
  {/if}
  {#if children.length && !collapsedIds?.has(task.id)}
    <TaskTree {tasks} parentId={task.id} depth={depth + 1} {variant} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} {dropTarget} {draggedTaskId} {collapsedIds} {onCollapseToggle} {onAddSubtask} {newSubtaskParent} {onSaveNewTask} {onCancelNewTask} {editingTask} {editSections} {onSaveEdit} {onCancelEdit} {onSaveAndContinue} {continuationAfter} {onSaveContinuation} {onCancelContinuation} {onSchedule} />
  {/if}
  {#if newSubtaskParent?.id === task.id && onSaveNewTask && onCancelNewTask}
    <div class:task-card={variant === 'card'} class="inline-edit" style={`--depth: ${depth + 1}`} role="listitem">
      <TaskComposer section={task.section_id} onSave={onSaveNewTask} onCancel={onCancelNewTask} />
    </div>
  {/if}
  {#if continuationAfter?.id === task.id && onSaveContinuation && onCancelContinuation}
    <div class:task-card={variant === 'card'} class="inline-edit" style={`--depth: ${depth}`} role="listitem">
      <TaskComposer section={task.section_id} defaultDueTo={continuationAfter.due_to} onSave={onSaveContinuation} onCancel={onCancelContinuation} />
    </div>
  {/if}
{/each}
