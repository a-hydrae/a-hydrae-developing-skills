---
name: a-hydrae-developing-skills
description: Source-grounded coding workflow for software development tasks that require current or platform-specific knowledge. Use when implementing, debugging, reviewing, or designing code involving APIs, SDKs, runtimes, operating systems, compilers, package versions, security-sensitive behavior, or community-known workarounds. The skill retrieves and weighs official, primary, and community sources such as Microsoft Learn/MSDN, Python docs, cppreference, man pages, Stack Overflow, Reddit, GitHub, and package registries before applying code changes.
---

# A Hydrae Developing Skills

## Core Rule

Do not treat retrieved information equally. Apply official and primary sources as technical contracts when version and target match. Treat Stack Overflow, Reddit, blogs, and similar sources as candidate evidence that must pass screening before use.

## Workflow

1. Classify the request:
   - language: Python, C, C++, C#, Assembly, shell, mixed;
   - target: Windows, Linux, .NET, Python runtime, compiler/toolchain, package ecosystem;
   - risk: version-sensitive, security-sensitive, performance-sensitive, undefined-behavior-prone, packaging-sensitive.
2. Plan retrieval:
   - prefer official docs for API contracts;
   - use primary sources for release changes, source behavior, issue status, and implementation details;
   - use community sources for known errors, workarounds, regressions, and practical examples.
3. Acquire read-only data:
   - use `scripts/source_search.py` for Stack Exchange, GitHub, PyPI, and direct URL acquisition;
   - do not publish, vote, comment, log in, bypass paywalls, or scrape aggressively.
4. Rank and screen:
   - read `references/source-policy.md` when evaluating source authority;
   - community findings require date, version, consensus, reproducibility, license, and security screening.
5. Normalize:
   - use `references/output-normalizer.md` for the result shape;
   - include question, sources, candidate solutions, decision, and verification.
6. Implement:
   - apply code changes only after the relevant evidence has been weighed;
   - verify with tests, builds, local reproduction, or state the residual limit.
7. Persist reusable findings:
   - when a solution is selected and verified, use `scripts/persist_finding.py` to store the normalized finding in the Obsidian wiki;
   - persist only curated findings, not raw documentation mirrors or unverified community snippets;
   - check existing wiki notes before re-querying external sources for the same problem.

## Source Expansion

If a useful source is not in the catalog, propose it to the user before persisting it. Include URL base, category, scopes, initial weight, why it is useful, acquisition method, parser plan, policy/rate-limit notes, and risks. See `references/vibe-coding-directives.md`.

## Output Expectations

When retrieval affects an answer or patch, include:

- normalized technical question;
- authoritative sources and community sources separately;
- candidate solutions found;
- screening result for each non-official solution;
- final decision and why;
- verification performed or not performed.

## Resources

- `references/source-policy.md`: weights, precedence, and community screening.
- `references/platform-routing.md`: multi-scope source routing by language, OS, runtime, layer, and topic.
- `references/output-normalizer.md`: Markdown and JSON result formats.
- `references/persistence-policy.md`: Obsidian reuse and persistence rules.
- `references/vibe-coding-directives.md`: controlled source/parser/schema expansion.
- `references/source-catalog.json`: initial source catalog.
- `scripts/source_search.py`: read-only acquisition prototype.
- `scripts/persist_finding.py`: persist verified findings to an Obsidian wiki.
