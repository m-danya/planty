<script lang="ts">
  import { Archive, CalendarDays, LogOut, Plus, Search, Settings, X } from '@lucide/svelte';
  import SectionNode from './SectionNode.svelte';
  import type { Section, User } from '$lib/types';
  import { getLocale, setLocale, t, type Locale } from '$lib/i18n.svelte';

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
    onLogout,
    sectionCounts = {},
    onSectionDragStart,
    onSectionDrop
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
    sectionCounts?: Record<string, number>;
    onSectionDragStart: (section: Section) => void;
    onSectionDrop: (target: Section) => void;
  } = $props();
  let settingsOpen = $state(false);
</script>

<aside class:open class="sidebar">
  <div class="sidebar-logo"><img src="/logo.png" alt="Planty" /><button class="mobile-only" onclick={onClose} aria-label={t('closeMenu')}><X /></button></div>
  <nav class="sidebar-main" aria-label={t('sections')}>
    <button class:active={view === 'search'} onclick={() => onView('search')}><Search />{t('search')} <kbd>/</kbd></button>
    <button class:active={view === 'calendar'} onclick={() => onView('calendar')}><CalendarDays />{t('calendar')}</button>
    <button class:active={view === 'archived'} onclick={() => onView('archived')}><Archive />{t('archive')}</button>
  </nav>
  <div class="sections-heading"><span>{t('sections')}</span><button onclick={onNewSection} aria-label={t('addSection')}><Plus /></button></div>
  <div class="sections-list">
    {#each sections as section (section.id)}
      <SectionNode {section} {selectedId} onSelect={onSelectSection} onMenu={onSectionMenu} counts={sectionCounts} onDragStart={onSectionDragStart} onDropSection={onSectionDrop} />
    {/each}
  </div>
  <div class="sidebar-user">
    <button class="profile-button" onclick={() => settingsOpen = true} aria-label={t('settings')}>
      <span class="avatar">{user.email.slice(0, 1).toUpperCase()}</span><span class="user-email">{user.email}</span><Settings size={17} />
    </button>
    <button onclick={onLogout} aria-label={t('logout')}><LogOut size={18} /></button>
  </div>
</aside>
{#if open}<button class="sidebar-backdrop" onclick={onClose} aria-label={t('closeSidebar')}></button>{/if}

{#if settingsOpen}
  <div class="dialog-shield" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) settingsOpen = false; }}>
    <div class="dialog settings-dialog" role="dialog" aria-modal="true" aria-label={t('settings')}>
      <h2>{t('settings')}</h2>
      <label>{t('language')}
        <select value={getLocale()} onchange={(event) => setLocale((event.currentTarget as HTMLSelectElement).value as Locale)}>
          <option value="ru">{t('russian')}</option><option value="en">{t('english')}</option>
        </select>
      </label>
      <div class="dialog-actions"><button class="primary" onclick={() => settingsOpen = false}>{t('done')}</button></div>
    </div>
  </div>
{/if}
