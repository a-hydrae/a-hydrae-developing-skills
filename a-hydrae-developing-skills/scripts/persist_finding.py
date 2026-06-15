#!/usr/bin/env python3
"""Persist normalized a-hydrae-developing-skills findings into an Obsidian wiki.

Input is the JSON normalizer shape emitted by source_search.py, optionally
completed by an agent with a decision and verification. The script writes:

- a human-readable Markdown note under wiki/resolved/<bucket>/;
- the raw normalized JSON under wiki/data/findings/;
- an index entry under wiki/resolved/Index.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


BUCKET_ALIASES = {
    "c++": "cpp",
    "cpp": "cpp",
    "c#": "csharp",
    "csharp": "csharp",
    "python": "python",
    "windows": "windows",
    "linux": "linux",
    "assembly": "assembly",
}


def today() -> str:
    return dt.date.today().isoformat()


def load_json(path: str | None) -> dict[str, Any]:
    if path and path != "-":
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def slugify(text: str, max_len: int = 80) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s+#.-]+", "", text)
    text = text.replace("#", "sharp").replace("+", "p")
    text = re.sub(r"[\s_.-]+", "-", text).strip("-")
    return (text[:max_len].strip("-") or "finding")


def stable_id(doc: dict[str, Any]) -> str:
    question = doc.get("question", {}).get("normalized_question") or doc.get("question", {}).get("user_request") or ""
    urls = sorted(source.get("url", "") for source in doc.get("sources", []) if source.get("url"))
    payload = json.dumps({"question": question, "urls": urls}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def choose_bucket(doc: dict[str, Any]) -> str:
    question = doc.get("question", {})
    candidates = []
    candidates.extend(question.get("languages") or [])
    candidates.extend(question.get("platforms") or [])
    candidates.extend(question.get("runtimes") or [])
    for candidate in candidates:
        key = str(candidate).lower()
        if key in BUCKET_ALIASES:
            return BUCKET_ALIASES[key]
    return "mixed"


def yaml_list(values: list[Any]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(str(v)) for v in values) + "]"


def md_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


def source_table(sources: list[dict[str, Any]]) -> str:
    lines = [
        "| Source | Category | Weight | Untrusted | Status | URL |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for source in sources:
        title = md_escape(source.get("title") or source.get("source_id"))
        url = source.get("url") or ""
        link = f"[{title}]({url})" if url else title
        lines.append(
            f"| {link} | {md_escape(source.get('category'))} | {source.get('base_weight', '')} | {source.get('untrusted', '')} | {md_escape(source.get('screening_status'))} | {md_escape(url)} |"
        )
    return "\n".join(lines)


def solution_sections(solutions: list[dict[str, Any]]) -> str:
    if not solutions:
        return "_No candidate solutions recorded._"
    sections = []
    for solution in solutions:
        screening = solution.get("screening") or {}
        sections.append(
            "\n".join(
                [
                    f"### {md_escape(solution.get('id', 'solution'))}",
                    "",
                    f"- Summary: {md_escape(solution.get('summary'))}",
                    f"- Type: `{md_escape(solution.get('type'))}`",
                    f"- Status: `{md_escape(solution.get('status'))}`",
                    f"- Sources: {', '.join(f'`{md_escape(s)}`' for s in solution.get('source_ids', [])) or '_none_'}",
                    f"- Version constraints: {', '.join(md_escape(v) for v in solution.get('version_constraints', [])) or '_none_'}",
                    f"- Risks: {', '.join(md_escape(r) for r in solution.get('risks', [])) or '_none_'}",
                    "",
                    "**Screening**",
                    "",
                    f"- Authority: {md_escape(screening.get('authority'))}",
                    f"- Recency: {md_escape(screening.get('recency'))}",
                    f"- Version match: {md_escape(screening.get('version_match'))}",
                    f"- Reproducibility: {md_escape(screening.get('reproducibility'))}",
                    f"- Security: {md_escape(screening.get('security'))}",
                    f"- License: {md_escape(screening.get('license'))}",
                ]
            )
        )
    return "\n\n".join(sections)


def render_markdown(doc: dict[str, Any], finding_id: str, json_rel: str) -> str:
    question = doc.get("question", {})
    decision = doc.get("decision", {})
    application = doc.get("application", {})
    normalized = question.get("normalized_question") or question.get("user_request") or "Untitled finding"
    languages = question.get("languages") or []
    platforms = question.get("platforms") or []
    runtimes = question.get("runtimes") or []
    tags = ["a-hydrae-developing-skills", "resolved-finding"]
    tags.extend(slugify(v, 32) for v in languages + platforms + runtimes if v)
    selected = decision.get("selected_solution_id") or ""
    verification = application.get("verification") or []
    verified = bool(verification)

    frontmatter = [
        "---",
        f'id: "{finding_id}"',
        f'created: "{today()}"',
        f'updated: "{today()}"',
        f'status: "{"verified" if verified else "unverified"}"',
        f'question: "{normalized.replace(chr(34), chr(39))}"',
        f"languages: {yaml_list(languages)}",
        f"platforms: {yaml_list(platforms)}",
        f"runtimes: {yaml_list(runtimes)}",
        f'tags: {yaml_list(tags)}',
        "---",
        "",
    ]

    body = [
        f"# {normalized}",
        "",
        "## Question",
        "",
        f"- User request: {md_escape(question.get('user_request'))}",
        f"- Normalized technical question: {md_escape(normalized)}",
        f"- Languages: {', '.join(md_escape(v) for v in languages) or '_none_'}",
        f"- OS/runtime: {', '.join(md_escape(v) for v in platforms + runtimes) or '_none_'}",
        f"- Relevant versions: {', '.join(md_escape(v) for v in question.get('versions', [])) or '_none_'}",
        f"- Project constraints: {', '.join(md_escape(v) for v in question.get('project_constraints', [])) or '_none_'}",
        "",
        "## Sources",
        "",
        source_table(doc.get("sources", [])),
        "",
        "## Candidate Solutions",
        "",
        solution_sections(doc.get("candidate_solutions", [])),
        "",
        "## Decision",
        "",
        f"- Selected solution: `{md_escape(selected)}`" if selected else "- Selected solution: _not recorded_",
        f"- Rationale: {md_escape(decision.get('rationale'))}",
        f"- Decisive sources: {', '.join(f'`{md_escape(s)}`' for s in decision.get('decisive_source_ids', [])) or '_none_'}",
        f"- Resolved conflicts: {', '.join(md_escape(c) for c in decision.get('resolved_conflicts', [])) or '_none_'}",
        f"- Rejected options: {', '.join(md_escape(o) for o in decision.get('rejected_options', [])) or '_none_'}",
        "",
        "## Application",
        "",
        f"- Affected files: {', '.join(md_escape(v) for v in application.get('affected_files', [])) or '_none_'}",
        f"- Implementation notes: {md_escape(application.get('implementation_notes'))}",
        f"- Verification: {', '.join(md_escape(v) for v in verification) or '_not recorded_'}",
        f"- Residual limits: {', '.join(md_escape(v) for v in application.get('residual_limits', [])) or '_none_'}",
        "",
        "## Reuse",
        "",
        "- Reuse only if language, OS/runtime, versions, and constraints still match.",
        "- Re-run verification if the dependency, SDK, compiler, runtime, or OS version changed.",
        f"- Normalized JSON: [[{json_rel}]]",
        "",
    ]
    return "\n".join(frontmatter + body)


def ensure_index(index_path: Path) -> None:
    if index_path.exists():
        return
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("# Resolved Findings\n\n", encoding="utf-8")


def update_index(index_path: Path, note_rel: str, doc: dict[str, Any], finding_id: str) -> None:
    ensure_index(index_path)
    text = index_path.read_text(encoding="utf-8")
    question = doc.get("question", {})
    title = question.get("normalized_question") or question.get("user_request") or finding_id
    entry = f"- {today()} [[{note_rel}]] `{finding_id}` - {title}\n"
    if finding_id in text:
        return
    index_path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Persist an a-hydrae-developing-skills normalized finding into an Obsidian wiki.")
    parser.add_argument("--input", "-i", help="Input normalized JSON file, or '-' for stdin.")
    parser.add_argument("--wiki", default="wiki", help="Obsidian wiki root. Default: wiki")
    parser.add_argument("--bucket", help="Override resolved bucket, e.g. windows, python, cpp.")
    parser.add_argument("--title", help="Override note title/slug source.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing note with the same stable id.")
    parser.add_argument("--print-path", action="store_true", help="Print written note path.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    doc = load_json(args.input)
    wiki = Path(args.wiki)
    finding_id = stable_id(doc)
    question = doc.get("question", {})
    title = args.title or question.get("normalized_question") or question.get("user_request") or finding_id
    bucket = args.bucket or choose_bucket(doc)
    note_dir = wiki / "resolved" / bucket
    data_dir = wiki / "data" / "findings"
    note_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    note_path = note_dir / f"{slug}-{finding_id}.md"
    json_path = data_dir / f"{finding_id}.json"
    if note_path.exists() and not args.overwrite:
        print(f"Refusing to overwrite existing note: {note_path}", file=sys.stderr)
        return 2

    json_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json_rel = json_path.relative_to(wiki).with_suffix("").as_posix()
    note_path.write_text(render_markdown(doc, finding_id, json_rel), encoding="utf-8")
    note_rel = note_path.relative_to(wiki).with_suffix("").as_posix()
    update_index(wiki / "resolved" / "Index.md", note_rel, doc, finding_id)
    if args.print_path:
        print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
