ruff format && \
ruff check --fix && \
mypy planty && \
pytest -x && \
echo "All right, ready to commit!"
