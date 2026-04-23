# CHANGELOG


## v0.4.0 (2026-04-23)

### Continuous Integration

* ci: update workflows to Python 3.14 and add custom rules validation

- Pin all matrix versions to 3.14 (ci, multiplatform, publish)
- Add validate_no_comments and validate_empty_init_files steps to lint job
- Bump actions/setup-python v4→v5, cache v3→v4, upload-artifact v3→v4, codecov v3→v4
- Remove hard-lint-py --help step from multiplatform (not a useful smoke test)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`96f90d6`](https://github.com/naylsonferreira/hard-lint-py/commit/96f90d6dc5290390561e40e3661a992a006171b6))

### Features

* feat: upgrade deps ([`db051a4`](https://github.com/naylsonferreira/hard-lint-py/commit/db051a48e8bb8f95eaa7d5453dd55965a7896114))

* feat: add empty-init rule and bump minimum Python to 3.14

- Add validate_empty_init_files rule enforcing __init__.py must be empty
- Integrate rule into run_lint and run_format pipelines
- Empty src/hard_lint_py/__init__.py to comply with own rule
- Remove version_variable from semantic_release (version_toml only)
- Bump requires-python to >=3.14 and update classifiers/docs

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`c10f4c2`](https://github.com/naylsonferreira/hard-lint-py/commit/c10f4c23b4153231e83f6ac59ed103927106ff0d))

### Fixes

* fix(ci): replace snok/install-poetry with pipx on publish workflow

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`c61687d`](https://github.com/naylsonferreira/hard-lint-py/commit/c61687df30864041b0358c1822beb69ef7e48838))

* fix(ci): replace snok/install-poetry with pipx on multiplatform workflow

snok/install-poetry@v1 fails to register poetry in PATH on Windows
PowerShell. pipx install poetry works reliably on all platforms.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`c90fa11`](https://github.com/naylsonferreira/hard-lint-py/commit/c90fa11d694bbefcc378c455e488d9e3bd7c13dc))

### Unknown

* Merge pull request #6 from naylsonferreira/feature-NF-add-rules

feat: add empty-init rule and bump minimum Python to 3.14 ([`5414acd`](https://github.com/naylsonferreira/hard-lint-py/commit/5414acd49a560ea0712565c91b66250a1d6ab05b))


## v0.3.0 (2026-03-11)

### Features

* feat: respect gitignore patterns in custom validation ([`ec20cf0`](https://github.com/naylsonferreira/hard-lint-py/commit/ec20cf0ec6ff9a48c862ea47c3bf4d0dbb1dcfed))


## v0.2.4 (2026-03-11)

### Fixes

* fix: enforce no-comments rule and add explicit lint command ([`fced019`](https://github.com/naylsonferreira/hard-lint-py/commit/fced019473efe3bbdeae649682f835dec2829408))


## v0.2.3 (2026-03-10)

### Chores

* chore(release): bump version to 0.2.3 ([`4670f3a`](https://github.com/naylsonferreira/hard-lint-py/commit/4670f3abfceb9318795d966025f94ec0442f1d7a))


## v0.1.0 (2026-03-11)

### Features

* feat: add lint config override detection and enforce hooks installation ([`6bb9fb0`](https://github.com/naylsonferreira/hard-lint-py/commit/6bb9fb042451541ca6a27606264397a38db8617b))


## v0.0.1 (2026-03-09)

### Fixes

* fix: correct test expectations for CLI and pre-commit hooks ([`c7c5ad5`](https://github.com/naylsonferreira/hard-lint-py/commit/c7c5ad550ac6af9fb4a0525f86a1c0023e61df34))


## v0.0.0 (2026-03-09)

### Chores

* chore: initial commit - hard-lint-py v0.2.2 ([`9854553`](https://github.com/naylsonferreira/hard-lint-py/commit/98545534c935b6e57d78088c3e8eb450b752e2bf))
