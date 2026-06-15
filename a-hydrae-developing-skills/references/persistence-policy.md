# Persistence Policy

Persist only reusable technical findings that have been screened and, ideally, verified locally. The Obsidian wiki is a curated memory of solved topics, not a mirror of external documentation.

## What to Persist

- Normalized technical question.
- Selected solution and rationale.
- Sources used, with categories and weights.
- Community screening results.
- Verification performed.
- Version, OS, runtime, package, compiler, or API constraints.
- Residual limits and known invalid approaches.

## What Not to Persist

- Whole documentation pages.
- Raw Stack Overflow/Reddit text dumps.
- Unverified snippets.
- Secrets, tokens, private repository details, personal data.
- Findings that only applied to a one-off local state unless clearly marked.

## Reuse Rule

Before browsing again, search the wiki for:

- exact API/function/package/error;
- language and OS/runtime tags;
- normalized question slug;
- source URLs.

Reuse a finding only if:

- the question matches closely;
- version constraints still apply;
- verification is present or current task can re-verify cheaply;
- no source is stale for the current request.

If a reused finding is stale or incomplete, update the note rather than creating a duplicate.

## Obsidian Layout

Recommended wiki paths:

```text
wiki/
├── resolved/
│   ├── Index.md
│   ├── python/
│   ├── windows/
│   ├── linux/
│   ├── cpp/
│   ├── csharp/
│   └── mixed/
└── data/
    └── findings/
```

Markdown notes are for human reuse. JSON files under `wiki/data/findings/` are for tools.
