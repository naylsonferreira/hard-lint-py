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
        self._setup_gitlint_config()
        self._configure_git_hooks_path()

    def _check_git_repo(self) -> bool:
        return self.git_dir.exists()

    def _check_pyproject(self) -> bool:
        return self.pyproject_path.exists()

    def _setup_pre_commit_hooks(self) -> None:
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        (self.pre_commit_dir / ".gitignore").write_text("*")

        pre_commit_content = (
            '#!/bin/sh\ncd "$(git rev-parse --show-toplevel)"\npoetry run hard-lint-py format .\n'
        )
        pre_commit_path = self.hooks_dir / "pre-commit"
        pre_commit_path.write_text(pre_commit_content)
        pre_commit_path.chmod(0o755)

        commit_msg_content = (
            "#!/bin/sh\n"
            'cd "$(git rev-parse --show-toplevel)"\n'
            'poetry run gitlint --config .hardlint/gitlint --msg-filename "$1"\n'
        )
        commit_msg_path = self.hooks_dir / "commit-msg"
        commit_msg_path.write_text(commit_msg_content)
        commit_msg_path.chmod(0o755)

    def _setup_gitlint_config(self) -> None:
        gitlint_config = (
            "[general]\n"
            "\n"
            "[title-match-regex]\n"
            "regex=^(feat|fix|docs|style|refactor|perf|test|chore)(\\(.+\\))?: .+\n"
        )
        (self.pre_commit_dir / "gitlint").write_text(gitlint_config)

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
