.PHONY: install run check lint types imports test contracts contracts-update trace mirror

install:
	uv sync

run:
	uv run uvicorn library.app:app --reload

# Everything CI runs, in the order a failure is cheapest to read.
check: lint types imports mirror trace test contracts

lint:
	uv run ruff check . && uv run ruff format --check .

types:
	uv run mypy

imports:
	uv run lint-imports

mirror:
	uv run python scripts/check_policy_mirror.py

trace:
	uv run python scripts/check_trace.py

test:
	uv run pytest -q

contracts:
	uv run python scripts/generate_contracts.py --check

contracts-update:
	uv run python scripts/generate_contracts.py
