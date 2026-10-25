<script lang="ts">
  import { ChevronDown, ChevronRight, Ellipsis, GripVertical } from '@lucide/svelte';
  import SectionNode from './SectionNode.svelte';
  import type { Section } from '$lib/types';
  import { localizedSectionTitle, taskCountLabel, t } from '$lib/i18n.svelte';

  let {
    section,
    selectedId,
    depth = 0,
    onSelect,
    onMenu,
    counts = {},
    onDragStart,
    onDropSection
  }: {
    section: Section;
    selectedId: string | null;
    depth?: number;
    onSelect: (section: Section) => void;
    onMenu: (event: MouseEvent, section: Section) => void;
    counts?: Record<string, number>;
    onDragStart: (section: Section) => void;
    onDropSection: (target: Section) => void;
  } = $props();
  let open = $state(true);
  let dragOver = $state(false);

  function handleClick(event: MouseEvent) {
    const target = event.target;
    if (target instanceof Element && target.closest('.section-more')) {
      event.preventDefault();
      event.stopPropagation();
      onMenu(event, section);
      return;
    }
    onSelect(section);
  }
</script>

<div class="section-node" style={`--section-depth: ${depth}`}>
  <button
    class="section-link"
    class:active={selectedId === section.id}
    class:section-drop={dragOver}
    draggable="true"
    title={taskCountLabel(counts[section.id] ?? section.tasks.length)}
    onclick={handleClick}
    oncontextmenu={(event) => { event.preventDefault(); onMenu(event, section); }}
    ondragstart={(event) => { event.dataTransfer?.setData('text/plain', section.id); onDragStart(section); }}
    ondragover={(event) => { event.preventDefault(); dragOver = true; }}
    ondragleave={() => dragOver = false}
    ondrop={(event) => { event.preventDefault(); dragOver = false; onDropSection(section); }}
  >
    <GripVertical class="section-grip" size={13} aria-label={t('dragSection')} />
    {#if section.subsections.length}
      <span class="section-toggle" role="button" tabindex="0" onclick={(event) => { event.stopPropagation(); open = !open; }} onkeydown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); event.stopPropagation(); open = !open; } }}>
        {#if open}<ChevronDown size={16} />{:else}<ChevronRight size={16} />{/if}
      </span>
    {:else}<span class="section-toggle"></span>{/if}
    <span>{localizedSectionTitle(section.title)}</span>
    <Ellipsis class="section-more" size={17} />
  </button>
  {#if open}
    {#each section.subsections as child (child.id)}
      <SectionNode section={child} {selectedId} depth={depth + 1} {onSelect} {onMenu} {counts} {onDragStart} {onDropSection} />
    {/each}
  {/if}
</div>
