<script lang="ts">
  import { Archive, CalendarDays, FileUp, LogOut, Play, Plus, Search, Settings, X } from '@lucide/svelte';
  import SectionNode from './SectionNode.svelte';
  import type { Section, User } from '$lib/types';
  import { getLocale, setLocale, t, type Locale } from '$lib/i18n.svelte';
  import {
    COMPLETION_SOUNDS,
    getAutoArchive,
    getCompletionSound,
    playCompletionSound,
    setAutoArchive,
    setCompletionSound,
    type CompletionSoundId
  } from '$lib/preferences.svelte';

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
    onSectionDragStart,
    onSectionDrop,
    onImportTodoist
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
    onSectionDragStart: (section: Section) => void;
    onSectionDrop: (target: Section) => void;
    onImportTodoist: (file: File, eraseExisting: boolean) => Promise<void>;
  } = $props();
  let settingsOpen = $state(false);
  let importFile = $state<File | null>(null);
  let eraseExisting = $state(true);
  let importing = $state(false);

  function openSettings() {
    importFile = null;
    eraseExisting = true;
    settingsOpen = true;
  }

  async function importTodoist() {
    if (!importFile || importing) return;
    importing = true;
    try {
      await onImportTodoist(importFile, eraseExisting);
      settingsOpen = false;
      importFile = null;
    } finally {
      importing = false;
    }
  }
</script>

<aside class:open class="sidebar">
  <div class="sidebar-logo"><img src="/logo.png" alt="Planty" /><button class="mobile-only" onclick={onClose} aria-label={t('closeMenu')}><X /></button></div>
  <nav class="sidebar-main" aria-label={t('sections')}>
    <button class:active={view === 'search'} onclick={() => onView('search')}><Search />{t('search')} <kbd>F</kbd></button>
    <button class:active={view === 'calendar'} onclick={() => onView('calendar')}><CalendarDays />{t('calendar')}</button>
    <button class:active={view === 'archived'} onclick={() => onView('archived')}><Archive />{t('archive')}</button>
  </nav>
  <div class="sections-heading"><span>{t('sections')}</span><button onclick={onNewSection} aria-label={t('addSection')}><Plus /></button></div>
  <div class="sections-list">
    {#each sections as section (section.id)}
      <SectionNode {section} {selectedId} onSelect={onSelectSection} onMenu={onSectionMenu} onDragStart={onSectionDragStart} onDropSection={onSectionDrop} />
    {/each}
  </div>
  <div class="sidebar-user">
    <button class="profile-button" onclick={openSettings} aria-label={t('settings')}>
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
      <label class="settings-toggle">
        <input type="checkbox" checked={getAutoArchive()} onchange={(event) => setAutoArchive(event.currentTarget.checked)} />
        <span>{t('autoArchive')}</span>
      </label>
      <div class="sound-setting">
        <label for="completion-sound">{t('completionSound')}</label>
        <div class="sound-setting-row">
          <select id="completion-sound" value={getCompletionSound()} onchange={(event) => setCompletionSound((event.currentTarget as HTMLSelectElement).value as CompletionSoundId)}>
            <option value="none">{t('noSound')}</option>
            {#each COMPLETION_SOUNDS as sound}
              <option value={sound.id}>{sound.label}</option>
            {/each}
          </select>
          <button
            type="button"
            class="sound-preview-button"
            disabled={getCompletionSound() === 'none'}
            onclick={playCompletionSound}
            aria-label={t('previewCompletionSound')}
            title={t('previewCompletionSound')}
          ><Play size={18} /></button>
        </div>
      </div>
      <section class="import-settings">
        <h3>{t('todoistImport')}</h3>
        <p>{t('todoistImportHint')}</p>
        <label class="file-picker">
          <FileUp size={19} />
          <span>{importFile?.name ?? t('chooseTodoistBackup')}</span>
          <input
            type="file"
            accept=".zip,application/zip"
            onchange={(event) => importFile = (event.currentTarget as HTMLInputElement).files?.[0] ?? null}
          />
        </label>
        <label class="checkbox-label">
          <input type="checkbox" bind:checked={eraseExisting} />
          <span>{t('eraseCurrentData')}</span>
        </label>
        <button class="import-button" disabled={!importFile || importing} onclick={() => void importTodoist()}>
          {importing ? t('importing') : t('importTodoist')}
        </button>
      </section>
      <div class="dialog-actions"><button class="primary" onclick={() => settingsOpen = false}>{t('done')}</button></div>
    </div>
  </div>
{/if}
