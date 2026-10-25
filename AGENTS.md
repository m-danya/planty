# Planty agent notes

- Backend layering is DDD-style: keep invariants and state transitions in `planty/domain`, orchestration and DTOs in `planty/application`, and SQLAlchemy persistence in `planty/infrastructure`. Routers only handle HTTP/auth/UoW boundaries; services coordinate repositories; repositories map entities to storage models.
- Domain entities must always be valid. Change aggregate state through domain methods, preserve section/task ordering and ownership checks, and update both persistence mappings and migrations when adding stored fields.
- Run backend checks from the repository root: `uv run ruff check planty`, `uv run mypy planty`, `uv run pytest`.
- Run frontend checks from `frontend`: `npm run check`, `npm run test`, `npm run test:e2e`, `npm run build`.
- For browser verification, start the backend and frontend preview, then use `playwright-cli open http://127.0.0.1:4173` and exercise login, keyboard shortcuts, task parsing/editing, sections, search, and drag-and-drop.
