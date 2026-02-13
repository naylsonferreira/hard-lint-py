"""Tests for hard-lint-py installation."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

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


def test_setup_pre_commit_hooks():
    """Test pre-commit hooks are created correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        installer._setup_pre_commit_hooks()

        # Verify .hardlint directory created
        assert (project_dir / ".hardlint").exists()

        # Verify hooks exist
        pre_commit_hook = project_dir / ".hardlint" / "_" / "pre-commit"
        commit_msg_hook = project_dir / ".hardlint" / "_" / "commit-msg"

        assert pre_commit_hook.exists()
        assert commit_msg_hook.exists()

        # Verify correct content
        pre_commit_content = pre_commit_hook.read_text()
        assert "poetry run ruff check" in pre_commit_content
        assert "poetry run black" in pre_commit_content
        assert "poetry run isort" in pre_commit_content

        # Verify commit-msg content
        commit_msg_content = commit_msg_hook.read_text()
        assert "feat" in commit_msg_content or "fix" in commit_msg_content


def test_configure_git_hooks_path():
    """Test git config core.hooksPath is set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()

        installer = HardLintInstaller(project_dir)

        # Mock subprocess.run
        with patch("subprocess.run") as mock_run:
            installer._configure_git_hooks_path()

            # Verify git config was called with correct parameters
            mock_run.assert_called_once()
            call_args = mock_run.call_args

            assert call_args[0][0] == [
                "git",
                "config",
                "core.hooksPath",
                ".hardlint/_",
            ]


def test_configure_git_hooks_path_error():
    """Test error handling in git config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        # Mock subprocess.run to raise an error
        def raise_error(*args, **kwargs):
            raise subprocess.CalledProcessError(
                1, "git", stderr=b"error message"
            )

        with patch("subprocess.run", side_effect=raise_error):
            with pytest.raises(RuntimeError, match="Failed to configure Git"):
                installer._configure_git_hooks_path()


def test_ensure_pyproject_config():
    """Test pyproject.toml is configured correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[tool.poetry]\nname = 'test'\n")

        installer = HardLintInstaller(project_dir)
        installer._ensure_pyproject_config()

        content = pyproject_path.read_text()
        assert "[tool.ruff]" in content
        assert "[tool.black]" in content
        assert "[tool.isort]" in content
        assert "line-length = 100" in content


def test_ensure_pyproject_config_already_configured():
    """Test pyproject.toml that already has tool configs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        pyproject_content = (
            "[tool.poetry]\n"
            "[tool.ruff]\n"
            "line-length = 120\n"
            "[tool.black]\n"
            "[tool.isort]\n"
        )
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        installer = HardLintInstaller(project_dir)
        installer._ensure_pyproject_config()

        content = pyproject_path.read_text()
        # Existing config should be preserved
        assert "line-length = 120" in content


def test_full_installation():
    """Test full installation flow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.poetry]\n")

        installer = HardLintInstaller(project_dir)

        # Mock subprocess.run for git config
        with patch("subprocess.run"):
            installer.install()

        # Verify results
        assert (project_dir / ".hardlint" / "_" / "pre-commit").exists()
        assert (project_dir / ".hardlint" / "_" / "commit-msg").exists()
