#!/usr/bin/env python3
"""Read-only deterministic inventory of repository quality-control surfaces."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


PATTERNS = {
    "manifests": ("package.json", "pyproject.toml", "Cargo.toml", "go.mod", "Makefile", "justfile"),
    "hooks": (".githooks/*", ".husky/*", "lefthook.yml", ".pre-commit-config.yaml"),
    "ci": (".github/workflows/*", ".gitlab-ci.yml", "Jenkinsfile"),
    "quality": ("*eslint*", "*ruff*", "*mypy*", "*pytest*", "*vitest*", "*jest*", "*coverage*"),
    "security": ("*trufflehog*", "*gitleaks*", "*semgrep*", "*osv*", "*dependabot*"),
}


def git(repo: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def tracked(repo: Path) -> list[str]:
    output = git(repo, "ls-files")
    return sorted(output.splitlines()) if output else []


def matches(files: list[str], pattern: str) -> list[str]:
    from fnmatch import fnmatch
    return [path for path in files if fnmatch(path, pattern) or fnmatch(Path(path).name, pattern)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    files = tracked(repo)
    if not files:
        parser.error(f"not a Git repository or no tracked files: {repo}")

    configured = git(repo, "config", "--local", "--get", "core.hooksPath")
    effective = git(repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks")
    surfaces = {
        group: sorted({path for pattern in patterns for path in matches(files, pattern)})
        for group, patterns in PATTERNS.items()
    }
    result = {
        "schema_version": "omp.quality-control-inventory.v1",
        "repository": str(repo),
        "revision": git(repo, "rev-parse", "HEAD"),
        "dirty": bool(git(repo, "status", "--porcelain=v1")),
        "effective_hooks": {
            "configured_core_hooks_path": configured,
            "path": effective,
            "pre_commit_executable": bool(effective and (Path(effective) / "pre-commit").is_file()),
            "pre_push_executable": bool(effective and (Path(effective) / "pre-push").is_file()),
        },
        "surfaces": surfaces,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
