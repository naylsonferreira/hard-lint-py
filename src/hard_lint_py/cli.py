"""Command-line interface for hard-lint-py."""

import sys
from pathlib import Path

from hard_lint_py.installer import HardLintInstaller


def main() -> int:
    """Main entry point for hard-lint-py CLI."""
    try:
        installer = HardLintInstaller(Path.cwd())
        installer.install()
        return 0
    except Exception as e:
        print(f"[ERROR] {e!s}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
