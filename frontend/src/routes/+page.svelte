<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { ArchiveRestore, Ellipsis, Menu, Pencil, Plus, Search, Trash2 } from '@lucide/svelte';
  import { api, ApiError } from '$lib/api';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import TaskComposer from '$lib/components/TaskComposer.svelte';
  import TaskTree from '$lib/components/TaskTree.svelte';
  import type { Section, Task, TaskDraft, User } from '$lib/types';

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
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  const root = $derived(sectionsTree.find((section) => section.parent_id === null) ?? null);
  const visibleSections = $derived(root ? root.subsections : sectionsTree);
  const allSections = $derived(flatten(visibleSections));
  const leafSections = $derived(allSections.filter((section) => section.subsections.length === 0));
  const heading = $derived(view === 'section' ? selected?.title ?? 'Задачи' : view === 'search' ? 'Поиск' : view === 'calendar' ? 'Календарь' : 'Архив');

  function flatten(items: Section[]): Section[] {
    return items.flatMap((section) => [section, ...flatten(section.subsections)]);
  }

  function notify(message: string) {
    toast = message;
    setTimeout(() => { if (toast === message) toast = ''; }, 3300);
  }

  async function safe(action: () => Promise<void>, fallback = 'Что-то пошло не так') {
    try { await action(); }
    catch (reason) { notify(reason instanceof ApiError ? reason.message : fallback); }
  }

  onMount(() => {
    void initialize();
    const keyHandler = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing = target?.matches('input, textarea, select, [contenteditable="true"]');
      if (!typing && (event.code === 'KeyQ' || event.key.toLocaleLowerCase('ru-RU') === 'q' || event.key.toLocaleLowerCase('ru-RU') === 'й')) {
        event.preventDefault();
        if (selected || leafSections.length) { editingTask = null; composerOpen = true; }
      }
      if (!typing && event.key === '/') {
        event.preventDefault();
        void changeView('search');
        queueMicrotask(() => document.querySelector<HTMLInputElement>('.search-input')?.focus());
      }
      if (event.key === 'Escape') { composerOpen = false; editingTask = null; moveTaskTarget = null; sectionDialog = null; sectionMenu = null; }
    };
    window.addEventListener('keydown', keyHandler);
    return () => window.removeEventListener('keydown', keyHandler);
  });

  async function initialize() {
    try {
      user = await api.me();
      await loadSections();
      const wanted = new URL(location.href).searchParams.get('section');
      const initial = leafSections.find((section) => section.id === wanted) ?? leafSections[0] ?? allSections[0];
      if (initial) await selectSection(initial);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) await goto('/login');
      else notify('Не удалось загрузить данные');
    } finally { loading = false; }
  }

  async function loadSections() { sectionsTree = await api.sections(); }

  async function selectSection(section: Section) {
    selected = section;
    view = 'section';
    sidebarOpen = false;
    composerOpen = false;
    const loaded = await api.section(section.id);
    tasks = loaded.tasks;
    const url = new URL(location.href);
    url.searchParams.set('section', section.id);
    history.replaceState({}, '', url);
  }

  async function refreshSection() {
    if (!selected) return;
    const loaded = await api.section(selected.id);
    tasks = loaded.tasks;
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
      if (editingTask) {
        await api.updateTask(editingTask.id, draft);
        if (editingTask.section_id !== sectionId) await api.moveTask(editingTask.id, sectionId, 0, editingTask.parent_task_id);
      } else {
        await api.createTask(sectionId || selected!.id, draft);
      }
      composerOpen = false;
      editingTask = null;
      if (selected?.id === sectionId || !sectionId) await refreshSection();
      notify('Задача сохранена');
    });
  }

  async function toggleTask(task: Task) { await safe(async () => { await api.toggleTask(task.id); await refreshCurrent(); }); }
  async function archiveTask(task: Task) { await safe(async () => { await api.archiveTask(task.id); await refreshCurrent(); notify('Задача перемещена в архив'); }); }
  async function deleteTask(task: Task) {
    if (!confirm(`Удалить задачу «${task.title}»?`)) return;
    await safe(async () => { await api.deleteTask(task.id); await refreshCurrent(); });
  }
  async function refreshCurrent() {
    if (view === 'section') await refreshSection();
    else if (view === 'archived') tasks = (await api.archived()).tasks;
    else if (view === 'search') searchResults = query ? await api.search(query) : [];
    else await changeView('calendar');
  }

  function editTask(task: Task) { editingTask = task; composerOpen = true; }

  async function moveTask(sectionId: string) {
    if (!moveTaskTarget) return;
    await safe(async () => {
      await api.moveTask(moveTaskTarget!.id, sectionId, 0, null);
      moveTaskTarget = null;
      await refreshCurrent();
      notify('Задача перемещена');
    });
  }

  async function dropTask(target: Task, mode: 'before' | 'child') {
    if (!draggedTask || draggedTask.id === target.id) return;
    const descendants = new Set<string>();
    const collect = (parentId: string) => tasks.filter((task) => task.parent_task_id === parentId).forEach((child) => { descendants.add(child.id); collect(child.id); });
    collect(draggedTask.id);
    if (descendants.has(target.id)) { notify('Нельзя перенести задачу внутрь её подзадачи'); return; }
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
      if (mode === 'delete' && selected?.id === section?.id) {
        const fallback = leafSections[0] ?? allSections[0];
        if (fallback) await selectSection(fallback); else { selected = null; tasks = []; }
      }
      notify(mode === 'delete' ? 'Раздел удалён' : 'Раздел сохранён');
    });
  }

  async function logout() { await api.logout(); await goto('/login'); }

  function closeMoveDialogOnBackdrop(event: MouseEvent) {
    if (event.target === event.currentTarget) moveTaskTarget = null;
  }

  function closeSectionDialogOnBackdrop(event: MouseEvent) {
    if (event.target === event.currentTarget) sectionDialog = null;
  }
</script>

<svelte:head><title>{heading} · Planty</title></svelte:head>

{#if loading || !user}
  <div class="loading" aria-label="Загрузка"></div>
{:else}
  <div class="app-shell">
    <div class="mobile-header"><button onclick={() => sidebarOpen = true} aria-label="Открыть меню"><Menu /></button><img src="/logo.png" alt="Planty" /><span></span></div>
    <Sidebar open={sidebarOpen} sections={visibleSections} selectedId={selected?.id ?? null} {user} {view} onClose={() => sidebarOpen = false} onSelectSection={(section) => void selectSection(section)} onView={(next) => void changeView(next)} onNewSection={openNewSection} onSectionMenu={openSectionMenu} onLogout={() => void logout()} />
    <main class="main-content">
      <div class="content-inner">
        <header class="page-heading">
          {#if view !== 'section'}<span class="heading-icon">{view === 'search' ? '🔎' : view === 'calendar' ? '🗓️' : '📦'}</span>{/if}
          <h1>{heading}</h1>
          {#if view === 'section'}<span class="task-count">{tasks.length}</span>{/if}
          <div class="heading-actions">
            {#if view === 'section'}<button onclick={() => { editingTask = null; composerOpen = true; }} aria-label="Добавить задачу"><Plus /></button>{/if}
            <button aria-label="Ещё"><Ellipsis /></button>
          </div>
        </header>

        {#if view === 'section'}
          {#if composerOpen && selected}
            <TaskComposer task={editingTask} section={editingTask?.section_id ?? selected.id} sections={leafSections} onSave={saveTask} onCancel={() => { composerOpen = false; editingTask = null; }} />
          {/if}
          <div class="task-list" role="list">
            <TaskTree {tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={(task) => moveTaskTarget = task} onDragStart={(task) => draggedTask = task} onDropTask={(task, mode) => void dropTask(task, mode)} />
          </div>
          {#if selected && !composerOpen}<button class="add-task-button" onclick={() => { editingTask = null; composerOpen = true; }}><Plus />Добавить задачу <kbd>Q</kbd></button>{/if}
          {#if !selected}<div class="empty-state"><div class="empty-icon">🌱</div>Создайте раздел, чтобы добавить первую задачу.</div>{/if}
        {:else if view === 'search'}
          <div class="search-wrap"><Search /><input class="search-input" bind:value={query} oninput={search} placeholder="Поиск по задачам" aria-label="Поиск по задачам" /></div>
          {#if query && searchResults.length === 0}<div class="empty-state">Ничего не найдено</div>{/if}
          <div class="task-list" role="list"><TaskTree tasks={searchResults} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={(task) => moveTaskTarget = task} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} /></div>
        {:else if view === 'calendar'}
          {#if overdueTasks.length}<section class="calendar-group overdue-group"><h2>Просрочено</h2><TaskTree tasks={overdueTasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={(task) => moveTaskTarget = task} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} /></section>{/if}
          {#each calendarGroups as group}<section class="calendar-group"><h2>{new Date(`${group.date}T12:00:00`).toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}</h2><TaskTree tasks={group.tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={(task) => moveTaskTarget = task} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} /></section>{/each}
          {#if !overdueTasks.length && !calendarGroups.length}<div class="empty-state"><div class="empty-icon">☀️</div>На ближайший месяц задач нет.</div>{/if}
        {:else}
          <div class="task-list" role="list"><TaskTree {tasks} onToggle={(task) => void toggleTask(task)} onEdit={editTask} onArchive={(task) => void archiveTask(task)} onDelete={(task) => void deleteTask(task)} onMove={(task) => moveTaskTarget = task} onDragStart={(task) => draggedTask = task} onDropTask={() => {}} /></div>
          {#if !tasks.length}<div class="empty-state"><ArchiveRestore size={40} /><p>Архив пуст</p></div>{/if}
        {/if}
      </div>
    </main>
  </div>
{/if}

{#if moveTaskTarget}
  <div class="dialog-shield" role="presentation" onclick={closeMoveDialogOnBackdrop}><div class="dialog" role="dialog" aria-modal="true" tabindex="-1"><h2>Переместить задачу</h2><label>Новый раздел<select bind:value={dialogParent}>{#each leafSections as section}<option value={section.id}>{section.title}</option>{/each}</select></label><div class="dialog-actions"><button onclick={() => moveTaskTarget = null}>Отмена</button><button class="primary" onclick={() => void moveTask(dialogParent || leafSections[0]?.id)}>Переместить</button></div></div></div>
{/if}

{#if sectionMenu}
  <button class="menu-shield" onclick={() => sectionMenu = null} aria-label="Закрыть меню"></button>
  <div class="context-menu section-menu" role="menu" style={`left:${Math.min(sectionMenu.x, innerWidth - 230)}px;top:${Math.min(sectionMenu.y, innerHeight - 150)}px`}><button role="menuitem" onclick={() => startSectionAction('rename')}><Pencil size={17} />Переименовать</button><button role="menuitem" onclick={() => startSectionAction('move')}><Menu size={17} />Переместить</button><button role="menuitem" class="danger" onclick={() => startSectionAction('delete')}><Trash2 size={17} />Удалить</button></div>
{/if}

{#if sectionDialog}
  <div class="dialog-shield" role="presentation" onclick={closeSectionDialogOnBackdrop}><form class="dialog" onsubmit={(event) => { event.preventDefault(); void submitSectionDialog(); }}><h2>{sectionDialog.mode === 'new' ? 'Новый раздел' : sectionDialog.mode === 'rename' ? 'Переименовать раздел' : sectionDialog.mode === 'move' ? 'Переместить раздел' : 'Удалить раздел?'}</h2>{#if sectionDialog.mode === 'new' || sectionDialog.mode === 'rename'}<label>Название<input bind:value={dialogTitle} required /></label>{/if}{#if sectionDialog.mode === 'new' || sectionDialog.mode === 'move'}<label>Родительский раздел<select bind:value={dialogParent}><option value={root?.id ?? ''}>Верхний уровень</option>{#each allSections.filter((candidate) => candidate.id !== sectionDialog?.section?.id) as section}<option value={section.id}>{section.title}</option>{/each}</select></label>{/if}{#if sectionDialog.mode === 'delete'}<p>Можно удалить только пустой раздел без подразделов. Это действие нельзя отменить.</p>{/if}<div class="dialog-actions"><button type="button" onclick={() => sectionDialog = null}>Отмена</button><button class:danger={sectionDialog.mode === 'delete'} class:primary={sectionDialog.mode !== 'delete'}>{sectionDialog.mode === 'delete' ? 'Удалить' : 'Сохранить'}</button></div></form></div>
{/if}

{#if toast}<div class="toast" role="status">{toast}</div>{/if}
