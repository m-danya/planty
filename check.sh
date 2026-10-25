uv run ruff format --check && \
uv run ruff check planty && \
uv run mypy planty && \
uv run pytest -x && \
cd frontend && \
    npm run check && \
    npm run test && \
    npm run test:e2e && \
    npm run build && \
echo "All right, ready to commit!"
