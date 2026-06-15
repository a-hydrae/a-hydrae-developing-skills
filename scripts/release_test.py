#!/usr/bin/env python3
"""Run the a-hydrae-developing-skills test-release loop.

The default loop is offline and deterministic:

1. validate the skill metadata;
2. compile Python scripts;
3. validate JSON references;
4. run unit tests;
5. smoke-test CLI help;
6. package the skill into dist/;
7. write a release manifest.

Use --live to add network smoke tests for providers.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "a-hydrae-developing-skills"
DIST_DIR = ROOT / "dist"
VALIDATOR = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"


def run_step(name: str, cmd: list[str], *, cwd: Path = ROOT, live: bool = False, quiet: bool = False) -> dict[str, Any]:
    print(f"[run] {name}: {' '.join(cmd)}")
    started = dt.datetime.now(dt.UTC).isoformat()
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    finished = dt.datetime.now(dt.UTC).isoformat()
    status = "passed" if proc.returncode == 0 else "failed"
    if proc.stdout and not quiet:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.stderr and not quiet:
        print(proc.stderr, end="" if proc.stderr.endswith("\n") else "\n", file=sys.stderr)
    return {
        "name": name,
        "cmd": cmd,
        "status": status,
        "returncode": proc.returncode,
        "started_at": started,
        "finished_at": finished,
        "live": live,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
        "stdout_full": proc.stdout if live else "",
        "quiet": quiet,
    }


def require_pass(step: dict[str, Any]) -> None:
    if step["returncode"] != 0:
        raise SystemExit(f"release loop failed at step: {step['name']}")


def require_live_accepted_source(step: dict[str, Any]) -> None:
    require_pass(step)
    try:
        doc = json.loads(step.get("stdout_full") or "{}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"live step did not emit JSON: {step['name']}: {exc}") from exc
    sources = doc.get("sources") or []
    accepted = [source for source in sources if source.get("screening_status") != "reject"]
    if not accepted:
        notes = "; ".join(str(source.get("notes", "")) for source in sources[:3])
        raise SystemExit(f"live step had no accepted source: {step['name']}: {notes}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_skill_files() -> list[Path]:
    files = []
    for path in SKILL_DIR.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if "__pycache__" in parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return sorted(files)


def package_skill(version: str) -> dict[str, Any]:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive = DIST_DIR / f"a-hydrae-developing-skills-test-{version}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in iter_skill_files():
            tar.add(path, arcname=path.relative_to(ROOT))
    return {
        "archive": str(archive.relative_to(ROOT)),
        "sha256": sha256_file(archive),
        "bytes": archive.stat().st_size,
    }


def write_manifest(version: str, steps: list[dict[str, Any]], package: dict[str, Any]) -> Path:
    manifest = {
        "name": "a-hydrae-developing-skills",
        "version": version,
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "skill_dir": str(SKILL_DIR.relative_to(ROOT)),
        "package": package,
        "steps": steps,
        "status": "passed" if all(step["returncode"] == 0 for step in steps) else "failed",
    }
    path = DIST_DIR / f"a-hydrae-developing-skills-test-{version}.manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def offline_persist_smoke() -> dict[str, Any]:
    sample = {
        "question": {
            "user_request": "release smoke",
            "normalized_question": "release smoke",
            "languages": ["Python"],
            "platforms": [],
            "runtimes": [],
            "versions": [],
            "project_constraints": [],
        },
        "sources": [],
        "candidate_solutions": [],
        "decision": {
            "selected_solution_id": "",
            "rationale": "release smoke",
            "decisive_source_ids": [],
            "resolved_conflicts": [],
            "rejected_options": [],
        },
        "application": {
            "affected_files": [],
            "implementation_notes": "",
            "verification": ["release smoke"],
            "residual_limits": [],
        },
        "extension_registry": [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "finding.json"
        wiki_path = tmp_path / "wiki"
        input_path.write_text(json.dumps(sample), encoding="utf-8")
        return run_step(
            "persist smoke",
            [
                sys.executable,
                "a-hydrae-developing-skills/scripts/persist_finding.py",
                "--input",
                str(input_path),
                "--wiki",
                str(wiki_path),
            ],
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run validation, tests, and packaging for a test release.")
    parser.add_argument("--live", action="store_true", help="Run live network smoke tests.")
    parser.add_argument("--version", help="Release version suffix. Default: UTC timestamp.")
    parser.add_argument("--skip-package", action="store_true", help="Run tests without creating dist archive.")
    args = parser.parse_args(argv)

    version = args.version or dt.datetime.now(dt.UTC).strftime("%Y%m%d%H%M%S")
    steps: list[dict[str, Any]] = []

    commands = [
        ("skill validate", [sys.executable, str(VALIDATOR), "a-hydrae-developing-skills"], False),
        ("compile scripts", [sys.executable, "-m", "py_compile", "a-hydrae-developing-skills/scripts/source_search.py", "a-hydrae-developing-skills/scripts/persist_finding.py"], False),
        ("catalog json", [sys.executable, "-m", "json.tool", "a-hydrae-developing-skills/references/source-catalog.json"], True),
        ("unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], False),
        ("source_search help", [sys.executable, "a-hydrae-developing-skills/scripts/source_search.py", "--help"], True),
        ("persist_finding help", [sys.executable, "a-hydrae-developing-skills/scripts/persist_finding.py", "--help"], True),
    ]
    for name, cmd, quiet in commands:
        step = run_step(name, cmd, quiet=quiet)
        steps.append(step)
        require_pass(step)

    step = offline_persist_smoke()
    steps.append(step)
    require_pass(step)

    if args.live:
        live_commands = [
            (
                "live direct-url microsoft learn",
                [
                    sys.executable,
                    "a-hydrae-developing-skills/scripts/source_search.py",
                    "--provider",
                    "direct-url",
                    "--query",
                    "CreateFileW FILE_FLAG_OVERLAPPED",
                    "--url",
                    "https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew",
                    "--language",
                    "C++",
                    "--platform",
                    "Windows",
                ],
            ),
            (
                "live pypi",
                [
                    sys.executable,
                    "a-hydrae-developing-skills/scripts/source_search.py",
                    "--provider",
                    "pypi",
                    "--pypi-package",
                    "requests",
                    "--language",
                    "Python",
                ],
            ),
            (
                "live stackexchange",
                [
                    sys.executable,
                    "a-hydrae-developing-skills/scripts/source_search.py",
                    "--provider",
                    "stackexchange",
                    "--query",
                    "python asyncio TaskGroup exception",
                    "--language",
                    "Python",
                    "--limit",
                    "1",
                ],
            ),
        ]
        for name, cmd in live_commands:
            step = run_step(name, cmd, live=True, quiet=True)
            steps.append(step)
            require_live_accepted_source(step)

    package = {"archive": None, "sha256": None, "bytes": 0}
    if not args.skip_package:
        package = package_skill(version)
        print(f"[package] {package['archive']} sha256={package['sha256']}")

    manifest_path = write_manifest(version, steps, package)
    print(f"[manifest] {manifest_path.relative_to(ROOT)}")
    print("[ok] test release loop passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
