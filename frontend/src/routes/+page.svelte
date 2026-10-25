<script lang="ts">
  import { goto, replaceState } from '$app/navigation';
  import { onMount } from 'svelte';
  import { ArchiveRestore, Menu, Pencil, Plus, Search, Trash2 } from '@lucide/svelte';
  import { api, ApiError } from '$lib/api';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import TaskComposer from '$lib/components/TaskComposer.svelte';
  import TaskTree from '$lib/components/TaskTree.svelte';
  import type { Section, Task, TaskDraft, User } from '$lib/types';
  import { getLocale, initLocale, localizedError, localizedSectionTitle, t } from '$lib/i18n.svelte';

  type View = 'section' | 'search' | 'calendar' | 'archived';
  type SectionDialog = { mode: 'new' | 'rename' | 'move' | 'delete'; section: Section | null };

  let user = $state<User | null>(null);
  let sectionsTree = $state<Section[]>([]);
  let selected = $state<Section | null>(null);
  let tasks = $state<Task[]>([]);
  let view = $state<View>('section');
  let loading = $state(true);
  let sidebarOpen = $state(false);
  let composerOpen = $state(false);
  let editingTask = $state<Task | null>(null);
  let moveTaskTarget = $state<Task | null>(null);
  let draggedTask = $state<Task | null>(null);
  let toast = $state('');
  let query = $state('');
  let searchResults = $state<Task[]>([]);
  let calendarGroups = $state<{ date: string; tasks: Task[] }[]>([]);
  let overdueTasks = $state<Task[]>([]);
  let sectionDialog = $state<SectionDialog | null>(null);
  let dialogTitle = $state('');
  let dialogParent = $state('');
  let sectionMenu = $state<{ section: Section; x: number; y: number } | null>(null);
  let collapsed = $state<Set<string>>(new Set());
  let subtaskParent = $state<Task | null>(null);
  let continuationAfter = $state<Task | null>(null);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;
  let sectionCounts = $state<Record<string, number>>({});
  let draggedSection = $state<Section | null>(null);

  const root = $derived(sectionsTree.find((section) => section.parent_id === null) ?? null);
  const visibleSections = $derived(root ? root.subsections : sectionsTree);
  const allSections = $derived(flatten(visibleSections));
  const leafSections = $derived(allSections.filter((section) => section.subsections.length === 0));
  const heading = $derived(view === 'section' ? localizedSectionTitle(selected?.title ?? t('tasks')) : view === 'search' ? t('search') : view === 'calendar' ? t('calendar') : t('archive'));

  function flatten(items: Section[]): Section[] {
    return items.flatMap((section) => [section, ...flatten(section.subsections)]);
  }

  function notify(message: string) {
    toast = message;
    setTimeout(() => { if (toast === message) toast = ''; }, 3300);
  }

  async function safe(action: () => Promise<void>, fallback = t('somethingWrong')) {
    try { await action(); }
    catch (reason) { notify(reason instanceof ApiError ? localizedError(reason.message, fallback) : fallback); }
  }

  onMount(() => {
    initLocale();
    void initialize();
    const keyHandler = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing = target?.matches('input, textarea, select, [contenteditable="true"]');
      if (!typing && (event.code === 'KeyQ' || event.key.toLocaleLowerCase('ru-RU') === 'q' || event.key.toLocaleLowerCase('ru-RU') === 'й')) {
        event.preventDefault();
        if (selected || leafSections.length) { editingTask = null; subtaskParent = null; composerOpen = true; }
      }
      if (!typing && event.key === '/') {
        event.preventDefault();
        void changeView('search');
        queueMicrotask(() => document.querySelector<HTMLInputElement>('.search-input')?.focus());
      }
      if (event.key === 'Escape') { composerOpen = false; editingTask = null; subtaskParent = null; continuationAfter = null; moveTaskTarget = null; sectionDialog = null; sectionMenu = null; }
    };
    window.addEventListener('keydown', keyHandler);
    return () => window.removeEventListener('keydown', keyHandler);
  });

  async function initialize() {
    try {
      user = await api.me();
      await loadSections();
      await loadSectionCounts();
      const wanted = new URL(location.href).searchParams.get('section');
      const initial = leafSections.find((section) => section.id === wanted) ?? leafSections[0] ?? allSections[0];
      if (initial) await selectSection(initial);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) await goto('/login');
      else notify(t('loadFailed'));
    } finally { loading = false; }
  }

  async function loadSections() { sectionsTree = await api.sections(); }

  async function loadSectionCounts() {
    const entries = await Promise.all(leafSections.map(async (section) => [section.id, (await api.section(section.id)).tasks.length] as const));
    const counts = Object.fromEntries(entries) as Record<string, number>;
    const total = (section: Section): number => counts[section.id] ?? section.subsections.reduce((sum, child) => sum + total(child), 0);
    allSections.forEach((section) => { counts[section.id] = total(section); });
    sectionCounts = counts;
  }

  function setSectionCount(sectionId: string, count: number) {
    const counts = { ...sectionCounts, [sectionId]: count };
    let current = allSections.find((section) => section.id === sectionId);
    while (current?.parent_id) {
      const parent = allSections.find((section) => section.id === current?.parent_id);
      if (!parent || parent.parent_id === null) break;
      counts[parent.id] = parent.subsections.reduce((sum, child) => sum + (counts[child.id] ?? 0), 0);
      current = parent;
    }
    sectionCounts = counts;
  }

  async function selectSection(section: Section) {
    selected = section;
    view = 'section';
    sidebarOpen = false;
    composerOpen = false;
    const loaded = await api.section(section.id);
    tasks = loaded.tasks;
    setSectionCount(section.id, loaded.tasks.length);
    const url = new URL(location.href);
    url.searchParams.set('section', section.id);
    replaceState(url, {});
  }

  async function refreshSection() {
    if (!selected) return;
    const loaded = await api.section(selected.id);
    tasks = loaded.tasks;
    setSectionCount(selected.id, loaded.tasks.length);
  }

  async function changeView(next: 'search' | 'calendar' | 'archived') {
    view = next;
    sidebarOpen = false;
    composerOpen = false;
    editingTask = null;
    if (next === 'calendar') {
      const today = new Date();
      const to = new Date(today); to.setDate(to.getDate() + 30);
      const iso = (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const result = await api.calendar(iso(today), iso(to));
      calendarGroups = result.by_dates.filter((group) => group.tasks.length);
      overdueTasks = result.overdue;
    }
    if (next === 'archived') tasks = (await api.archived()).tasks;
  }

  function search() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      searchResults = query.trim() ? await api.search(query.trim()) : [];
    }, 180);
  }

  async function saveTask(draft: TaskDraft, sectionId: string) {
    await safe(async () => {
      const movedBetweenSections = editingTask !== null && editingTask.section_id !== sectionId;
      if (editingTask) {
        await api.updateTask(editingTask.id, draft);
        if (movedBetweenSections) await api.moveTask(editingTask.id, sectionId, 0, editingTask.parent_task_id);
      } else {
        const parentId = continuationAfter?.parent_task_id ?? subtaskParent?.id ?? null;
        const created = await api.createTask(sectionId || selected!.id, draft, parentId);
        if (continuationAfter) {
          const descendants = new Set<string>();
          const collect = (parentTaskId: string) => tasks
            .filter((task) => task.parent_task_id === parentTaskId)
            .forEach((child) => { descendants.add(child.id); collect(child.id); });
          collect(continuationAfter.id);
          const lastIndex = tasks.reduce(
            (result, task, index) => task.id === continuationAfter?.id || descendants.has(task.id) ? index : result,
            -1
          );
          await api.moveTask(created.id, sectionId || selected!.id, lastIndex + 1, parentId);
        }
      }
      composerOpen = false;
      editingTask = null;
      subtaskParent = null;
      continuationAfter = null;
      if (selected) await refreshSection();
      if (movedBetweenSections) await loadSectionCounts();
      notify(t('taskSaved'));
    });
  }

  async function saveTaskAndContinue(draft: TaskDraft, sectionId: string) {
    const current = editingTask;
    if (!current) return;
    let saved = false;
    await safe(async () => {
      await api.updateTask(current.id, draft);
      if (current.section_id !== sectionId) {
        await api.moveTask(current.id, sectionId, 0, current.parent_task_id);
        await loadSectionCounts();
      }
      await refreshSection();
      saved = true;
      notify(t('taskSaved'));
    });
    if (!saved) return;
    editingTask = null;
    continuationAfter = { ...current, section_id: sectionId };
    composerOpen = true;
  }

  async function toggleTask(task: Task) { await safe(async () => { await api.toggleTask(task.id); await refreshCurrent(); }); }
  async function archiveTask(task: Task) { await safe(async () => { await api.archiveTask(task.id); await refreshCurrent(); notify(t('taskArchived')); }); }
  async function scheduleTask(task: Task, dueTo: string) {
    await safe(async () => {
      await api.updateTask(task.id, { due_to: dueTo });
      await refreshCurrent();
      notify(t('taskScheduled'));
    });
  }
  async function deleteTask(task: Task) {
    if (!confirm(`${t('deleteTaskPrompt')} «${task.title}»?`)) return;
    await safe(async () => { await api.deleteTask(task.id); await refreshCurrent(); });
  }
  async function refreshCurrent() {
    if (view === 'section') await refreshSection();
    else if (view === 'archived') tasks = (await api.archived()).tasks;
    else if (view === 'search') searchResults = query ? await api.search(query) : [];
    else await changeView('calendar');
  }

  function editTask(task: Task) { editingTask = task; subtaskParent = null; continuationAfter = null; composerOpen = true; }

  function openAddSubtask(task: Task) { subtaskParent = task; editingTask = null; continuationAfter = null; composerOpen = true; }

  function toggleCollapse(task: Task) {
    const next = new Set(collapsed);
    if (next.has(task.id)) next.delete(task.id);
    else next.add(task.id);
    collapsed = next;
  }

  function openMoveTask(task: Task) {
    moveTaskTarget = task;
    dialogParent = task.section_id;
  }

  async function moveTask(sectionId: string) {
    if (!moveTaskTarget) return;
    await safe(async () => {
      await api.moveTask(moveTaskTarget!.id, sectionId, 0, null);
      moveTaskTarget = null;
      await refreshCurrent();
      await loadSectionCounts();
      notify(t('taskMoved'));
    });
  }

  async function dropTask(target: Task, mode: 'before' | 'child') {
    if (!draggedTask || draggedTask.id === target.id) return;
    const descendants = new Set<string>();
    const collect = (parentId: string) => tasks.filter((task) => task.parent_task_id === parentId).forEach((child) => { descendants.add(child.id); collect(child.id); });
    collect(draggedTask.id);
    if (descendants.has(target.id)) { notify(t('cannotNestTask')); return; }
    let index = tasks.findIndex((task) => task.id === target.id);
    if (draggedTask.section_id === target.section_id) {
      const sourceIndex = tasks.findIndex((task) => task.id === draggedTask!.id);
      if (sourceIndex < index) index -= 1;
    }
    await safe(async () => {
      await api.moveTask(draggedTask!.id, target.section_id, Math.max(0, mode === 'child' ? index + 1 : index), mode === 'child' ? target.id : target.parent_task_id);
      draggedTask = null;
      await refreshSection();
    });
  }

  async function dropSection(target: Section) {
    const source = draggedSection;
    draggedSection = null;
    if (!source || source.id === target.id || !target.parent_id) return;
    const descendants = new Set(flatten(source.subsections).map((section) => section.id));
    if (descendants.has(target.id)) { notify(t('cannotNestSection')); return; }
    const siblings = allSections.filter((section) => section.parent_id === target.parent_id);
    let index = siblings.findIndex((section) => section.id === target.id);
    const sourceIndex = siblings.findIndex((section) => section.id === source.id);
    if (source.parent_id === target.parent_id && sourceIndex >= 0 && sourceIndex < index) index -= 1;
    await safe(async () => {
      await api.moveSection(source.id, target.parent_id!, Math.max(0, index));
      await loadSections();
      await loadSectionCounts();
      notify(t('sectionMoved'));
    });
  }

  function openNewSection() { dialogTitle = ''; dialogParent = root?.id ?? ''; sectionDialog = { mode: 'new', section: null }; }
  function openSectionMenu(event: MouseEvent, section: Section) { sectionMenu = { section, x: event.clientX, y: event.clientY }; }
  function startSectionAction(mode: 'rename' | 'move' | 'delete') {
    if (!sectionMenu) return;
    const section = sectionMenu.section;
    dialogTitle = section.title;
    dialogParent = section.parent_id ?? root?.id ?? '';
    sectionDialog = { mode, section };
    sectionMenu = null;
  }

  async function submitSectionDialog() {
    if (!sectionDialog) return;
    await safe(async () => {
      const { mode, section } = sectionDialog!;
      if (mode === 'new') await api.createSection(dialogTitle.trim(), dialogParent);
      if (mode === 'rename' && section) await api.updateSection(section.id, dialogTitle.trim());
      if (mode === 'move' && section) await api.moveSection(section.id, dialogParent, 0);
      if (mode === 'delete' && section) await api.deleteSection(section.id);
      sectionDialog = null;
      await loadSections();
      await loadSectionCounts();
      if (mode === 'delete' && selected?.id === section?.id) {
        const fallback = leafSections[0] ?? allSections[0];
        if (fallback) await selectSection(fallback); else { selected = null; tasks = []; }
      }
      notify(mode === 'delete' ? t('sectionDeleted') : t('sectionSaved'));
    });
  }

  async function logout() { await api.logout(); await goto('/login'); }

  async function importTodoist(file: File, eraseExisting: boolean) {
    try {
      const result = await api.importTodoist(file, eraseExisting);
      await loadSections();
      await loadSectionCounts();
      const next = leafSections[0] ?? allSections[0] ?? null;
      if (next) await selectSection(next);
      else { selected = null; tasks = []; }
      notify(t('todoistImported')
        .replace('{projects}', String(result.projects))
        .replace('{tasks}', String(result.tasks)));
    } catch (reason) {
      notify(reason instanceof ApiError
        ? localizedError(reason.message, t('todoistImportFailed'))
        : t('todoistImportFailed'));
      throw reason;
    }
  }

  function closeMoveDialogOnBackdrop(event: MouseEvent) {
    if (event.target === event.currentTarget) moveTaskTarget = null;
  }

  function closeSectionDialogOnBackdrop(event: MouseEvent) {
    if (event.target === event.currentTarget) sectionDialog = null;
  }
</script>

<svelte:head><title>{heading} · Planty</title></svelte:head>

{#if loading || !user}
  <div class="loading" aria-label={t('loading')}></div>
{:else}
  <div class="app-shell">
    <div class="mobile-header"><button onclick={() => sidebarOpen = true} aria-label={t('openMenu')}><Menu /></button><img src="/logo.png" alt="Planty" /><span></span></div>
    <Sidebar open={sidebarOpen} sections={visibleSections} selectedId={selected?.id ?? null} {user} {view} onClose={() => sidebarOpen = false} onSelectSection={(section) => void selectSection(section)} onView={(next) => void changeView(next)} onNewSection={openNewSection} onSectionMenu={openSectionMenu} onLogout={() => void logout()} {sectionCounts} onSectionDragStart={(section) => draggedSection = section} onSectionDrop={(target) => void dropSection(target)} onImportTodoist={importTodoist} />
    <main class="main-content">
      <div class="content-inner">
        <header class="page-heading">
          {#if view !== 'section'}<span class="heading-icon">{view === 'search' ? '🔎' : view === 'calendar' ? '🗓️' : '📦'}</span>{/if}
          <h1>{heading}</h1>
          <div class="heading-actions">
            {#if view === 'section'}<button onclick={() => { editingTask = null; subtaskParent = null; composerOpen = true; }} aria-label={t('addTask')}><Plus /></button>{/if}
          </div>
        </header>

        {#if view === 'section'}
          {#if composerOpen && selected && !editingTask && !continuationAfter}
            <TaskComposer section={subtaskParent ? subtaskParent.section_id : selected.id} sections={subtaskParent ? [] : leafSections} onSave={saveTask} onCancel={() => { composerOpen = false; editingTask = null; subtaskParent = null; }} />
          {/if}
          <div class="task-list" role="list">
            <TaskTree {tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={openMoveTask} onDragStart={(task) => draggedTask = task} onDropTask={(task, mode) => void dropTask(task, mode)} collapsedIds={collapsed} onCollapseToggle={toggleCollapse} onAddSubtask={openAddSubtask} {editingTask} editSections={leafSections} onSaveEdit={saveTask} onCancelEdit={() => { composerOpen = false; editingTask = null; }} onSaveAndContinue={saveTaskAndContinue} {continuationAfter} onSaveContinuation={saveTask} onCancelContinuation={() => { composerOpen = false; continuationAfter = null; }} onSchedule={(task, dueTo) => void scheduleTask(task, dueTo)} />
          </div>
          {#if selected && !composerOpen}<button class="add-task-button" onclick={() => { editingTask = null; subtaskParent = null; composerOpen = true; }}><Plus />{t('addTask')} <kbd>Q</kbd></button>{/if}
          {#if !selected}<div class="empty-state"><div class="empty-icon">🌱</div>{t('createSectionFirst')}</div>{/if}
        {:else if view === 'search'}
          <div class="search-wrap"><Search /><input class="search-input" bind:value={query} oninput={search} placeholder={t('searchTasks')} aria-label={t('searchTasks')} /></div>
          {#if query && searchResults.length === 0}<div class="empty-state">{t('nothingFound')}</div>{/if}
          <div class="task-list" role="list"><TaskTree tasks={searchResults} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={openMoveTask} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} onSchedule={(task, dueTo) => void scheduleTask(task, dueTo)} /></div>
        {:else if view === 'calendar'}
          {#if overdueTasks.length}<section class="calendar-group overdue-group"><h2>{t('overdue')}</h2><TaskTree tasks={overdueTasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={openMoveTask} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} onSchedule={(task, dueTo) => void scheduleTask(task, dueTo)} /></section>{/if}
          {#each calendarGroups as group}<section class="calendar-group"><h2>{new Date(`${group.date}T12:00:00`).toLocaleDateString(getLocale() === 'ru' ? 'ru-RU' : 'en-US', { weekday: 'long', day: 'numeric', month: 'long' })}</h2><TaskTree tasks={group.tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={openMoveTask} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} onSchedule={(task, dueTo) => void scheduleTask(task, dueTo)} /></section>{/each}
          {#if !overdueTasks.length && !calendarGroups.length}<div class="empty-state"><div class="empty-icon">☀️</div>{t('noMonthTasks')}</div>{/if}
        {:else}
          <div class="task-list" role="list"><TaskTree {tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={openMoveTask} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} onSchedule={(task, dueTo) => void scheduleTask(task, dueTo)} /></div>
          {#if !tasks.length}<div class="empty-state"><ArchiveRestore size={40} /><p>{t('archiveEmpty')}</p></div>{/if}
        {/if}
      </div>
    </main>
  </div>
{/if}

{#if moveTaskTarget}
  <div class="dialog-shield" role="presentation" onclick={closeMoveDialogOnBackdrop}><div class="dialog" role="dialog" aria-modal="true" tabindex="-1"><h2>{t('moveTask')}</h2><label>{t('newSection')}<select bind:value={dialogParent}>{#each leafSections as section}<option value={section.id}>{localizedSectionTitle(section.title)}</option>{/each}</select></label><div class="dialog-actions"><button onclick={() => moveTaskTarget = null}>{t('cancel')}</button><button class="primary" onclick={() => void moveTask(dialogParent || leafSections[0]?.id)}>{t('move')}</button></div></div></div>
{/if}

{#if sectionMenu}
  <button class="menu-shield" onclick={() => sectionMenu = null} aria-label={t('closeMenu')}></button>
  <div class="context-menu section-menu" role="menu" style={`left:${Math.min(sectionMenu.x, innerWidth - 230)}px;top:${Math.min(sectionMenu.y, innerHeight - 150)}px`}><button role="menuitem" onclick={() => startSectionAction('rename')}><Pencil size={17} />{t('rename')}</button><button role="menuitem" onclick={() => startSectionAction('move')}><Menu size={17} />{t('move')}</button><button role="menuitem" class="danger" onclick={() => startSectionAction('delete')}><Trash2 size={17} />{t('delete')}</button></div>
{/if}

{#if sectionDialog}
  <div class="dialog-shield" role="presentation" onclick={closeSectionDialogOnBackdrop}><form class="dialog" onsubmit={(event) => { event.preventDefault(); void submitSectionDialog(); }}><h2>{sectionDialog.mode === 'new' ? t('newSection') : sectionDialog.mode === 'rename' ? t('renameSection') : sectionDialog.mode === 'move' ? t('moveSection') : t('deleteSection')}</h2>{#if sectionDialog.mode === 'new' || sectionDialog.mode === 'rename'}<label>{t('sectionName')}<input bind:value={dialogTitle} required /></label>{/if}{#if sectionDialog.mode === 'new' || sectionDialog.mode === 'move'}<label>{t('parentSection')}<select bind:value={dialogParent}><option value={root?.id ?? ''}>{t('topLevel')}</option>{#each allSections.filter((candidate) => candidate.id !== sectionDialog?.section?.id) as section}<option value={section.id}>{localizedSectionTitle(section.title)}</option>{/each}</select></label>{/if}{#if sectionDialog.mode === 'delete'}<p>{t('deleteSectionHint')}</p>{/if}<div class="dialog-actions"><button type="button" onclick={() => sectionDialog = null}>{t('cancel')}</button><button class:danger={sectionDialog.mode === 'delete'} class:primary={sectionDialog.mode !== 'delete'}>{sectionDialog.mode === 'delete' ? t('delete') : t('save')}</button></div></form></div>
{/if}

{#if toast}<div class="toast" role="status">{toast}</div>{/if}
