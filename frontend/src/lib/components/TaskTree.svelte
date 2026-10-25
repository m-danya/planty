<script lang="ts">
  import TaskItem from './TaskItem.svelte';
  import TaskTree from './TaskTree.svelte';
  import type { Task } from '$lib/types';

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
    onDropTask
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
  } = $props();

  const directTasks = $derived(tasks.filter((task) => task.parent_task_id === parentId || (parentId === null && task.parent_task_id && !tasks.some((candidate) => candidate.id === task.parent_task_id))));
</script>

{#each directTasks as task (task.id)}
  {@const children = tasks.filter((candidate) => candidate.parent_task_id === task.id)}
  <TaskItem {task} {depth} childCount={children.length} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} {onDropTask} />
  {#if children.length}
    <TaskTree {tasks} parentId={task.id} depth={depth + 1} {onToggle} {onEdit} {onArchive} {onDelete} {onMove} {onDragStart} {onDropTask} />
  {/if}
{/each}
