# Output Normalizer

Use this shape whenever external sources influence a coding answer or patch.

## Markdown Shape

```markdown
## Question

- User request:
- Normalized technical question:
- Languages:
- OS/runtime:
- Relevant versions:
- Project constraints:

## Sources Consulted

| Source | URL | Category | Base weight | Untrusted | Scope match | Freshness | Status |
| --- | --- | --- | ---: | --- | --- | --- | --- |

## Candidate Solutions

### Solution A

- Summary:
- Sources:
- Type: documented/community-workaround/source-code/inferred
- Pros:
- Cons:
- Risks:
- Version/OS constraints:
- Screening:
- Status:

## Decision

- Selected solution:
- Rationale:
- Decisive sources:
- Resolved conflicts:
- What not to use and why:

## Application

- Affected files:
- Implementation notes:
- Verification:
- Residual limits:
```

## JSON Core

The JSON core is stable. Source-specific extras go under `extensions` and must be declared in `extension_registry` when persisted.

```json
{
  "question": {
    "user_request": "",
    "normalized_question": "",
    "languages": [],
    "platforms": [],
    "runtimes": [],
    "versions": [],
    "project_constraints": []
  },
  "sources": [],
  "candidate_solutions": [],
  "decision": {
    "selected_solution_id": "",
    "rationale": "",
    "decisive_source_ids": [],
    "resolved_conflicts": [],
    "rejected_options": []
  },
  "application": {
    "affected_files": [],
    "implementation_notes": "",
    "verification": [],
    "residual_limits": []
  },
  "extension_registry": []
}
```

Rules:

- Do not use community evidence without screening.
- Treat any source marked `untrusted: true` as unsafe for direct code reuse. Verify behavior, security, license, and version fit before applying code or patterns.
- Public code from GitHub, Stack Exchange, Reddit, blogs, package registries, and unaffiliated repositories is `untrusted` by default. Official vendor or project documentation for the target language/platform is trusted when the source, version, and scope match the task.
- Do not copy community snippets blindly; extract the pattern and cite when needed.
- Record conflicts between sources.
- Mark missing official confirmation as a residual limit.
- Keep the core stable; add parser-specific metadata to `extensions`.
- Persist reusable, verified findings with `scripts/persist_finding.py`; do not persist unreviewed acquisition output as if it were solved knowledge.
