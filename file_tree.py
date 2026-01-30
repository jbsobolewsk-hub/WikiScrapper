# file_tree.py

from pathlib import Path
from typing import List

EXCLUDED_DIRS = {".venv", ".git", ".idea", "__pycache__"}
EXCLUDED_EXTENSIONS = {".pdf", ".zip"}
EXCLUDED_FILES = {"file_tree.py", ".editorconfig"}
README_PATH = Path("README.md")


def build_tree(root: Path, prefix: str = "") -> List[str]:
    lines = []

    entries = sorted(
        (
            p for p in root.iterdir()
            if not (
            (p.is_dir() and p.name in EXCLUDED_DIRS)
            or (p.is_file() and p.suffix.lower() in EXCLUDED_EXTENSIONS)
            or (p.is_file() and p.name in EXCLUDED_FILES)
        )
        ),
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for idx, path in enumerate(entries):
        is_dir = path.is_dir()
        name = f"{path.name}/" if is_dir else path.name

        connector = "└── " if idx == len(entries) - 1 else "├── "
        lines.append(prefix + connector + name)

        if is_dir:
            extension = "    " if idx == len(entries) - 1 else "│   "
            lines.extend(build_tree(path, prefix + extension))

    return lines


def generate_tree_text(root: Path) -> str:
    lines = [f"{root.name}/"]
    lines.extend(build_tree(root))
    return "\n".join(lines)


def update_readme(tree_text: str) -> None:
    if not README_PATH.exists():
        raise FileNotFoundError("README.md not found")

    content = README_PATH.read_text(encoding="utf-8")

    marker = "```bash\n"
    blocks = content.split(marker)

    if len(blocks) < 2:
        raise ValueError("README.md does not contain a target bash block")

    # last bash block
    before = marker.join(blocks[:-1])
    last = blocks[-1]

    if "```" not in last:
        raise ValueError("Malformed bash code block")

    _, after = last.split("```", 1)

    new_block = f"{marker}\n{tree_text}\n```"

    README_PATH.write_text(
        before + new_block + after,
        encoding="utf-8"
    )


def main():
    root = Path(".").resolve()
    tree_text = generate_tree_text(root)
    # print(tree_text)
    update_readme(tree_text)


if __name__ == "__main__":
    main()
