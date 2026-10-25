<script lang="ts">
  import { Archive, CalendarDays, LogOut, Plus, Search, X } from '@lucide/svelte';
  import SectionNode from './SectionNode.svelte';
  import type { Section, User } from '$lib/types';

  let {
    open,
    sections,
    selectedId,
    user,
    view,
    onClose,
    onSelectSection,
    onView,
    onNewSection,
    onSectionMenu,
    onLogout
  }: {
    open: boolean;
    sections: Section[];
    selectedId: string | null;
    user: User;
    view: string;
    onClose: () => void;
    onSelectSection: (section: Section) => void;
    onView: (view: 'search' | 'calendar' | 'archived') => void;
    onNewSection: () => void;
    onSectionMenu: (event: MouseEvent, section: Section) => void;
    onLogout: () => void;
  } = $props();
</script>

<aside class:open class="sidebar">
  <div class="sidebar-logo"><img src="/logo.png" alt="Planty" /><button class="mobile-only" onclick={onClose} aria-label="Закрыть меню"><X /></button></div>
  <nav class="sidebar-main" aria-label="Основная навигация">
    <button class:active={view === 'search'} onclick={() => onView('search')}><Search />Поиск <kbd>/</kbd></button>
    <button class:active={view === 'calendar'} onclick={() => onView('calendar')}><CalendarDays />Календарь</button>
    <button class:active={view === 'archived'} onclick={() => onView('archived')}><Archive />Архив</button>
  </nav>
  <div class="sections-heading"><span>Разделы</span><button onclick={onNewSection} aria-label="Добавить раздел"><Plus /></button></div>
  <div class="sections-list">
    {#each sections as section (section.id)}
      <SectionNode {section} {selectedId} onSelect={onSelectSection} onMenu={onSectionMenu} />
    {/each}
  </div>
  <div class="sidebar-user">
    <span class="avatar">{user.email.slice(0, 1).toUpperCase()}</span>
    <span class="user-email">{user.email}</span>
    <button onclick={onLogout} aria-label="Выйти"><LogOut size={18} /></button>
  </div>
</aside>
{#if open}<button class="sidebar-backdrop" onclick={onClose} aria-label="Закрыть боковую панель"></button>{/if}
