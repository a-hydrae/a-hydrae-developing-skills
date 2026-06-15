# Vibe Coding Directives

## Purpose

Vibe-coding directives let the agent propose new sources, parsers, and output fields when useful technical sources appear during work.

Autonomy is limited. The agent may discover and propose. Persistent registration requires explicit user authorization.

## When to Propose a Source

Propose a new source when it:

- appears repeatedly for a language, OS, framework, or error;
- contains official or primary information not covered by the catalog;
- includes maintainer or expert technical discussion;
- provides reproducible examples, benchmark data, or relevant implementation details;
- covers a niche not served by existing sources.

Do not propose a source when it:

- mirrors documentation already covered;
- requires personal login, paywall bypass, or aggressive scraping;
- has non-citable or low-quality content;
- contradicts higher-authority sources without version context.

## Approval Request

Before adding a persistent source, show:

```text
Source proposed:
- Name:
- Base URL:
- Category:
- Initial weight:
- Language scopes:
- OS/runtime scopes:
- Layer/topic scopes:
- Why it is useful:
- Acquisition method:
- Policy/rate-limit notes:
- Parser plan:
- Sample pages:
- Risks:
```

If the user does not approve, the source may be used only in the current task as cited evidence.

## Suggested Initial Weights

| Category | Initial weight | Notes |
| --- | ---: | --- |
| `official` | 90-100 | Vendor/project docs, standards, official manuals |
| `primary` | 75-90 | Upstream source, release notes, SDK headers |
| `vendor-forum` | 55-75 | Official forums with staff or maintainers |
| `community` | 35-60 | Stack Overflow-like forums, Reddit, technical forums |
| `blog` | 30-70 | Depends on author, date, evidence, reputation |
| `benchmark` | 40-75 | Useful only if reproducible and environment-compatible |

Weight alone is not enough. Applicability, date, version, and conflicts must still be screened.

## Generated Parser Rules

A generated parser must be:

- read-only;
- limited to the approved domain/source;
- explicit about endpoints, selectors, and extracted fields;
- rate-limited;
- tested on sample pages when possible;
- unable to submit forms, comment, vote, publish, log in, or use personal accounts unless separately authorized.

## Output Fields

If a parser finds useful metadata not represented in the normalizer, the field must first go under `extensions` and be declared in `extension_registry`.

Do not change the stable core schema without authorization.

## Demotion or Removal

The agent should propose reducing weight or removing a source when it:

- frequently returns obsolete results;
- changes access policy;
- becomes too fragile to parse;
- is replaced by a better official source;
- contains low-quality or unverifiable material.
