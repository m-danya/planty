<script lang="ts">
  import { taskCountLabel } from '$lib/i18n.svelte';

  let { count, testId }: { count: number; testId?: string } = $props();
</script>

<span class="task-count-slot" aria-hidden="true">
  <span class="task-count-tooltip" data-testid={testId}>{taskCountLabel(count)}</span>
</span>
