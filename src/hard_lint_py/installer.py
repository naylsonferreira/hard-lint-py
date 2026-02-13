import subprocess
from pathlib import Path


class HardLintInstaller:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.git_dir = project_root / ".git"
        self.pre_commit_dir = project_root / ".hardlint"
        self.hooks_dir = self.pre_commit_dir / "_"
        self.pyproject_path = project_root / "pyproject.toml"

    def install(self) -> None:
        if not self._check_git_repo():
            raise RuntimeError("Not a Git repository. Initialize Git first with: git init")

        if not self._check_pyproject():
            raise RuntimeError("pyproject.toml not found in project root")

        self._setup_pre_commit_hooks()
        self._configure_git_hooks_path()
        self._ensure_pyproject_config()

    def _check_git_repo(self) -> bool:
        return self.git_dir.exists()

    def _check_pyproject(self) -> bool:
        return self.pyproject_path.exists()

    def _setup_pre_commit_hooks(self) -> None:
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create .gitignore in .hardlint
        (self.pre_commit_dir / ".gitignore").write_text("*")

        # Create pre-commit hook using poetry run
        pre_commit_content = (
            "#!/bin/sh\n"
            'cd "$(git rev-parse --show-toplevel)"\n'
            "poetry run ruff check . --fix && "
            "poetry run black . --quiet && "
            "poetry run isort . --quiet\n"
        )
        pre_commit_path = self.hooks_dir / "pre-commit"
        pre_commit_path.write_text(pre_commit_content)
        pre_commit_path.chmod(0o755)

        # Create commit-msg hook
        commit_msg_content = (
            "#!/bin/sh\n"
            'cd "$(git rev-parse --show-toplevel)"\n'
            'MESSAGE=$(cat "$1")\n'
            'poetry run python -c "import sys; import re; '
            "pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore)'; "
            "msg = '''$MESSAGE'''; "
            'sys.exit(0 if re.match(pattern, msg) else 1)"\n'
        )
        commit_msg_path = self.hooks_dir / "commit-msg"
        commit_msg_path.write_text(commit_msg_content)
        commit_msg_path.chmod(0o755)

    def _configure_git_hooks_path(self) -> None:
        try:
            subprocess.run(
                ["git", "config", "core.hooksPath", ".hardlint/_"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to configure Git: {e.stderr.decode()}") from e

    def _ensure_pyproject_config(self) -> None:
        pyproject_content = self.pyproject_path.read_text()

        # Check if tool.ruff exists
        if "[tool.ruff]" not in pyproject_content:
            pyproject_content += "\n[tool.ruff]\n"
            pyproject_content += "line-length = 100\n"
            pyproject_content += 'target-version = "py310"\n'
            pyproject_content += 'select = ["E", "F", "W", "I", "N", "C", "B"]\n'

        # Check if tool.black exists
        if "[tool.black]" not in pyproject_content:
            pyproject_content += "\n[tool.black]\n"
            pyproject_content += "line-length = 100\n"

        # Check if tool.isort exists
        if "[tool.isort]" not in pyproject_content:
            pyproject_content += "\n[tool.isort]\n"
            pyproject_content += 'profile = "black"\n'
            pyproject_content += "line_length = 100\n"

        self.pyproject_path.write_text(pyproject_content)
