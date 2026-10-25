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
  1. Exercise Q, Russian Й, slash, and Escape shortcuts.
    - expect: composers and search open only outside editable controls
  2. Resize to mobile and open and close the sidebar.
    - expect: the responsive sidebar follows its open state

### 3. Tasks

**Seed:** `tests/fixtures.ts`

#### 3.1. task-composer-and-editing

**File:** `tests/task-composer-and-editing.spec.ts`

**Steps:**
  1. Create a task containing a recurring natural-language date.
    - expect: the phrase is highlighted and the normalized task is rendered
  2. Alt-click the task, edit it, and move it to another section.
    - expect: the due date is preserved and update and move payloads are correct

#### 3.2. task-lifecycle

**File:** `tests/task-lifecycle.spec.ts`

**Steps:**
  1. Complete, archive, restore, and delete tasks through visible controls.
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
  2. Collapse the parent task with its chevron and expand it again.
    - expect: child rows hide and reappear and aria-expanded follows the state

#### 3.6. task-errors

**File:** `tests/task-errors.spec.ts`

**Steps:**
  1. Fail task creation and completion requests once.
    - expect: API details appear as toasts and local UI state is not corrupted

### 4. Sections

**Seed:** `tests/fixtures.ts`

#### 4.1. section-lifecycle

**File:** `tests/section-lifecycle.spec.ts`

**Steps:**
  1. Create, rename, move, collapse, expand, and delete an empty section.
    - expect: each operation updates the sidebar after a server refresh
    - expect: deleting the selected section chooses a valid fallback

### 5. Special Views

**Seed:** `tests/fixtures.ts`

#### 5.1. search-calendar-and-archive

**File:** `tests/search-calendar-and-archive.spec.ts`

**Steps:**
  1. Search titles and descriptions, including an empty result.
    - expect: debounced results match the query and encoded request
  2. Open calendar and archive views.
    - expect: overdue and dated groups and archived tasks are rendered

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
