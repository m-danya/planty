<p align="center">
    <img src="./imgs/logo_vert.png" height="200px">
</p>

> "I have <i>plenty</i> things to do!"

Planty is an open-source task management app inspired by Todoist and GTD system.

This project is being **actively developed** and is not yet a fully working product.


## Run locally with development data

Prerequisites:

- Git and OpenSSL
- [uv](https://docs.astral.sh/uv/)
- Node.js 20 and npm
- tmux

Run the following commands from top to bottom:

```bash
git clone https://github.com/m-danya/planty
cd planty

cp .env.dev.sample .env.dev
printf '\nPLANTY_AUTH_SECRET=%s\n' "$(openssl rand -base64 32)" >> .env.dev

uv sync
npm --prefix frontend ci

# This intentionally resets the local SQLite database.
rm -f planty.db
uv run alembic upgrade head
uv run python -m planty.scripts.seed_dev

./run-dev.sh
```

Open `http://127.0.0.1:5173` and log in with:

- Email: `user@example.ru`
- Password: `user@example.ru`

The seed command creates two verified users, fourteen sections, and eighteen
tasks. It only runs in `DEV` mode and refuses to modify a non-empty database.
The `rm -f planty.db` command deletes all existing local data; it is part of the
initial/reset procedure, not a command for normal restarts.

`run-dev.sh` opens the backend and frontend in separate windows of the
`planty-dev` tmux session. Detach with `Ctrl-b d`; run `./run-dev.sh` again to
reconnect. It applies pending migrations before starting, so on subsequent
starts only `./run-dev.sh` is needed.

To start the processes without tmux, use two terminals:

```bash
# Terminal 1, from the repository root
uv run uvicorn planty.main:app --reload

# Terminal 2
npm --prefix frontend run dev
```

Vite serves the application on `http://127.0.0.1:5173` and proxies `/api`
requests to the backend on `http://127.0.0.1:8000`.

### Create an empty local database

To work without the bundled development data, reset the database, apply the
schema, and create a verified administrator interactively:

```bash
rm -f planty.db
uv run alembic upgrade head
uv run python -m planty.scripts.create_admin
```

## Run with Docker

The Docker setup uses SQLite and production mode. It does not load development
data automatically.

Prerequisite: Docker with the Compose plugin.

```bash
git clone https://github.com/m-danya/planty
cd planty

cp .env.sample .env
printf '\nPLANTY_AUTH_SECRET=%s\n' "$(openssl rand -base64 32)" >> .env

# The bind mount must be a file before Docker starts.
touch planty.db
docker compose build
docker compose run --rm backend uv run --no-sync alembic upgrade head
docker compose run --rm backend uv run --no-sync python -m planty.scripts.create_admin
docker compose up -d
```

Open `http://localhost`. Stop the stack with `docker compose down`.

## Development notes

The production frontend is a static SvelteKit build. `npm run build` writes it
to `frontend/build`; the frontend Docker image serves those files with Caddy
and does not run Node.js.

Use [nvm](https://github.com/nvm-sh/nvm) to install the expected Node.js
version:

```bash
nvm install 20
nvm use 20
```

### Run tests and type checking

```bash
uv run pytest
uv run mypy planty
```

Measuring code coverage:

```bash
uv run coverage run -m pytest
uv run coverage report # or "uv run coverage html"
```

### Run linting & formatting

(or just use Ruff extension for VS Code)

```bash
uv run ruff check --extend-select I --fix
uv run ruff format
```

### Generate types for frontend from openapi.json

The Svelte frontend keeps its small typed API wrapper in `frontend/src/lib/api.ts`.

### History of the project

Planty started in 2024 as a pet project developed without coding agents: a
self-hosted, open-source task manager inspired by Todoist and GTD. The original
goals were to put Domain-Driven Design into practice and to build an alternative
to Todoist's task limits.

Later that year, as the backend became more complete, I used ChatGPT to help me
try building the frontend in Next.js. Coding agents had not become widespread
yet, so I used ChatGPT and copied the frontend code manually.

Now, in 2026, after coding agents had advanced significantly, I decided to
rebuild the frontend from scratch with their help, this time using SvelteKit.

Here is a demo of the original Next.js frontend from December 12, 2024, kept as
a snapshot of the project's history:

https://github.com/user-attachments/assets/6e2622b6-cec3-46f8-bd35-dc2c760b33b0

<!-- TODO: Record and add an up-to-date demo of the SvelteKit frontend. -->
