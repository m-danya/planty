<script lang="ts">
  import TaskTree from './TaskTree.svelte';
  import type { Section, Task, TaskDraft, TaskDropMode } from '$lib/types';

  let {
    tasks,
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
    editDateOpen = false,
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
    variant?: 'list' | 'card';
    onToggle: (task: Task) => void;
    onEdit: (task: Task, openDateDetails?: boolean) => void;
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
    editDateOpen?: boolean;
    editSections?: Section[];
    onSaveEdit?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancelEdit?: () => void;
    onSaveAndContinue?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    continuationAfter?: Task | null;
    onSaveContinuation?: (draft: TaskDraft, sectionId: string) => void | Promise<void>;
    onCancelContinuation?: () => void;
    onSchedule?: (task: Task, dueTo: string) => void;
  } = $props();
</script>

<div class:board-cards={variant === 'card'} class="task-list" role="list">
  <TaskTree
    {tasks}
    {variant}
    {onToggle}
    {onEdit}
    {onArchive}
    {onDelete}
    {onMove}
    {onDragStart}
    {dropTarget}
    {draggedTaskId}
    {collapsedIds}
    {onCollapseToggle}
    {onAddSubtask}
    {newSubtaskParent}
    {onSaveNewTask}
    {onCancelNewTask}
    {editingTask}
    {editDateOpen}
    {editSections}
    {onSaveEdit}
    {onCancelEdit}
    {onSaveAndContinue}
    {continuationAfter}
    {onSaveContinuation}
    {onCancelContinuation}
    {onSchedule}
  />
</div>
