import argparse
import subprocess
import sys
from pathlib import Path

from hard_lint_py.installer import HardLintInstaller


def check_install_status():
    """Check if hard-lint-py install was run and show warning if not."""
    hardlint_dir = Path.cwd() / ".hardlint" / "_"
    if not hardlint_dir.exists():
        print("WARNING: Pre-commit hooks not installed!")
        print("Run 'hard-lint-py install' to set up git hooks.")
        print("(You can still use check/format commands without it)\n")


def run_check(paths=None) -> int:
    check_install_status()
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
    check_install_status()
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
