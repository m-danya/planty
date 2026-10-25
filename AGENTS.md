# Planty agent notes

- Backend layering is DDD-style: keep invariants and state transitions in `planty/domain`, orchestration and DTOs in `planty/application`, and SQLAlchemy persistence in `planty/infrastructure`. Routers only handle HTTP/auth/UoW boundaries; services coordinate repositories; repositories map entities to storage models.
- Domain entities must always be valid. Change aggregate state through domain methods, preserve section/task ordering and ownership checks, and update both persistence mappings and migrations when adding stored fields.
- Run backend checks from the repository root: `uv run ruff check planty`, `uv run mypy planty`, `uv run pytest`.
- Run frontend checks from `frontend`: `npm run check`, `npm run test`, `npm run test:e2e`, `npm run build`.
- Before committing, run `./check.sh` from the repository root. It is the
  non-mutating full quality gate: Ruff formatting and lint checks, mypy,
  backend pytest, Svelte checks, Vitest, deterministic Playwright e2e tests,
  and the production frontend build. Install Python and frontend dependencies
  and Playwright Chromium beforehand; the script checks the project but does
  not bootstrap the environment.
- Never commit or push unless the user explicitly asks. Completing a task,
  passing checks, or fixing CI on its own is not authorization to commit or
  push; leave changes in the working tree and report them.
- Write commit messages using the 50/72 rule: keep the imperative subject at
  50 characters or fewer, separate it from the body with a blank line, and
  wrap body lines at 72 characters. Use the body to explain why the change is
  needed and summarize important implementation details.
- For browser verification, use `playwright-cli` from the repository root so it
  automatically reads the ignored local `.playwright/cli.config.json`. That
  config points the global CLI at the Chromium already installed by the
  frontend Playwright package; do not recreate an equivalent config in `/tmp`.
  Start the backend and frontend, then open `http://127.0.0.1:5173` for a
  real-backend smoke check. Exercise login, keyboard shortcuts, task
  parsing/editing, sections, search, and drag-and-drop. Port 4173 is reserved
  for the mocked production-preview e2e suite.

## Frontend tests

- Run commands from `frontend`. Install exact dependencies with `npm ci`; install
  the browser once with `npx playwright install chromium` if it is missing.
- `npm run test` runs deterministic Vitest unit tests, primarily for the
  natural-language date parser. `npm run test:e2e` builds the static SvelteKit
  site, starts its preview on port 4173, and runs every Playwright scenario.
  The e2e suite does not need the Python backend, a database, credentials, or
  network access: `tests/fixtures.ts` intercepts every `/api` request.
- Run one scenario with
  `npm run test:e2e -- tests/task-lifecycle.spec.ts`. Debug it with
  `PLAYWRIGHT_HTML_OPEN=never npm run test:e2e -- tests/task-lifecycle.spec.ts --debug=cli`,
  then attach `playwright-cli` to the session name printed by Playwright.
- Add or update the user-level scenario in `specs/frontend.plan.md` before
  writing a new browser test. Keep one scenario per `*.spec.ts` file and import
  `test` and `expect` from `./fixtures`, never directly from `@playwright/test`.
- Browser tests use a fresh in-memory API state per test, deterministic IDs, a
  single worker, Russian locale, Moscow timezone, and a clock fixed at
  2026-10-25. Change state through `mockApi.state` before `mockApi.open()`;
  simulate a one-shot error with `mockApi.failOnce()`; inspect payloads through
  `mockApi.requests()`. If frontend code adds an endpoint, add its behavior to
  the central mock handler—an unknown `/api` call deliberately returns 501.
- Prefer role, label, and test-id locators. Assert observable UI and request
  payloads. Do not add sleeps, `networkidle`, order-dependent shared state, or
  real backend calls; Playwright assertions already retry until their timeout.
- Keep real-backend browser verification as a separate smoke check. It catches
  proxy, cookie, migration, and serialization integration problems that mocked
  Playwright tests intentionally cannot cover.
