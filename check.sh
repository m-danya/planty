ruff format && \
ruff check --fix && \
mypy planty && \
pytest -x && \
cd frontend && \
npm run build && \
echo "All right, ready to commit!"
