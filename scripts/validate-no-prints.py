import ast
import sys
from pathlib import Path


class PrintCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.prints = []

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.prints.append((node.lineno, 'print()'))
        self.generic_visit(node)


def has_print_calls(file_path: Path) -> list[tuple[int, str]]:
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        visitor = PrintCallVisitor()
        visitor.visit(tree)
        return visitor.prints
    except SyntaxError:
        return []


def main() -> int:
    src_path = Path('src')
    found_prints = False

    for py_file in src_path.rglob('*.py'):
        prints = has_print_calls(py_file)
        if prints:
            found_prints = True
            for line_num, print_call in prints:
                print(f'{py_file}:{line_num}: {print_call}')

    if found_prints:
        print(f'\nFound print statements in code. Remove them!', file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
