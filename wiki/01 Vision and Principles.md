# Vision and Principles

## Problem

Coding agents often know generic patterns, but real software work depends on unstable details: SDK versions, OS behavior, compiler flags, ABI rules, permissions, edge cases, known bugs, official examples, and community workarounds.

Before agentic coding, developers did not solve everything from memory. They checked official docs, Stack Overflow, issue trackers, forums, blogs, and source code. This skill gives an agent a disciplined version of that workflow.

## Principles

- **Sources before code**: for unstable APIs, OS behavior, packages, security boundaries, and toolchains, retrieve evidence before implementation.
- **Official docs as the base layer**: vendor/project docs, language docs, standards, SDK docs, and man pages have priority when version and target match.
- **Community as practical memory**: Stack Overflow, Reddit, forums, and repositories help discover known errors, workarounds, regressions, and real-world caveats.
- **Mandatory weighting and screening**: every source must be weighted for authority, freshness, version match, reproducibility, license, and security.
- **Read-only acquisition**: the skill searches and reads external platforms; it must not publish, vote, comment, log in, or modify remote content.
- **No massive mirrors**: do not download full documentation corpora. Keep only catalogs, metadata, short snippets, temporary cache, and curated findings.
- **Provenance and citations**: any externally derived claim should keep source links and confidence context.
- **Facts and heuristics are separate**: an API contract is not equivalent to a Reddit comment, even when both are useful.

## Anti-Patterns

- Mirroring large documentation sets just because they are available.
- Mixing official documentation and community opinions without labels.
- Treating Reddit or Stack Overflow as normative.
- Copying community snippets without license review and attribution.
- Applying a community answer that conflicts with official documentation without explaining the conflict.
- Assuming Windows, Linux, Python, .NET, C++, or package ecosystems are stable over time.
