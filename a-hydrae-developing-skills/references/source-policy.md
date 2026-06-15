# Source Policy

## Authority Weights

| Source type | Base weight | Rule |
| --- | ---: | --- |
| Vendor/project official docs | 100 | Apply as contract when version and target match |
| Standards, RFCs, PEPs, specs | 95 | Apply as normative; check implementation details |
| Release notes and changelogs | 90 | Apply for compatibility, breaking changes, and deprecations |
| Upstream source repository outside GitHub | 85 | Primary evidence; verify branch/tag |
| Man pages, kernel docs, SDK headers | 80 | Primary evidence; verify OS/distro/SDK version |
| Stack Overflow accepted/high-score | 55 | Candidate solution; screen before use |
| GitHub repositories/code examples | 55 | Candidate source-code evidence; exclude issues/PRs from normal search and screen before use |
| Technical Reddit thread | 35 | Practical weak signal; never normative |
| Personal blog | 30-70 | Depends on author, date, code, reputation |
| Anonymous snippet | 10 | Do not apply without independent confirmation |

## Precedence

When a current official/primary source conflicts with community evidence, prefer the official/primary source. Use community evidence only to explain workarounds, bugs, version differences, or undocumented observed behavior, and label it as such.

When official docs are old, incomplete, or do not cover the requested environment, seek primary evidence: release notes, upstream source, maintainer issue, SDK header, man page, or local test.

## Untrusted Code Flag

Every source record carries `untrusted`.

- `untrusted: true` means code, snippets, commands, and implementation patterns from the source must not be copied or executed directly. Verify security, license, version fit, and behavior first.
- Public code/community sources are untrusted by default: GitHub, Stack Exchange, Reddit, blogs, PyPI/package metadata and linked source, and unaffiliated repositories.
- Official vendor or project documentation for the target language/platform is trusted when the source, version, and scope match the task.
- The flag does not replace source weight. A source can have useful evidence and still be untrusted for code reuse.

## Community Screening

Before using a community solution, check:

- date: post and edits are compatible with the current version;
- version: language, runtime, framework, OS, compiler, package match;
- consensus: accepted answer, score, critical comments, competing answers, maintainer presence;
- reproducibility: minimal example or local test is possible;
- conflict: no contradiction with official docs or upstream source unless explained;
- license: do not copy snippets blindly; cite when needed;
- security: no unsafe bypasses, injection, race, permission, or trust boundary issue;
- generality: solves the current problem, not only the author's special case.

Screening statuses:

- `accepted`: can be used as evidence after verification;
- `needs-official-confirmation`: find official/primary backing first;
- `version-bound`: apply only to matching version/OS/runtime;
- `workaround-only`: use only if the real issue matches and no better official path exists;
- `reject`: do not use.
