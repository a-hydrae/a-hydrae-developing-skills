# Vibe Coding Directives

The agent may discover and propose new sources, parsers, and output fields. Persistence requires explicit user authorization.

## New Source Proposal

Show this before adding a source to the catalog:

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

Do not persist sources that require personal login, bypass paywalls, ignore policy/robots, or cannot be cited transparently.

## Parser Rules

Generated parsers must be:

- read-only;
- limited to the approved domain/source;
- explicit about endpoint, selectors, and extracted fields;
- rate-limited;
- tested on sample pages when possible;
- unable to submit forms, comment, vote, publish, or authenticate with personal accounts unless separately authorized.

If a parser finds useful metadata not in the normalizer, put it in `extensions` for the current task and propose a stable field before persistence.
