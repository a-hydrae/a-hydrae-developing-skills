# Roadmap

## Phase 0 - Design

- [x] Create Obsidian wiki.
- [x] Define vision and principles.
- [x] Define initial sources.
- [x] Define skill architecture.
- [x] Choose final skill name.
- [x] Keep repository source and install copies for agent runtimes.

## Phase 1 - Minimal Skill

- [x] Create skill directory with `SKILL.md`.
- [x] Write source policy.
- [x] Write platform routing.
- [x] Write vibe-coding directives.
- [x] Write output normalizer.
- [x] Write persistence policy.
- [x] Validate with skill validator.

## Phase 2 - Lightweight Connectors

- [x] Add `source_search.py` with pluggable providers.
- [x] Add Stack Exchange API provider.
- [x] Add direct URL provider for official docs.
- [x] Add GitHub repository search provider.
- [x] Add Reddit public search provider.
- [x] Add PyPI JSON API provider.
- [x] Add extensible source catalog.
- [ ] Add short TTL cache.
- [ ] Add stronger source-specific parsers where justified.

## Phase 3 - Ranking and Synthesis

- [x] Normalize acquisition output.
- [x] Add `untrusted` flag.
- [x] Add `extension_registry`.
- [x] Persist verified findings to Obsidian.
- [ ] Add mechanical enforcement for unscreened/untrusted findings.
- [ ] Add ranking script separate from acquisition.
- [ ] Expand tests with realistic Windows, Linux, Python, C++, and .NET tasks.

## Phase 4 - Hardening

- [ ] License and citation policy review.
- [ ] Rate limiting and robots/policy compliance review.
- [ ] Credential handling policy.
- [ ] User approval workflow for persistent sources/parsers.
- [ ] Staleness policy for persisted findings.
- [ ] Measure whether the skill reduces coding errors or hallucinated APIs.
