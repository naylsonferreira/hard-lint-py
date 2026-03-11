"""Tests for hard-lint-py CLI."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from hard_lint_py.cli import (
    find_comments_in_src,
    find_docstrings_in_src,
    main,
    run_check,
    run_format,
)


def test_main_success():
    """Test CLI main function with successful installation."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.return_value = None

            result = main()

            assert result == 0
            mock_installer_class.assert_called_once()
            mock_instance.install.assert_called_once()


def test_main_with_error():
    """Test CLI main function handling errors."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.side_effect = RuntimeError("Test error")

            with patch("sys.stdout"):
                result = main()

            assert result == 1
            mock_instance.install.assert_called_once()


def test_main_with_generic_exception():
    """Test CLI main function with generic exception."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.side_effect = Exception("Unexpected error")

            with patch("sys.stdout"):
                result = main()

            assert result == 1


def test_main_cwd_argument():
    """Test that main uses current working directory."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            with patch("hard_lint_py.cli.Path.cwd") as mock_cwd:
                mock_cwd.return_value = "/fake/path"
                mock_instance = mock_installer_class.return_value
                mock_instance.install.return_value = None

                main()

                mock_cwd.assert_called_once()
                # Verify HardLintInstaller was called with current directory
                mock_installer_class.assert_called_once()


def test_main_lint_command_dispatch():
    """CLI must dispatch lint subcommand to run_lint."""
    with patch("hard_lint_py.cli.run_lint", return_value=0) as mock_run_lint:
        with patch.object(sys, "argv", ["hard-lint-py", "lint", "src"]):
            result = main()

    assert result == 0
    mock_run_lint.assert_called_once_with(["src"])


def test_main_check_alias_dispatches_to_lint():
    """check subcommand remains as a compatibility alias to lint."""
    with patch("hard_lint_py.cli.run_lint", return_value=0) as mock_run_lint:
        with patch.object(sys, "argv", ["hard-lint-py", "check", "src"]):
            result = main()

    assert result == 0
    mock_run_lint.assert_called_once_with(["src"])


def test_find_docstrings_in_src_detects_docstring():
    """Docstrings must be detected so they can be rejected by validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "module.py").write_text(
            'def run() -> str:\n    """Allowed docstring."""\n    return "ok"\n'
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            docstrings = find_docstrings_in_src()

        assert len(docstrings) == 1
        assert docstrings[0][1] == 2


def test_find_comments_in_src_does_not_flag_docstring_as_comment():
    """Docstrings are not hash comments and should not appear in comment detector."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "module.py").write_text(
            'def run() -> str:\n    """Docstring."""\n    return "ok"\n'
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            comments = find_comments_in_src()

        assert comments == []


def test_run_check_fails_when_comments_exist():
    """run_check must fail if src/ contains hash-style comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "module.py").write_text(
            'def run() -> str:\n    # not allowed\n    return "ok"\n'
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = run_check(["src"])

        assert result == 1


def test_run_format_fails_when_comments_exist():
    """run_format must fail if src/ contains hash-style comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "module.py").write_text(
            'def run() -> str:\n    # not allowed\n    return "ok"\n'
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = run_format(["src"])

        assert result == 1


def test_run_check_fails_when_docstring_exists():
    """run_check must fail if src/ contains docstrings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "module.py").write_text(
            'def run() -> str:\n    """Not allowed."""\n    return "ok"\n'
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = run_check(["src"])

        assert result == 1
