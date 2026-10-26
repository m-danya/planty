# Frontend Test Plan

## Application Overview

Planty is a static SvelteKit task manager. The browser suite runs against the
production preview while intercepting every `/api` request with an in-memory,
stateful API. Tests use a fixed clock and deterministic IDs, so they require no
backend, database, network access, or pre-existing user data.

## Test Scenarios

### 1. Authentication

**Seed:** `tests/fixtures.ts`

#### 1.1. authentication-flow

**File:** `tests/authentication-flow.spec.ts`

**Steps:**
  1. Open the login page as a logged-out user and submit rejected credentials.
    - expect: a localized credentials error remains on the login page
  2. Switch to registration and submit valid credentials.
    - expect: registration and form-encoded login requests are sent
    - expect: the user reaches the task application
  3. Log out, then revisit login while authenticated.
    - expect: logout returns to login and authenticated users are redirected home

### 2. Startup and Navigation

**Seed:** `tests/fixtures.ts`

#### 2.1. startup-routing-and-failures

**File:** `tests/startup-routing-and-failures.spec.ts`

**Steps:**
  1. Open a URL selecting a nested section.
    - expect: that section and its tasks load and the query parameter is retained
  2. Reload with a one-shot sections failure.
    - expect: the initialization error is shown without an unhandled exception

#### 2.2. keyboard-and-mobile-navigation

**File:** `tests/keyboard-and-mobile-navigation.spec.ts`

**Steps:**
  1. Exercise Q, Russian Й, F, and Escape shortcuts.
    - expect: composers and search open only outside editable controls
  2. Resize to mobile and open and close the sidebar.
    - expect: the responsive sidebar follows its open state

### 3. Tasks

**Seed:** `tests/fixtures.ts`

#### 3.1. task-composer-and-editing

**File:** `tests/task-composer-and-editing.spec.ts`

**Steps:**
  1. Edit a nested task and press Shift+Enter.
    - expect: the edit is saved and a new composer opens after the task subtree
    - expect: the next task is created with the same parent and sibling position
  2. Create a task containing a flexible recurring natural-language date and time.
    - expect: the phrase is highlighted, `каждые!` maps to flexible recurrence,
      and the create payload contains the parsed due time
    - expect: clicking the date chip explains the due date, editable time,
      recurrence, source phrase, and completion-based schedule
  3. Alt-click the task and edit it in place.
    - expect: the composer replaces the task row instead of appearing above the list
    - expect: the stored recurrence and completion-based mode remain inspectable,
      and editing the time updates the task payload
  4. Type a `#section` prefix and choose the suggested destination by keyboard.
    - expect: the token is removed from the title and update/move payloads are correct

#### 3.2. task-lifecycle

**File:** `tests/task-lifecycle.spec.ts`

**Steps:**
  1. Complete, archive, restore, and delete tasks through visible controls.
    - expect: completion auto-archives by default, but the local setting can disable it
    - expect: every refreshed view reflects the mock server state
    - expect: cancelling deletion leaves the task intact

#### 3.3. task-move-dialog

**File:** `tests/task-move-dialog.spec.ts`

**Steps:**
  1. Open a task context menu and move the task to a different section.
    - expect: the task disappears from the source and appears in the destination

#### 3.4. task-drag-and-drop

**File:** `tests/task-drag-and-drop.spec.ts`

**Steps:**
  1. Drop one task onto another and try to create a cycle.
    - expect: the first task becomes an indented child
    - expect: the cyclic move is rejected before an API call
  2. Create another subtask through the parent's context menu.
    - expect: the action is available even before the parent has any subtasks
    - expect: the composer opens without a section selector
    - expect: the create request carries the parent task id
  3. Drop at the top edge of a row.
    - expect: the task becomes a sibling with a null parent

#### 3.5. task-presentation

**File:** `tests/task-presentation.spec.ts`

**Steps:**
  1. Render overdue, today, tomorrow, future, recurring, completed, child, and
     orphan tasks.
    - expect: labels, classes, hierarchy, and accessible actions are correct
    - expect: tomorrow is brown and nearby weekdays are named and purple
    - expect: due time uses the same neutral color regardless of the date color
  2. Collapse the parent task with its chevron and expand it again.
    - expect: child rows hide and reappear and aria-expanded follows the state

#### 3.6. task-errors

**File:** `tests/task-errors.spec.ts`

**Steps:**
  1. Fail task creation and completion requests once.
    - expect: API details appear as toasts and local UI state is not corrupted

#### 3.7. task-scheduling-menu

**File:** `tests/task-scheduling-menu.spec.ts`

**Steps:**
  1. Open a task context menu and schedule it for today and tomorrow.
    - expect: the shortcuts use the same date colors as task rows
    - expect: each shortcut updates the task due date and refreshed label
  2. Open the other-day calendar and choose an arbitrary date.
    - expect: the styled calendar supports month navigation and selection
    - expect: the selected local date is sent and rendered on the task

### 4. Sections

**Seed:** `tests/fixtures.ts`

#### 4.1. section-lifecycle

**File:** `tests/section-lifecycle.spec.ts`

**Steps:**
  1. Reorder a top-level section by drag-and-drop.
    - expect: the move request has the correct parent/index and the tree refreshes
  2. Create, rename, move, collapse, expand, and delete an empty section.
    - expect: each operation updates the sidebar after a server refresh
    - expect: deleting the selected section chooses a valid fallback

#### 4.2. section-aggregate-views

**File:** `tests/section-aggregate-views.spec.ts`

**Steps:**
  1. Open a parent section containing both direct and deeply nested leaf sections.
    - expect: every descendant leaf is grouped under its own heading and all tasks are visible
    - expect: task counts appear only while hovering the current section or a subsection title
    - expect: Alt-click editing replaces the task in its own group
  2. Switch the parent section to board mode and create a task in one column.
    - expect: columns reuse the task card component and creation targets that leaf section
    - expect: the layout is saved for this section in `localStorage` and survives reload
  3. Save opposite layouts for two parent sections and move between them.
    - expect: each section restores its own layout before and after reload

#### 4.3. section-sidebar-expansion

**File:** `tests/section-sidebar-expansion.spec.ts`

**Steps:**
  1. Collapse a nested section and its parent, then reload the page.
    - expect: both sections remain collapsed through `localStorage`
  2. Expand only the parent and then expand the nested section.
    - expect: each section restores its own expansion state independently
    - expect: the expanded states also survive reload

### 5. Special Views

**Seed:** `tests/fixtures.ts`

#### 5.1. search-calendar-and-archive

**File:** `tests/search-calendar-and-archive.spec.ts`

**Steps:**
  1. Search titles and descriptions, including an empty result.
    - expect: debounced results match the query and encoded request
    - expect: Alt-click opens the shared inline editor in the search result
  2. Open calendar and archive views.
    - expect: overdue and dated groups and archived tasks are rendered
    - expect: Alt-click edits a calendar task in place and also opens inline editing in the archive

#### 5.2. empty-states

**File:** `tests/empty-states.spec.ts`

**Steps:**
  1. Start without user sections or dated and archived tasks.
    - expect: section, search, calendar, and archive empty states are visible

### 6. Date Parser

**Seed:** `tests/date-parser.test.ts`

#### 6.1. parser-branches

**File:** `tests/date-parser.test.ts`

**Steps:**
  1. Parse Russian and English absolute, relative, weekday, and recurring dates.
    - expect: every supported parser branch returns a local ISO date
  2. Format every recurrence unit in singular and plural form.
    - expect: stable localized labels are returned
  3. Parse completion-based `каждый!`, year rollover, invalid dates, and business days.
    - expect: flexible mode and calendar calculations are normalized correctly
  4. Parse word-based intervals, quarter recurrences, start dates, weekday
     abbreviations, and localized labels.
    - expect: common Todoist-style Russian forms map to backend recurrence fields
  5. Parse 24-hour and 12-hour times with dates, weekdays, recurrences, and
     without an explicit date.
    - expect: Todoist-style time phrases produce a local date plus `HH:MM`, and
      a time without a date uses today or tomorrow depending on whether it passed

### 7. Localization

#### 7.1. localization-and-settings

**File:** `tests/localization-and-settings.spec.ts`

**Steps:**
  1. Open the application without a stored preference.
    - expect: navigation and system section names are fully Russian
    - expect: the sidebar does not show section task counts
    - expect: auto-archive is enabled by default and can be disabled in `localStorage`
  2. Change the profile language to English.
    - expect: the visible shell updates immediately
  3. Reload the page.
    - expect: the language and auto-archive preferences remain selected through `localStorage`

#### 7.2. todoist-import

**File:** `tests/todoist-import.spec.ts`

**Steps:**
  1. Open profile settings, select a Todoist ZIP, disable data erasure, and import.
    - expect: imported sections appear next to the existing sections
    - expect: the multipart request sends the disabled erase flag
  2. Import again with data erasure enabled.
    - expect: existing sections are replaced by imported sections
    - expect: the result toast reports imported project and task counts
