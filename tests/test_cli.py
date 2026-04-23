import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from hard_lint_py.cli import (
    find_comments_in_src,
    find_docstrings_in_src,
    find_non_empty_init_files,
    main,
    run_check,
    run_format,
    validate_empty_init_files,
    validate_no_comments_rule,
)


def test_main_success():
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.return_value = None

            result = main()

            assert result == 0
            mock_installer_class.assert_called_once()
            mock_instance.install.assert_called_once()


def test_main_with_error():
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.side_effect = RuntimeError("Test error")

            with patch("sys.stdout"):
                result = main()

            assert result == 1
            mock_instance.install.assert_called_once()


def test_main_with_generic_exception():
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            mock_instance = mock_installer_class.return_value
            mock_instance.install.side_effect = Exception("Unexpected error")

            with patch("sys.stdout"):
                result = main()

            assert result == 1


def test_main_cwd_argument():
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch.object(sys, "argv", ["hard-lint-py"]):
            with patch("hard_lint_py.cli.Path.cwd") as mock_cwd:
                mock_cwd.return_value = "/fake/path"
                mock_instance = mock_installer_class.return_value
                mock_instance.install.return_value = None

                main()

                mock_cwd.assert_called_once()
                mock_installer_class.assert_called_once()


def test_main_lint_command_dispatch():
    with patch("hard_lint_py.cli.run_lint", return_value=0) as mock_run_lint:
        with patch.object(sys, "argv", ["hard-lint-py", "lint", "src"]):
            result = main()

    assert result == 0
    mock_run_lint.assert_called_once_with(["src"])


def test_main_check_alias_dispatches_to_lint():
    with patch("hard_lint_py.cli.run_lint", return_value=0) as mock_run_lint:
        with patch.object(sys, "argv", ["hard-lint-py", "check", "src"]):
            result = main()

    assert result == 0
    mock_run_lint.assert_called_once_with(["src"])


def test_find_docstrings_in_src_detects_docstring():
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


def test_validate_rule_respects_src_scope():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"
        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        (src_dir / "module.py").write_text('def run() -> str:\n    return "ok"\n')
        (tests_dir / "test_module.py").write_text(
            "def test_run() -> None:\n    # only in tests\n    assert True\n"
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = validate_no_comments_rule(["src"])

        assert result == 0


def test_validate_rule_respects_tests_scope():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        (tests_dir / "test_module.py").write_text(
            "def test_run() -> None:\n    # not allowed\n    assert True\n"
        )

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = validate_no_comments_rule(["tests"])

        assert result == 1


def test_find_non_empty_init_files_detects_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("from .module import something\n")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = find_non_empty_init_files(["src"])

        assert len(result) == 1


def test_find_non_empty_init_files_allows_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = find_non_empty_init_files(["src"])

        assert result == []


def test_find_non_empty_init_files_allows_whitespace_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("\n\n")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = find_non_empty_init_files(["src"])

        assert result == []


def test_validate_empty_init_files_returns_1_on_violation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("x = 1\n")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = validate_empty_init_files(["src"])

        assert result == 1


def test_validate_empty_init_files_returns_0_when_clean():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = validate_empty_init_files(["src"])

        assert result == 0


def test_run_check_fails_when_init_has_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("from .module import something\n")

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = run_check(["src"])

        assert result == 1


def test_validate_rule_respects_gitignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (tmp_path / ".gitignore").write_text("src/\n")
        (src_dir / "module.py").write_text('def run() -> str:\n    # ignored\n    return "ok"\n')

        with patch("hard_lint_py.cli.Path.cwd", return_value=tmp_path):
            result = validate_no_comments_rule(["."])

        assert result == 0
