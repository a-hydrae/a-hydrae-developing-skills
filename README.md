# A Hydrae Developing Skills

A source-grounded coding skill for agents that need to write better code by checking current, platform-specific, and community-tested evidence before implementing.

The skill is designed for development tasks involving APIs, SDKs, runtimes, operating systems, compilers, package ecosystems, and community-known workarounds. It starts with Python, C, C++, C#, Assembly, Windows, and Linux.

## Why

Coding agents often rely on generic prior knowledge. That is risky when the answer depends on a specific OS version, API contract, runtime behavior, compiler detail, package release, or security boundary.

This skill makes the agent:

- classify the technical target before coding;
- retrieve read-only evidence from official, primary, and community sources;
- assign source weights instead of treating all results equally;
- mark public code as untrusted by default;
- normalize findings into a reusable structure;
- persist verified solutions in an Obsidian-compatible wiki.

## Source Model

Sources are weighted by authority and screened before use.

| Source type | Base weight | Use |
| --- | ---: | --- |
| Vendor/project official docs | 100 | API contracts and documented behavior |
| Standards, RFCs, PEPs, specs | 95 | Normative semantics |
| Release notes and changelogs | 90 | Compatibility and breaking changes |
| Upstream source repository outside GitHub | 85 | Primary implementation evidence |
| Man pages, kernel docs, SDK headers | 80 | OS, libc, kernel, SDK details |
| Stack Overflow accepted/high-score | 55 | Candidate community evidence |
| GitHub repositories/code examples | 55 | Candidate source-code evidence |
| Technical Reddit thread | 35 | Weak practical signal |
| Personal blog | 30-70 | Depends on author/date/code quality |
| Anonymous snippet | 10 | Do not use without confirmation |

When official or primary sources conflict with community evidence, the official/primary source wins if it matches the target version and environment.

## Untrusted Code Rule

Every source record includes an `untrusted` flag.

Public code and community sources are `untrusted: true` by default, including GitHub, Stack Exchange, Reddit, blogs, package registries, and unaffiliated repositories.

`untrusted: true` means code, snippets, commands, and implementation patterns must not be copied or executed directly. The agent must verify security, license, version fit, and behavior first.

Official vendor or project documentation for the target language/platform is trusted when the source, version, and scope match the task. Examples include Microsoft Learn for Windows APIs and Python documentation for Python runtime or standard-library behavior.

## GitHub Behavior

The GitHub provider intentionally excludes issues and pull requests from normal results because they are noisy for code generation.

Default GitHub acquisition uses repository search:

- endpoint: GitHub repository search API;
- sort: stars descending;
- output: `owner/repo` results;
- status: `needs-screening`;
- trust: `untrusted: true`.

Example:

```bash
python3 a-hydrae-developing-skills/scripts/source_search.py \
  --provider github \
  --query "windows service" \
  --limit 5 \
  --pretty
```

## Screening And Enforcement

Screening is performed by the agent using the rules in `references/source-policy.md` and `references/output-normalizer.md`.

Current enforcement is workflow-level, not a hard sandbox:

- `source_search.py` labels risky material with fields such as `untrusted: true` and statuses such as `needs-screening`, `needs-official-confirmation`, `version-bound`, or `reject`;
- `SKILL.md` instructs the agent not to implement from untrusted or unscreened material;
- normalized output must include a `decision` section before a finding becomes reusable;
- `persist_finding.py` is intended for verified findings, not raw acquisition output.

This means the flag is a guardrail and audit hook, not a cryptographic or runtime control. A stronger future implementation could enforce this mechanically by refusing to persist, apply, or patch from sources whose status is still `needs-screening` or whose `untrusted` evidence lacks an explicit verification record.

For now, a GitHub result with:

```json
{
  "untrusted": true,
  "screening_status": "needs-screening"
}
```

must be treated as a lead to inspect, not as code to copy. The agent should only use it after documenting why it is applicable, how license/security/version risks were checked, and what verification was run.

## Layout

```text
a-hydrae-developing-skills/
  SKILL.md
  agents/openai.yaml
  references/
    source-policy.md
    platform-routing.md
    output-normalizer.md
    persistence-policy.md
    vibe-coding-directives.md
    source-catalog.json
  scripts/
    source_search.py
    persist_finding.py
scripts/
  release_test.py
tests/
wiki/
```

## Install

Copy or symlink the skill directory into your agent's skill directory:

```bash
cp -a a-hydrae-developing-skills ~/.codex/skills/a-hydrae-developing-skills
```

For Hermes-style installations, copy the same directory into the active Hermes skills directory used by your profile.

## Activation

Agents should activate this skill when a coding task depends on current, platform-specific, version-sensitive, or community-known technical knowledge.

Typical triggers include:

- Windows, Linux, .NET, Python, C, C++, C#, Assembly, SDK, API, compiler, runtime, package, or deployment questions;
- security-sensitive code, unsafe APIs, permissions, races, injection, or trust boundaries;
- errors, regressions, undocumented behavior, compatibility issues, or workarounds;
- requests that would normally benefit from checking Microsoft Learn, Python docs, man pages, Stack Overflow, GitHub repositories, Reddit, PyPI, or similar sources.

The skill can be selected automatically from the `description` field in `SKILL.md`, or invoked explicitly:

```text
Use $a-hydrae-developing-skills to research this before coding.
```

## Usage

Run a source acquisition query:

```bash
python3 a-hydrae-developing-skills/scripts/source_search.py \
  --provider direct-url \
  --url https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew \
  --query "CreateFileW FILE_FLAG_OVERLAPPED" \
  --language C++ \
  --platform Windows \
  --pretty
```

Use Stack Exchange:

```bash
python3 a-hydrae-developing-skills/scripts/source_search.py \
  --provider stackexchange \
  --query "python asyncio TaskGroup ExceptionGroup" \
  --language Python \
  --pretty
```

Use PyPI metadata:

```bash
python3 a-hydrae-developing-skills/scripts/source_search.py \
  --provider pypi \
  --pypi-package requests \
  --language Python \
  --pretty
```

Persist a verified finding into the wiki:

```bash
python3 a-hydrae-developing-skills/scripts/persist_finding.py \
  --input finding.json \
  --wiki wiki
```

## Normalized Output

Acquisition emits a JSON document with:

- `question`;
- `sources`;
- `candidate_solutions`;
- `decision`;
- `application`;
- `extension_registry`.

The model should not treat acquisition output as a final answer. It must screen sources, resolve conflicts, choose a solution, implement only when appropriate, and verify the result.

### `extension_registry`

`extension_registry` documents extra fields discovered by a provider or parser without changing the stable JSON core.

Provider-specific metadata goes under `source.extensions`. Each field should be declared in `extension_registry` with:

- `field`: field name;
- `type`: expected value type;
- `scope`: where the field applies, such as `source`, `snippet`, `solution`, `decision`, or `application`;
- `introduced_by_source_id`: provider/source that introduced it;
- `reason`: why the field is useful;
- `stability`: usually `experimental` until promoted;
- `approved`: whether the field is accepted as stable schema.

Example GitHub fields include `repository_full_name`, `language`, `stars`, `forks`, `license`, and `pushed_at`. Example Stack Exchange fields include accepted answer id, score, tags, and answer count.

The registry lets the skill evolve without silently mutating the core schema.

## Vibe-Coding Extensions

The skill can propose new sources, parsers, and output fields during work, but persistent changes require explicit user authorization.

This is intended for controlled self-extension: the agent may notice that a new documentation site, package registry, forum, or vendor source would be useful, but it must ask before adding it to the persistent catalog or writing a reusable parser.

Each proposed source must include:

- URL base;
- category;
- scope;
- initial weight;
- access method;
- parser plan;
- rate-limit/policy notes;
- risks.

Generated parsers must be:

- read-only;
- limited to the approved domain/source;
- explicit about endpoints, selectors, and extracted fields;
- rate-limited;
- tested on sample pages when possible;
- unable to submit forms, comment, vote, publish, log in, or use personal accounts unless separately authorized.

If a parser finds a useful field that is not in the normalizer, the field should first be emitted in `extensions` and declared in `extension_registry`. It should only become a stable field after review.

## Test

```bash
make test
```

Run the release loop:

```bash
make release-test
```

Run live acquisition checks:

```bash
make release-test-live
```

## Status

Prototype. The skill is usable for source-grounded coding workflows, but source parsers are intentionally lightweight and conservative. Public-code reuse must always pass review.
