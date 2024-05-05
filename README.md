# Planty

<p align="center">
    <img src="./imgs/planty.png" height="200px">
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

sudo apt install python3.11 python3.11-venv
python3.11 -m venv venv
source venv/bin/activate
poetry install

# run postgres
docker compose up -d

# (backend is not dockerized yet)
# run "FastAPI" configuration in VS code or:
uvicorn planty.main:app --reload
```
