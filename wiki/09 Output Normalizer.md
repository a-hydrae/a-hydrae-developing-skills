# Output Normalizer

## Purpose

Any agent request that uses external sources should produce normalized output. The format makes clear:

- the technical question;
- consulted sources;
- candidate solutions;
- source weights and screening;
- selected decision;
- verification.

The format has a stable core and extensible fields. Source-specific metadata belongs in `extensions` and must be declared in `extension_registry`.

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

## Rules

- Do not use community evidence without screening.
- Treat `untrusted: true` as unsafe for direct code reuse.
- Public code from GitHub, Stack Exchange, Reddit, blogs, package registries, and unaffiliated repositories is untrusted by default.
- Official vendor/project documentation for the target language/platform is trusted when source, version, and scope match.
- Do not copy community snippets blindly; extract the pattern, review license, and cite when needed.
- Record conflicts between sources.
- Mark missing official confirmation as a residual limit.
- Persist only reusable, verified findings.

## `extension_registry`

`extension_registry` documents extra provider/parser fields without changing the stable core schema.

Each entry should include:

- `field`;
- `type`;
- `scope`;
- `introduced_by_source_id`;
- `reason`;
- `stability`;
- `approved`.

Examples:

| Field | Scope | Type | Use |
| --- | --- | --- | --- |
| `repository_full_name` | source | string | GitHub owner/repo identity |
| `stars` | source | integer | GitHub popularity signal |
| `accepted_answer_id` | source | string | Stack Exchange accepted answer link |
| `answer_score` | source/snippet | integer | Community signal |
| `package_version` | source/solution | string | Package applicability |
| `last_verified_against` | solution | string | Local verification version/date |

New stable fields require review. During a task, experimental fields may stay under `extensions` with `approved: false`.
