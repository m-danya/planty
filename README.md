<p align="center">
    <img src="./imgs/logo_vert.png" height="200px">
</p>

> "I have <i>plenty</i> things to do!"

Planty is an open-source task management app inspired by Todoist and GTD system.

This project is being **actively developed** and is not yet a fully working product.

Here is a quick demo (last updated: December 12, 2024):

https://github.com/user-attachments/assets/6e2622b6-cec3-46f8-bd35-dc2c760b33b0

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
# during initial development. To get db with sample data from tests, uncomment a
# line in `config.py` to avoid using in-memory db for tests and run this:
pytest; mv planty_test.db planty.db

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

Use [nvm](https://github.com/nvm-sh/nvm) to manage nodejs versions:

```
nvm install --lts 20
nvm use --lts 20
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

### Generate types for frontend from openapi.json

1. Start backend, save 127.0.0.1:8000/openapi.json to `frontend` directory (TODO: automate)
2. Run this:

```
cd frontend
npx swagger-typescript-api -p ./openapi.json -o ./api --axios
```
