<script lang="ts">
  import '../styles.css';
  let { children } = $props();
</script>

<svelte:head>
  <title>Planty</title>
  <meta name="description" content="A calm place for everything you need to do" />
  <meta name="theme-color" content="#16a34a" />
</svelte:head>

{@render children()}
