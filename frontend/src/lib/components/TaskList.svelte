<script lang="ts">
  import TaskTree from './TaskTree.svelte';
  import type { Section, Task, TaskDraft } from '$lib/types';

  let {
    tasks,
    variant = 'list',
    onToggle,
    onEdit,
    onArchive,
    onDelete,
    onMove,
    onDragStart,
    onDropTask,
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
    variant?: 'list' | 'card';
    onToggle: (task: Task) => void;
    onEdit: (task: Task) => void;
    onArchive: (task: Task) => void;
    onDelete: (task: Task) => void;
    onMove: (task: Task) => void;
    onDragStart: (task: Task) => void;
    onDropTask: (target: Task, mode: 'before' | 'child') => void;
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
    {onDropTask}
    {collapsedIds}
    {onCollapseToggle}
    {onAddSubtask}
    {newSubtaskParent}
    {onSaveNewTask}
    {onCancelNewTask}
    {editingTask}
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
