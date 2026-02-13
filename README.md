# Hard-Lint for Python 🐍

Rigorous linting and code quality setup for Python projects with automatic pre-commit hooks.

## Features

- **Automated Pre-commit Hooks**: Validates code before every commit
  - `pre-commit`: Runs `ruff`, `black`, and `isort`
  - `commit-msg`: Validates messages follow Conventional Commits format
- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Multiplattform**: Works on Windows, macOS, and Linux
- **Auto-setup**: Single command to enable all checks

## Installation

```bash
pip install hard-lint-py
# or with poetry
poetry add -D hard-lint-py
```

## Quick Start

```bash
# 1. Install and setup hooks
hard-lint-py

# 2. Make your first commit
git add .
git commit -m "feat: initial setup"
```

That's it! Your project now has:
- **Ruff** for fast Python linting
- **Black** for code formatting
- **isort** for import sorting
- **Commitlint** for commit message validation

## What Gets Installed

### Git Hooks

Hooks are created in `.hardlint/_/`:

- **pre-commit**: Runs before commits to validate code
  - Fixes issues with `ruff check --fix`
  - Formats with `black`
  - Sorts imports with `isort`

- **commit-msg**: Validates commit messages
  - Must follow Conventional Commits format
  - Examples: `feat:`, `fix:`, `chore:`, `docs:`, etc.

### Configuration

Auto-configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"
line_length = 100
```

## Usage

### Normal workflow

```bash
# Make changes
echo "x = 1" > new_file.py

# Stage changes
git add new_file.py

# Commit (hooks will run automatically)
git commit -m "feat: add new feature"
```

### If pre-commit fails

The hook will:
1. Try to fix issues automatically (ruff, black, isort)
2. Show you what needs manual review
3. Block the commit until everything is fixed

### If commit-msg fails

Invalid message example:
```bash
git commit -m "added this feature"  # ❌ Missing type prefix
```

Valid message example:
```bash
git commit -m "feat: added new feature"  # ✅ Has type prefix
```

### Skip hooks (use with caution)

```bash
git commit -m "..." --no-verify
```

## Configuration

All tools read from `pyproject.toml`. Customize as needed:

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "W"]

[tool.black]
line-length = 120

[tool.isort]
profile = "black"
line_length = 120
```

## Troubleshooting

**Hooks not running?**
```bash
# Re-run installation
hard-lint-py
```

**Commit-msg validation failing?**
- Check that your message starts with a type: `feat:`, `fix:`, `chore:`, etc.

**Import sorting conflicts with black?**
- Already configured! isort uses black profile by default.

## Supported Python Versions

- Python 3.10+
- Python 3.11
- Python 3.12

## License

MIT

## Author

Naylson Ferreira
