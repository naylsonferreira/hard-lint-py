import io
import sys
import tokenize
from pathlib import Path


def has_comments(file_path: Path) -> list[tuple[int, str]]:
    content = file_path.read_text()

    comments = []

    try:
        tokens = tokenize.generate_tokens(io.StringIO(content).readline)
        for token_type, token_string, (start_line, _), _, _ in tokens:
            if token_type == tokenize.COMMENT:
                if not token_string.startswith("#!"):
                    comments.append((start_line, token_string.strip()))
    except tokenize.TokenError:
        pass

    return comments


def main() -> int:
    src_path = Path("src")
    found_comments = False

    for py_file in src_path.rglob("*.py"):
        comments = has_comments(py_file)
        if comments:
            found_comments = True
            for line_num, comment in comments:
                print(f"{py_file}:{line_num}: {comment}")

    if found_comments:
        print("\nFound comments in code. Remove them!", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
