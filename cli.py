#!/usr/bin/env python3
"""DataForge CLI — Setup, Dev, Test, Ship."""

import argparse
import subprocess
import sys
import os


def run(cmd: str, check: bool = True):
    """Run a shell command."""
    print(f"  > {cmd}")
    return subprocess.run(cmd, shell=True, check=check)


def cmd_setup(_args):
    """Setup virtual environment and install dependencies."""
    print("[setup] Creating virtual environment...")
    run(f"{sys.executable} -m venv .venv")
    pip = ".venv/Scripts/pip" if os.name == "nt" else ".venv/bin/pip"
    run(f"{pip} install -r requirements.txt")
    run(f"{pip} install pytest httpx anyio pytest-anyio")
    print("[setup] Done!")


def cmd_dev(_args):
    """Run development server."""
    print("[dev] Starting DataForge dev server...")
    run("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def cmd_test(_args):
    """Run test suite."""
    print("[test] Running tests...")
    run("python -m pytest tests/ -v")


def cmd_spotlight(_args):
    """Open API docs in browser."""
    import webbrowser
    webbrowser.open("http://localhost:8000/docs")
    print("[spotlight] Opened /docs in browser")


def cmd_ship(_args):
    """Build and deploy to Railway."""
    print("[ship] Running pre-deploy checks...")
    result = run("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        print("[ship] Tests failed! Fix before deploying.")
        sys.exit(1)
    print("[ship] Tests passed. Deploying...")
    run("railway up", check=False)
    print("[ship] Done!")


def main():
    parser = argparse.ArgumentParser(description="DataForge CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Setup project")
    sub.add_parser("dev", help="Run dev server")
    sub.add_parser("test", help="Run tests")
    sub.add_parser("spotlight", help="Open API docs")
    sub.add_parser("ship", help="Deploy to Railway")

    args = parser.parse_args()
    commands = {
        "setup": cmd_setup,
        "dev": cmd_dev,
        "test": cmd_test,
        "spotlight": cmd_spotlight,
        "ship": cmd_ship,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
