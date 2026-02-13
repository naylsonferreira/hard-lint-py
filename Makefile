.PHONY: help install test lint format build publish clean dev verify

help:
	@echo "Hard-Lint Python - Available Commands:"
	@echo ""
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make test          - Run tests with pytest"
	@echo "  make lint          - Run linting with ruff"
	@echo "  make format        - Format code with black and isort"
	@echo "  make fix           - Fix linting errors automatically"
	@echo "  make build         - Build distribution packages"
	@echo "  make publish       - Publish to PyPI (requires auth)"
	@echo "  make clean         - Remove build artifacts and caches"
	@echo "  make dev           - Install in development mode"
	@echo "  make verify        - Verify installation works"
	@echo ""

install:
	poetry install

dev:
	poetry install --with dev

test:
	poetry run pytest -v tests/

lint:
	poetry run ruff check src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

fix:
	poetry run ruff check src/ tests/ --fix
	poetry run black src/ tests/
	poetry run isort src/ tests/

build: clean
	poetry build

publish: build
	poetry publish

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

verify:
	poetry run python -c "from hard_lint_py import main; print('✓ Hard-Lint-Py imported successfully')"
	poetry run python -c "from hard_lint_py.cli import main; print('✓ CLI module available')"
