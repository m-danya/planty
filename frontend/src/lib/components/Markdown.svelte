<script lang="ts">
  import { parseMarkdown, type MarkdownInline } from '$lib/markdown';

  let { source }: { source: string } = $props();
  const blocks = $derived(parseMarkdown(source));
</script>

{#snippet renderInline(nodes: MarkdownInline[])}
  {#each nodes as node}
    {#if node.type === 'text'}
      {node.value}
    {:else if node.type === 'strong'}
      <strong>{@render renderInline(node.children)}</strong>
    {:else if node.type === 'emphasis'}
      <em>{@render renderInline(node.children)}</em>
    {:else if node.type === 'strikethrough'}
      <del>{@render renderInline(node.children)}</del>
    {:else if node.type === 'link'}
      <a href={node.href} target="_blank" rel="noopener noreferrer">{@render renderInline(node.children)}</a>
    {/if}
  {/each}
{/snippet}

{#each blocks as block}
  {#if block.type === 'paragraph'}
    <p>{@render renderInline(block.children)}</p>
  {:else}
    <ul>
      {#each block.items as item}
        <li>{@render renderInline(item)}</li>
      {/each}
    </ul>
  {/if}
{/each}
