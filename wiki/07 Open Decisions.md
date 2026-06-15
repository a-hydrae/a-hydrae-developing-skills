# Open Decisions

## Scope

The skill currently focuses on source-grounded coding for system, runtime, package, and platform-sensitive development. It may later become broader, but the first useful target is coding where current or authoritative evidence matters.

## Skill Location

The repository is the source of truth. Runtime installations should receive copied or symlinked skill directories.

## API vs Browsing

Preferred order:

1. official API when it exposes the needed technical content;
2. direct URL parsing for authoritative documentation;
3. targeted web/search lookup when no technical-docs API is available;
4. community APIs for practical signals.

Avoid aggressive scraping and avoid storing large mirrored corpora.

## Self-Extension

The agent may propose new sources or parsers, but persistent additions require explicit user approval.

Each persistent addition needs:

- source category;
- initial weight;
- scope;
- acquisition method;
- parser plan;
- policy/rate-limit notes;
- risks;
- screening rules.

## Reddit

Reddit can surface practical developer experience, regressions, and tooling problems. It is never normative.

Open questions:

- whether to use official API credentials;
- which subreddits are admissible;
- how to represent thread quality and age.

## Stack Overflow

Stack Exchange is a strong first community connector because it has structured metadata, tags, accepted answers, scores, and stable APIs. License and attribution still matter.

## Stronger Enforcement

Current enforcement is workflow-level. A future version could refuse to persist or apply findings whose sources remain `needs-screening` or whose `untrusted` evidence has no verification record.
