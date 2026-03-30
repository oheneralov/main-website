#!/usr/bin/env python
"""
Linting script for the langchain-rag project.
Runs ruff and mypy checks.
"""

import subprocess
import sys
from pathlib import Path

# Get the backend directory
BACKEND_DIR = Path(__file__).parent
SRC_DIRS = [
    BACKEND_DIR / "*.py",
    BACKEND_DIR / "tests",
]


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'=' * 60}")
    print(f"[CHECK] {description}")
    print(f"{'=' * 60}")
    try:
        result = subprocess.run(cmd, cwd=BACKEND_DIR, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print(f"[FAIL] Command not found: {cmd[0]}")
        print("   Install with: pip install -r requirements-dev.txt")
        return False


def run_tool_command(module_name: str, args: list[str], description: str) -> bool:
    """
    Run a tool via module or directly by name.
    Tries sys.executable first, then falls back to tool name (searches PATH).
    """
    print(f"\n{'=' * 60}")
    print(f"[CHECK] {description}")
    print(f"{'=' * 60}")

    # Try with sys.executable first
    cmd = [sys.executable, "-m", module_name, *args]
    try:
        result = subprocess.run(
            cmd,
            cwd=BACKEND_DIR,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if "No module named" not in result.stderr:
            # Print output for details
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.returncode == 0
    except (FileNotFoundError, Exception):
        pass

    # Fallback: try tool name directly (will search PATH for global Python installation)
    cmd = [module_name, *args]
    try:
        result = subprocess.run(
            cmd, cwd=BACKEND_DIR, check=False, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print(f"[FAIL] Tool not found: {module_name}")
        print("   Install with: pip install -r requirements-dev.txt")
        return False


def main():
    """Run all linting checks."""
    results = {}

    # Run ruff check
    results["ruff check"] = run_tool_command(
        "ruff", ["check", "."], "Running ruff (fast linter)"
    )

    # Run ruff format check
    results["ruff format"] = run_tool_command(
        "ruff", ["format", ".", "--check"], "Checking code formatting with ruff"
    )

    # Run mypy - only check our own Python files in the backend directory
    project_files = [f.name for f in Path(".").glob("*.py") if f.is_file()]
    results["mypy"] = run_tool_command(
        "mypy",
        [*project_files, "--no-site-packages"],
        "Running type checker (mypy)",
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("[SUMMARY] Linting Summary")
    print(f"{'=' * 60}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for tool, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{tool:.<40} {status}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n[OK] All linting checks passed!")
        return 0
    else:
        print("\n[WARNING] Some linting checks failed.")
        print("\nTo auto-fix issues, run:")
        print("  python lint.py --fix")
        return 1


def fix_issues():
    """Auto-fix linting issues."""
    print("[ACTION] Auto-fixing linting issues...\n")

    # Run ruff format
    run_tool_command("ruff", ["format", "."], "Formatting with ruff")

    print("\n[OK] Auto-fixing complete!")


if __name__ == "__main__":
    if "--fix" in sys.argv:
        fix_issues()
    else:
        sys.exit(main())
