# Hard-Lint for Python 🐍

Rigorous linting and code quality setup for Python projects with automatic pre-commit hooks.

## Features

- **Automated Pre-commit Hooks**: Validates code before every commit
  - `pre-commit`: Runs `ruff`, `black`, and `isort`
  - `commit-msg`: Validates messages follow Conventional Commits format
- **Strict Linting**: Ruff checks for errors, complexity, and code quality
- **Synchronized Formatters**: Ruff, Black, and isort configured with same profile (no conflicts)
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
  - Validates no comments exist
  - Enforces empty `__init__.py` files

- **commit-msg**: Validates commit messages
  - Must follow Conventional Commits format
  - Examples: `feat:`, `fix:`, `chore:`, `docs:`, etc.

## Linting Rules

### Custom Rules

| Rule | Description |
|------|-------------|
| **no-comments** | Forbids inline comments and docstrings in all Python files |
| **empty-init** | `__init__.py` files must be completely empty (no imports, no code) |

### Ruff Rules Enforced

| Rule | Category | Description |
|------|----------|-----------|
| E | pycodestyle errors | PEP 8 compliance |
| F | Pyflakes | Unused imports, undefined names |
| W | pycodestyle warnings | Code warnings |
| I | isort | Import sorting |
| N | pep8-naming | Naming conventions |
| C | mccabe | Code complexity |
| B | flake8-bugbear | Common bugs and design problems |
| RUF | Ruff-specific | Additional quality checks |
| UP | pyupgrade | Modernize Python syntax |

### Synchronized Formatter Configuration

All three formatters (Ruff, Black, isort) use the **same profile** to prevent conflicts:

| Aspect | Configuration | Notes |
|--------|---------------|-------|
| **Line Length** | 100 characters | Consistent across all tools |
| **Python Version** | 3.14+ | Targets modern Python |
| **Imports Profile** | `isort: black` | Compatible with Black |
| **Trailing Commas** | Enabled | Multi-line consistency |

### Configuration

Auto-configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ["py314"]

[tool.isort]
profile = "black"           # Compatible with Black
line_length = 100
known_first_party = ["hard_lint_py"]

[tool.ruff]
line-length = 100
target-version = "py314"
select = ["E", "F", "W", "I", "N", "C", "B", "RUF", "UP"]
```

## Usage

### Normal workflow

```bash
# Make changes
cat > new_file.py << 'EOF'
def greet(name):
    # Greet a person by name
    return f"Hello, {name}!"
EOF

# Stage changes
git add new_file.py

# Commit (hooks will run automatically)
git commit -m "feat: add greeting function"
```

### Pre-commit Hook Behavior

When you commit, the hook automatically:
1. **Ruff**: Checks for linting issues, imports, and code quality
2. **Black**: Formats code to 100-character lines
3. **isort**: Sorts and organizes imports
4. Blocks commit if any issues can't be auto-fixed

If pre-commit fails:
```bash
# Fix will be auto-applied, just re-add and commit
git add .
git commit -m "feat: your message"
```

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

**Formatters conflicting with each other?**
- They shouldn't! Ruff, Black, and isort are configured with the same profile
- If you see conflicts, run all three: `ruff check --fix`, `black .`, `isort .`

**Line length conflicts?**
- All tools configured to 100 characters
- Black and isort won't fight over formatting
- Ruff respects Black's decisions (E501 ignored)

## Supported Python Versions

- Python 3.14+

## Development

When developing with hard-lint-py:

### Pre-commit Validation
Your code will be validated on every commit:
```bash
git commit -m "feat: your feature"
# Runs: ruff check --fix → black → isort → commitlint
```

### Manual Validation
Run validation checks manually:
```bash
# All checks
make lint
make format
make test
make test-cov

# Individual tools
poetry run ruff check src/ tests/
poetry run black --check src/ tests/
poetry run isort --check-only src/ tests/
```

### Quality Standards
- ✅ 99% code coverage
- ✅ No unused imports or variables
- ✅ Empty `__init__.py` files
- ✅ Consistent formatting (100 char lines)
- ✅ Code complexity within limits
- ✅ Modern Python syntax
- ✅ No common bugs or design problems

## License

MIT

## Author

Naylson Ferreira
