<script lang="ts">
  import TaskItem from './TaskItem.svelte';
  import TaskComposer from './TaskComposer.svelte';
  import TaskTree from './TaskTree.svelte';
  import type { Section, Task, TaskDraft } from '$lib/types';

  let {
    tasks,
    parentId = null,
    depth = 0,
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
    <div class="inline-edit" style={`--depth: ${depth}`} role="listitem">
      <TaskComposer {task} section={task.section_id} sections={editSections} onSave={onSaveEdit} {onSaveAndContinue} onCancel={onCancelEdit} />
    </div>
  {:else}
    <TaskItem {task} {depth} childCount={children.length} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} {onDropTask} collapsed={collapsedIds?.has(task.id) ?? false} {onCollapseToggle} {onAddSubtask} {onSchedule} />
  {/if}
  {#if children.length && !collapsedIds?.has(task.id)}
    <TaskTree {tasks} parentId={task.id} depth={depth + 1} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} {onDropTask} {collapsedIds} {onCollapseToggle} {onAddSubtask} {editingTask} {editSections} {onSaveEdit} {onCancelEdit} {onSaveAndContinue} {continuationAfter} {onSaveContinuation} {onCancelContinuation} {onSchedule} />
  {/if}
  {#if continuationAfter?.id === task.id && onSaveContinuation && onCancelContinuation}
    <div class="inline-edit" style={`--depth: ${depth}`} role="listitem">
      <TaskComposer section={task.section_id} onSave={onSaveContinuation} onCancel={onCancelContinuation} />
    </div>
  {/if}
{/each}
