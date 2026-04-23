import argparse
import ast
import io
import subprocess
import sys
import tokenize
import tomllib
from pathlib import Path

from pathspec import PathSpec

from hard_lint_py.installer import HardLintInstaller


IGNORED_PATH_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
    "dist",
    ".hardlint",
}


def _resolve_validation_targets(paths: list[str] | None) -> list[Path]:
    target_paths = paths if paths else ["src"]
    resolved: list[Path] = []

    for raw_path in target_paths:
        path = Path(raw_path)
        candidate = path if path.is_absolute() else (Path.cwd() / path)
        if candidate.exists():
            resolved.append(candidate)

    return resolved


def _load_gitignore_spec() -> PathSpec | None:
    gitignore = Path.cwd() / ".gitignore"
    if not gitignore.exists():
        return None

    lines = gitignore.read_text().splitlines()
    return PathSpec.from_lines("gitignore", lines)


def _is_path_ignored(path: Path) -> bool:
    if any(part in IGNORED_PATH_PARTS for part in path.parts):
        return True

    spec = _load_gitignore_spec()
    if spec is None:
        return False

    try:
        relative = path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return False

    return spec.match_file(relative.as_posix())


def _iter_python_files(paths: list[str] | None):
    seen: set[Path] = set()

    for target in _resolve_validation_targets(paths):
        if target.is_file():
            if target.suffix == ".py" and not _is_path_ignored(target):
                normalized = target.resolve()
                if normalized not in seen:
                    seen.add(normalized)
                    yield normalized
            continue

        for py_file in target.rglob("*.py"):
            if _is_path_ignored(py_file):
                continue
            normalized = py_file.resolve()
            if normalized in seen:
                continue
            seen.add(normalized)
            yield normalized


def find_comments_in_src(paths: list[str] | None = None) -> list[tuple[Path, int, str]]:
    found: list[tuple[Path, int, str]] = []

    for py_file in _iter_python_files(paths):
        content = py_file.read_text()
        try:
            tokens = tokenize.generate_tokens(io.StringIO(content).readline)
            for token_type, token_string, (start_line, _), _, _ in tokens:
                if token_type == tokenize.COMMENT and not token_string.startswith("#!"):
                    found.append((py_file, start_line, token_string.strip()))
        except tokenize.TokenError:
            continue

    return found


def _collect_docstrings_from_node(node: ast.AST, file_path: Path) -> list[tuple[Path, int, str]]:
    found: list[tuple[Path, int, str]] = []

    body = getattr(node, "body", None)
    if isinstance(body, list) and body:
        first_stmt = body[0]
        if (
            isinstance(first_stmt, ast.Expr)
            and isinstance(first_stmt.value, ast.Constant)
            and isinstance(first_stmt.value.value, str)
        ):
            doc = (
                first_stmt.value.value.strip().splitlines()[0]
                if first_stmt.value.value.strip()
                else ""
            )
            line = getattr(first_stmt, "lineno", 1)
            found.append((file_path, line, doc))

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            found.extend(_collect_docstrings_from_node(child, file_path))

    return found


def find_docstrings_in_src(paths: list[str] | None = None) -> list[tuple[Path, int, str]]:
    found: list[tuple[Path, int, str]] = []

    for py_file in _iter_python_files(paths):
        content = py_file.read_text()
        try:
            module = ast.parse(content)
        except SyntaxError:
            continue
        found.extend(_collect_docstrings_from_node(module, py_file))

    return found


def find_non_empty_init_files(paths: list[str] | None = None) -> list[Path]:
    found: list[Path] = []

    for py_file in _iter_python_files(paths):
        if py_file.name != "__init__.py":
            continue
        if py_file.read_text().strip():
            found.append(py_file)

    return found


def validate_empty_init_files(paths: list[str] | None = None) -> int:
    violations = find_non_empty_init_files(paths)
    if not violations:
        return 0

    for py_file in violations:
        print(f"{py_file}: __init__.py must be empty")

    print("\nFound non-empty __init__.py files. They must be kept empty!", file=sys.stderr)
    return 1


def validate_no_comments_rule(paths: list[str] | None = None) -> int:
    comments = find_comments_in_src(paths)
    docstrings = find_docstrings_in_src(paths)
    if not comments and not docstrings:
        return 0

    for py_file, line_num, comment in comments:
        print(f"{py_file}:{line_num}: {comment}")

    for py_file, line_num, doc in docstrings:
        print(f"{py_file}:{line_num}: docstring -> {doc}")

    print("\nFound comments/docstrings in code. Remove them!", file=sys.stderr)
    return 1


def check_lint_config_override() -> int:
    is_hard_lint_py_repo = (Path.cwd() / "src" / "hard_lint_py" / "cli.py").exists()
    if is_hard_lint_py_repo:
        return 0

    pyproject = Path.cwd() / "pyproject.toml"

    if not pyproject.exists():
        return 0

    try:
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)
    except Exception:
        return 0

    tool_config = config.get("tool", {})
    forbidden_configs = ["ruff", "black", "isort", "pylint", "flake8"]
    found_configs = [c for c in forbidden_configs if c in tool_config]

    if found_configs:
        print(f"ERROR: Project has lint configuration overrides: {', '.join(found_configs)}")
        print(
            "Hard-lint-py manages all lint configurations. Remove these sections from"
            " pyproject.toml"
        )
        return 1

    config_files = [".flake8", ".pylintrc", "setup.cfg", "tox.ini"]
    found_files = [f for f in config_files if Path.cwd().joinpath(f).exists()]

    if found_files:
        print(f"ERROR: Project has lint configuration files: {', '.join(found_files)}")
        print("Hard-lint-py manages all lint configurations. Remove these files.")
        return 1

    return 0


def check_install_status() -> int:
    hardlint_dir = Path.cwd() / ".hardlint" / "_"
    if not hardlint_dir.exists():
        print("ERROR: Pre-commit hooks not installed!")
        print("Run 'hard-lint-py install' to set up git hooks.")
        return 1
    return 0


def run_lint(paths=None) -> int:
    if check_lint_config_override() != 0:
        return 1
    if check_install_status() != 0:
        return 1
    target_paths = paths if paths else ["."]
    if validate_no_comments_rule(target_paths) != 0:
        return 1
    if validate_empty_init_files(target_paths) != 0:
        return 1
    try:
        print(f"Running checks on {target_paths}...")
        subprocess.run(["poetry", "run", "ruff", "check", *target_paths], check=True)
        subprocess.run(
            ["poetry", "run", "black", "--check", "--line-length", "100", *target_paths],
            check=True,
        )
        subprocess.run(
            [
                "poetry",
                "run",
                "isort",
                "--check-only",
                "--profile",
                "black",
                "--line-length",
                "100",
                *target_paths,
            ],
            check=True,
        )
        print("All checks passed!")
        return 0
    except subprocess.CalledProcessError:
        print("Checks failed.")
        return 1


def run_format(paths=None) -> int:
    if check_lint_config_override() != 0:
        return 1
    if check_install_status() != 0:
        return 1
    target_paths = paths if paths else ["."]
    if validate_no_comments_rule(target_paths) != 0:
        return 1
    if validate_empty_init_files(target_paths) != 0:
        return 1
    try:
        print(f"Running formatting on {target_paths}...")
        subprocess.run(
            ["poetry", "run", "black", "--line-length", "100", *target_paths], check=True
        )
        subprocess.run(
            [
                "poetry",
                "run",
                "isort",
                "--profile",
                "black",
                "--line-length",
                "100",
                *target_paths,
            ],
            check=True,
        )
        subprocess.run(["poetry", "run", "ruff", "check", "--fix", *target_paths], check=True)
        print("Formatting complete!")
        return 0
    except subprocess.CalledProcessError:
        print("Formatting failed.")
        return 1


def run_verify(paths=None) -> int:
    if check_lint_config_override() != 0:
        return 1
    if check_install_status() != 0:
        return 1
    try:
        print("Running verification (lint + tests)...")
        if run_lint(paths) != 0:
            print("Lint checks failed. Aborting verification.")
            return 1

        print("Running tests...")
        subprocess.run(["poetry", "run", "pytest"], check=True)
        print("Verification complete! All checks and tests passed.")
        return 0
    except subprocess.CalledProcessError:
        print("Tests failed.")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Hard Lint CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("install", help="Install hardlint configuration")

    lint_parser = subparsers.add_parser("lint", help="Run lint checks")
    lint_parser.add_argument("paths", nargs="*", help="Paths to lint")

    check_parser = subparsers.add_parser("check", help="Run lint checks (alias for lint)")
    check_parser.add_argument("paths", nargs="*", help="Paths to check")

    format_parser = subparsers.add_parser("format", help="Run formatting")
    format_parser.add_argument("paths", nargs="*", help="Paths to format")

    verify_parser = subparsers.add_parser("verify", help="Run verification (lint + tests)")
    verify_parser.add_argument("paths", nargs="*", help="Paths to verify (passed to lint check)")

    if len(sys.argv) == 1:
        try:
            installer = HardLintInstaller(Path.cwd())
            installer.install()
            print("Hardlint configuration installed successfully.")
            return 0
        except Exception as e:
            print(f"Installation failed: {e}")
            return 1

    args = parser.parse_args()

    if args.command == "install":
        try:
            installer = HardLintInstaller(Path.cwd())
            installer.install()
            print("Hardlint configuration installed successfully.")
            return 0
        except Exception as e:
            print(f"Installation failed: {e}")
            return 1
    elif args.command == "lint":
        return run_lint(args.paths)
    elif args.command == "check":
        return run_lint(args.paths)
    elif args.command == "format":
        return run_format(args.paths)
    elif args.command == "verify":
        return run_verify(args.paths)

    return 0


if __name__ == "__main__":
    sys.exit(main())


run_check = run_lint
