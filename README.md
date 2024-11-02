<p align="center">
    <img src="./imgs/logo_vert.png" height="200px">
</p>

> "I have <i>plenty</i> things to do!"

Planty is an open-source task management app inspired by Todoist and GTD system.

(not yet released)

## How to run

Prerequisites: Docker (with compose plugin)

```
git clone https://github.com/m-danya/planty
cd planty
cp .env.sample .env
echo "\nPLANTY_AUTH_SECRET=$(openssl rand -base64 32)" >> .env

sudo apt install python3.11 python3.11-venv
python3.11 -m venv venv
source venv/bin/activate
poetry install

# Run Alembic migrations
# alembic upgrade head

# Alembic migrations are not being maintained yet due to a high pace of changes
# during initial development. To get correct db from tests, run this:
pytest; cp planty_test.db planty.db

# (backend is not dockerized yet)
# run "FastAPI" configuration in VS code or:
uvicorn planty.main:app --reload
```

To start the frontend, run the following commands:

```
cd frontend
npm i
npm run dev
```

### Switching between database engines

By default, the SQLite engine is used for persistence, but you can easily switch
to PostgreSQL: change `DB_TYPE` in `.env` file to `postgresql` and run
the system with `docker compose compose.yaml --profile with-postgres up -d`.

### Run tests and type checking

```
pytest
mypy .
```

Measuring code coverage:

```
coverage run -m pytest
coverage report # or "coverage html"
```

### Run linting & formatting

(or just use Ruff extension for VS Code)

```
ruff check --extend-select I --fix
ruff format
```
