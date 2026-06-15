# Retrieval and Ranking

## Mental Model

The skill should produce a small technical review: this is the normative source, these are the community caveats, this is the selected implementation path, and this is how it was verified.

## Query Planning

For each request:

1. extract APIs, symbols, error messages, versions, OS, runtime, and toolchain;
2. build a small set of targeted queries;
3. search the most authoritative domain first;
4. search community sources only when prior developer experience is likely useful;
5. avoid broad searches when a direct reference exists.

Examples:

- Windows API: `site:learn.microsoft.com CreateFileW FILE_FLAG_OVERLAPPED`
- .NET: `site:learn.microsoft.com dotnet ProcessStartInfo UseShellExecute`
- Python: `site:docs.python.org asyncio TaskGroup Python 3.13`
- Linux: `site:man7.org epoll edge triggered`

## Ranking

Ranking separates two decisions:

1. source authority in the abstract;
2. applicability to the current request.

Indicative score:

```text
score =
  authority_weight
  + version_match
  + recency
  + specificity
  + reproducibility
  + community_consensus
  - contradiction_penalty
  - license_risk
  - ambiguity
  - outdated_signal
```

## Authority Weights

| Source type | Base weight | Rule |
| --- | ---: | --- |
| Vendor/project official docs | 100 | Apply as contract when version and target match |
| Standards, RFCs, PEPs, specs | 95 | Normative; still check implementation details |
| Release notes and changelogs | 90 | Compatibility, breaking changes, deprecations |
| Upstream source repository outside GitHub | 85 | Primary evidence; verify branch/tag |
| Man pages, kernel docs, SDK headers | 80 | Primary or official-like; verify OS/distro/SDK version |
| Stack Overflow accepted/high-score | 55 | Candidate solution; screen before use |
| GitHub repositories/code examples | 55 | Candidate code evidence; exclude issues/PRs by default |
| Technical Reddit thread | 35 | Weak practical signal |
| Personal blog | 30-70 | Depends on author, date, code, reputation |
| Anonymous snippet | 10 | Do not use without independent confirmation |

## Precedence

When community evidence conflicts with current official or primary evidence, the official/primary source wins if it matches the target environment.

When official docs are old, incomplete, or do not cover the requested environment, seek primary evidence: release notes, upstream source, SDK headers, man pages, or local tests.

## Untrusted Flag

Each source must include `untrusted`.

- `untrusted: true`: do not copy or execute code/snippets/commands without reviewing security, license, version fit, and behavior.
- Public code and community sources are untrusted by default: GitHub, Stack Exchange, Reddit, blogs, package registries, and unaffiliated repositories.
- Official vendor/project documentation for the target language or platform is trusted when source, version, and scope match.
- The flag is separate from source weight. A source may be useful evidence and still unsafe for direct code reuse.

## Screening

Before using community or public-code evidence, check:

- date and update history;
- language/runtime/framework/OS/compiler/package version match;
- consensus and critical comments;
- maintainer or upstream involvement;
- reproducibility through a minimal test or primary source;
- conflicts with higher-authority sources;
- license and attribution requirements;
- security implications;
- whether the solution generalizes beyond the original case.

Statuses:

| Status | Action |
| --- | --- |
| `accepted` | Use only after verification or authoritative support |
| `needs-official-confirmation` | Find official/primary backing before implementation |
| `needs-screening` | Inspect and verify before use |
| `version-bound` | Apply only to matching versions |
| `workaround-only` | Use only when the exact issue matches and no better path exists |
| `reject` | Do not use |

## Required Output

When retrieval affects a coding answer, include:

- normalized technical question;
- source links;
- candidate solutions;
- screening for each non-official source;
- final decision and rationale;
- official vs community distinction;
- version/date notes where relevant;
- implementation or patch;
- verification performed or residual limits.

Use [[09 Output Normalizer]] for persistent or tool-consumed findings.

## Cache

Cache should be local, small, and temporary:

- short TTL for pages and query results;
- key by query, source, date, language, and version;
- store metadata and short snippets, not full documentation mirrors;
- invalidate for latest/today/security/version-specific requests.
