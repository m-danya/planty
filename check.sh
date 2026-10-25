ruff format && \
ruff check --fix && \
mypy planty && \
pytest -x && \
cd frontend && \
    npm run check && \
    npm run test && \
    npm run build && \
echo "All right, ready to commit!"
