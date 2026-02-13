"""Tests for hard-lint-py installation."""

import tempfile
from pathlib import Path

import pytest
from hard_lint_py.installer import HardLintInstaller


def test_installer_requires_git_repo():
    """Test that installer fails without a Git repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        installer = HardLintInstaller(Path(tmpdir))
        with pytest.raises(RuntimeError, match="Not a Git repository"):
            installer.install()


def test_installer_requires_pyproject():
    """Test that installer fails without pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()

        installer = HardLintInstaller(project_dir)
        with pytest.raises(RuntimeError, match="pyproject.toml not found"):
            installer.install()


def test_git_repo_check():
    """Test Git repository detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        assert not installer._check_git_repo()

        (project_dir / ".git").mkdir()
        assert installer._check_git_repo()


def test_pyproject_check():
    """Test pyproject.toml detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        assert not installer._check_pyproject()

        (project_dir / "pyproject.toml").write_text("[tool.poetry]\n")
        assert installer._check_pyproject()
