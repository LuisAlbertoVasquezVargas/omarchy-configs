# scripts/compare_configs.py

import os
import sys
from difflib import unified_diff
from filecmp import cmp
from pathlib import Path

MAX_DIFF_LINES = 40

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
    home_file: Path,
    relative_path: Path,
) -> None:
    repo_lines = read_lines(repo_file)
    home_lines = read_lines(home_file)

    if repo_lines is None or home_lines is None:
        print("  Text diff unavailable for this file.")
        return

    diff_lines = list(
        unified_diff(
            repo_lines,
            home_lines,
            fromfile=f"repo/.config/{relative_path}",
            tofile=f"home/.config/{relative_path}",
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


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    repo_config = repo_root / ".config"
    home_config = Path.home() / ".config"

    if not repo_config.is_dir():
        raise SystemExit(
            f"Repository config directory not found: {repo_config}"
        )

    matches: list[Path] = []
    mismatches: list[Path] = []
    missing: list[Path] = []

    print(color("Config comparison", BOLD))
    print(f"Repository: {repo_config}")
    print(f"Current:    {home_config}")
    print()

    for repo_file in sorted(repo_config.rglob("*")):
        if repo_file.is_symlink() or not repo_file.is_file():
            continue

        relative_path = repo_file.relative_to(repo_config)
        home_file = home_config / relative_path

        if not home_file.exists():
            print(f"{label('missing', RED)} {relative_path}")
            print(f"  Not found at: {home_file}")
            print()
            missing.append(relative_path)
            continue

        if home_file.is_symlink() or not home_file.is_file():
            continue

        if cmp(repo_file, home_file, shallow=False):
            print(f"{label('match', GREEN)} {relative_path}")
            matches.append(relative_path)
            continue

        print(f"{label('mismatch', YELLOW)} {relative_path}")
        print_diff(repo_file, home_file, relative_path)
        print()

        mismatches.append(relative_path)

    print()
    print(color("Comparison report", BOLD))
    print_report_group("match", GREEN, matches)
    print()
    print_report_group("mismatch", YELLOW, mismatches)
    print()
    print_report_group("missing", RED, missing)


if __name__ == "__main__":
    main()
