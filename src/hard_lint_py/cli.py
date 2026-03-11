import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

from hard_lint_py.installer import HardLintInstaller


def check_lint_config_override() -> int:
    """Check if project has lint config overrides that conflict with hard-lint-py."""
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
    """Check if hard-lint-py install was run and raise error if not."""
    hardlint_dir = Path.cwd() / ".hardlint" / "_"
    if not hardlint_dir.exists():
        print("ERROR: Pre-commit hooks not installed!")
        print("Run 'hard-lint-py install' to set up git hooks.")
        return 1
    return 0


def run_check(paths=None) -> int:
    if check_lint_config_override() != 0:
        return 1
    if check_install_status() != 0:
        return 1
    target_paths = paths if paths else ["."]
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
        if run_check(paths) != 0:
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

    check_parser = subparsers.add_parser("check", help="Run lint checks")
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
    elif args.command == "check":
        return run_check(args.paths)
    elif args.command == "format":
        return run_format(args.paths)
    elif args.command == "verify":
        return run_verify(args.paths)

    return 0


if __name__ == "__main__":
    sys.exit(main())
