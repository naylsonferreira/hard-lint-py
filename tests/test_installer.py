import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from hard_lint_py.installer import HardLintInstaller


def test_installer_requires_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        installer = HardLintInstaller(Path(tmpdir))
        with pytest.raises(RuntimeError, match="Not a Git repository"):
            installer.install()


def test_installer_requires_pyproject():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()

        installer = HardLintInstaller(project_dir)
        with pytest.raises(RuntimeError, match="pyproject.toml not found"):
            installer.install()


def test_git_repo_check():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        assert not installer._check_git_repo()

        (project_dir / ".git").mkdir()
        assert installer._check_git_repo()


def test_pyproject_check():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        assert not installer._check_pyproject()

        (project_dir / "pyproject.toml").write_text("[tool.poetry]\n")
        assert installer._check_pyproject()


def test_setup_pre_commit_hooks():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        installer._setup_pre_commit_hooks()

        assert (project_dir / ".hardlint").exists()

        pre_commit_hook = project_dir / ".hardlint" / "_" / "pre-commit"
        commit_msg_hook = project_dir / ".hardlint" / "_" / "commit-msg"

        assert pre_commit_hook.exists()
        assert commit_msg_hook.exists()

        pre_commit_content = pre_commit_hook.read_text()
        assert "poetry run hard-lint-py format" in pre_commit_content

        commit_msg_content = commit_msg_hook.read_text()
        assert "feat" in commit_msg_content or "fix" in commit_msg_content


def test_configure_git_hooks_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()

        installer = HardLintInstaller(project_dir)

        with patch("subprocess.run") as mock_run:
            installer._configure_git_hooks_path()

            mock_run.assert_called_once()
            call_args = mock_run.call_args

            assert call_args[0][0] == [
                "git",
                "config",
                "core.hooksPath",
                ".hardlint/_",
            ]


def test_configure_git_hooks_path_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        installer = HardLintInstaller(project_dir)

        def raise_error(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "git", stderr=b"error message")

        with patch("subprocess.run", side_effect=raise_error):
            with pytest.raises(RuntimeError, match="Failed to configure Git"):
                installer._configure_git_hooks_path()


def test_ensure_pyproject_config():
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
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        pyproject_content = (
            "[tool.poetry]\n[tool.ruff]\nline-length = 120\n[tool.black]\n[tool.isort]\n"
        )
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        installer = HardLintInstaller(project_dir)
        installer._ensure_pyproject_config()

        content = pyproject_path.read_text()
        assert "line-length = 120" in content


def test_full_installation():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".git").mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.poetry]\n")

        installer = HardLintInstaller(project_dir)

        with patch("subprocess.run"):
            installer.install()

        assert (project_dir / ".hardlint" / "_" / "pre-commit").exists()
        assert (project_dir / ".hardlint" / "_" / "commit-msg").exists()
