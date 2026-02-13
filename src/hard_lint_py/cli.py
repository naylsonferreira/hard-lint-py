import sys
from pathlib import Path

from hard_lint_py.installer import HardLintInstaller


def main() -> int:
    try:
        installer = HardLintInstaller(Path.cwd())
        installer.install()
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
