# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

### Changed

---

## [0.1.0] - 2026-02-13

### Added

- Initial release of hard-lint-py
- `hard-lint-py` CLI command for installation
- Pre-commit hook setup with ruff, black, and isort
- Commit-msg validation with commitlint-like enforcement
- Auto-configuration of `pyproject.toml` with sensible defaults
- Support for Python 3.10+
- Comprehensive README with quick start guide

### Features

- Automated pre-commit hook installation in `.hardlint/` directory
- Git hooks path configuration via `git config core.hooksPath`
- Zero-configuration setup with reasonable defaults
- Multiplattform support (Windows, macOS, Linux)
