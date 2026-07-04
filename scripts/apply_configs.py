# scripts/apply_configs.py

import os
import sys
from datetime import datetime
from difflib import unified_diff
from filecmp import cmp
from pathlib import Path
from shutil import copy2

MAX_DIFF_LINES = 20

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"


def color(text: str, code: str) -> str:
    if not USE_COLOR:
        return text

    return f"{code}{text}{RESET}"


def label(name: str, code: str) -> str:
    return color(f"[{name}]", code)


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (UnicodeDecodeError, OSError):
        return None


def color_diff_line(line: str) -> str:
    if line.startswith("+++") or line.startswith("---"):
        return color(line, CYAN)

    if line.startswith("+"):
        return color(line, GREEN)

    if line.startswith("-"):
        return color(line, RED)

    if line.startswith("@@"):
        return color(line, MAGENTA)

    return line


def print_diff(
    repo_file: Path,
    system_file: Path,
    relative_path: Path,
) -> None:
    repo_lines = read_lines(repo_file)
    system_lines = read_lines(system_file)

    if repo_lines is None or system_lines is None:
        print("  Text diff unavailable for this file.")
        return

    diff_lines = list(
        unified_diff(
            system_lines,
            repo_lines,
            fromfile=f"system/.config/{relative_path}",
            tofile=f"repo/.config/{relative_path}",
            lineterm="",
        )
    )

    for line in diff_lines[:MAX_DIFF_LINES]:
        print(f"  {color_diff_line(line.rstrip())}")

    omitted = len(diff_lines) - MAX_DIFF_LINES

    if omitted > 0:
        print(f"  ... {omitted} additional diff lines omitted")


def print_report_group(
    name: str,
    code: str,
    files: list[Path],
) -> None:
    print(f"{label(name, code)} {len(files)}")

    for file in files:
        print(f"  - {file}")


def confirm_apply() -> bool:
    print()
    response = input("Type 'yes' to apply these changes: ")
    return response.strip().lower() == "yes"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    repo_config = repo_root / ".config"
    system_config = Path.home() / ".config"

    if not repo_config.is_dir():
        raise SystemExit(
            f"Repository config directory not found: {repo_config}"
        )

    matches: list[Path] = []
    creations: list[tuple[Path, Path, Path]] = []
    replacements: list[tuple[Path, Path, Path]] = []

    print(color("Config deployment preview", BOLD))
    print(f"Source: {repo_config}")
    print(f"Target: {system_config}")
    print()

    for repo_file in sorted(repo_config.rglob("*")):
        if repo_file.is_symlink() or not repo_file.is_file():
            continue

        relative_path = repo_file.relative_to(repo_config)
        system_file = system_config / relative_path

        if system_file.is_symlink():
            raise SystemExit(
                f"Refusing to replace symbolic link: {system_file}"
            )

        if not system_file.exists():
            print(f"{label('create', CYAN)} {relative_path}")
            creations.append((repo_file, system_file, relative_path))
            continue

        if not system_file.is_file():
            raise SystemExit(
                f"Refusing to replace non-regular path: {system_file}"
            )

        if cmp(repo_file, system_file, shallow=False):
            print(f"{label('match', GREEN)} {relative_path}")
            matches.append(relative_path)
            continue

        print(f"{label('replace', YELLOW)} {relative_path}")
        print_diff(repo_file, system_file, relative_path)
        print()

        replacements.append((repo_file, system_file, relative_path))

    print()
    print(color("Deployment report", BOLD))
    print_report_group("match", GREEN, matches)
    print()
    print_report_group(
        "create",
        CYAN,
        [relative for _, _, relative in creations],
    )
    print()
    print_report_group(
        "replace",
        YELLOW,
        [relative for _, _, relative in replacements],
    )

    if not creations and not replacements:
        return

    if not confirm_apply():
        print(color("Deployment cancelled.", RED))
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = (
        Path.home()
        / ".local"
        / "state"
        / "omarchy-configs"
        / "backups"
        / timestamp
        / ".config"
    )

    if replacements:
        for _, system_file, relative_path in replacements:
            backup_file = backup_root / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            copy2(system_file, backup_file)

    for repo_file, system_file, relative_path in creations:
        system_file.parent.mkdir(parents=True, exist_ok=True)
        copy2(repo_file, system_file)
        print(f"{label('created', CYAN)} {relative_path}")

    for repo_file, system_file, relative_path in replacements:
        system_file.parent.mkdir(parents=True, exist_ok=True)
        copy2(repo_file, system_file)
        print(f"{label('replaced', GREEN)} {relative_path}")

    print()
    print(color("Deployment complete", BOLD))
    print(f"Created:  {len(creations)}")
    print(f"Replaced: {len(replacements)}")

    if replacements:
        print(f"Backup:   {backup_root.parent}")


if __name__ == "__main__":
    main()
