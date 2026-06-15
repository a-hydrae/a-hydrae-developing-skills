# Obsidian Persistence

## Purpose

The wiki can store verified findings so agents can reuse solved technical decisions without navigating again.

It is not a documentation cache. It is a curated memory of resolved problems.

## Layout

```text
wiki/
├── resolved/
│   ├── Index.md
│   ├── python/
│   ├── windows/
│   ├── linux/
│   ├── cpp/
│   ├── csharp/
│   ├── assembly/
│   └── mixed/
└── data/
    └── findings/
```

- `resolved/`: human-readable Markdown notes.
- `data/findings/`: normalized JSON for tools.
- `resolved/Index.md`: chronological finding index.

## Save Criteria

Save a finding only when:

- the question is likely reusable;
- a solution was selected;
- sources were weighed and screened;
- there is a local verification, test, build, or explicit residual limit;
- language, OS/runtime, package, compiler, API, and version constraints are clear.

Do not save:

- raw search output;
- acquisition-only smoke tests;
- findings without decisions;
- unverified community snippets;
- private data, secrets, internal paths, or non-generalizable details.

## Reuse

Before navigating again:

1. search the wiki for API, error, package, or normalized question;
2. check language, OS/runtime, and versions;
3. check staleness;
4. reuse only if constraints match;
5. update the note if new evidence changes the decision.

## Script

```bash
python3 a-hydrae-developing-skills/scripts/persist_finding.py \
  --input finding.json \
  --wiki wiki \
  --print-path
```

Typical pipeline:

```bash
python3 a-hydrae-developing-skills/scripts/source_search.py ... --pretty > /tmp/finding.json
# Agent completes decision and verification in the normalized JSON.
python3 a-hydrae-developing-skills/scripts/persist_finding.py --input /tmp/finding.json --wiki wiki
```

## Public Repository Rule

The public repository should not include task-specific persisted findings. Keep `wiki/resolved/Index.md` and templates, but leave user/project-specific findings local unless intentionally curated for publication.
