default: clean sync configure format lint check test

sync-spec:
	@echo "Syncing configuration with global spec..."
	@nitpick fix > /dev/null || true
	@echo "...done."

sync: sync-spec
	@printf "\e[1mSync complete!\e[0m\n\n"

configure-spec:
	@echo "Checking configuration against global spec..."
	@nitpick check
	@printf "\e[1mConfiguration is in sync!\e[0m\n\n"

configure: configure-spec

format:
	@echo "Formatting Python docstrings..."
	@docformatter . -r --in-place --exclude .venv .git || true
	@echo "...done."
	@echo "Formatting Python files..."
	@echo "  1. Ruff Format"
	@ruff format . > /dev/null
	@echo "  2. Ruff Check (fix only)"
	@ruff check --fix-only . --quiet
	@echo "  3. Add trailing commas"
	@find . -path ./.venv -prune -o -name '*.py' -print0 | xargs -P 16 -0 -I{} sh -c 'add-trailing-comma "{}" || true'
	@echo "  4. Ruff Format (again)"
	@ruff format . --quiet
	@echo "  5. Ruff Check (fix only, again)"
	@ruff check --fix-only . --quiet
	@echo "...done."

lint:
	@echo "Checking for Python formatting issues which can be fixed automatically..."
	@echo "  1. Ruff Format"
	@ruff format . --diff > /dev/null 2>&1 || (printf 'Found files which need to be auto-formatted. Make sure your dependencies are up to date and then run \e[1mmake format\e[0m and re-lint.\n'; exit 1)
	@echo "  2. Ruff Check (fix only)"
	@ruff check . --diff --silent || (printf 'Found files which need to be auto-formatted. Make sure your dependencies are up to date and then run \e[1mmake format\e[0m and re-lint.\n'; exit 1)
	@echo "...done. No issues found."
	@echo "Running Python linter..."
	@echo "  1. Ruff Check"
	@ruff check . --quiet
	@echo "  2. Flake8"
	@flake8 .
	@echo "...done. No issues found."

check: check-py

check-py:
	@echo "Running Python type checks..."
	@ty check .
	@echo "...done. No issues found."

test:
	@find . -name "*.pyc" -delete
	@coverage erase
	@coverage run --source=data_enum -m pytest --ignore=.venv --ignore=dist --ignore=prof --ignore=build -vv
	@coverage report -m --fail-under 90

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info
	@echo "...done."

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install uv
	.venv/bin/uv pip install -r requirements/develop.txt
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

teardown:
	rm -rf .venv

.PHONY: default sync sync-spec configure configure-spec format lint check check-py test clean setup teardown
