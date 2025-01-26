(
    ruff format --check || (
        ruff format && \
        echo "Reformatted. You should run this script again." && \
        false
    )
) && \
ruff check --fix && \
mypy planty && \
pytest -x && \
echo "All right, ready to commit!"
