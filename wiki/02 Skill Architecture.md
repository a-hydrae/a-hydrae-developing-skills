# Skill Architecture

## Shape

The skill should keep `SKILL.md` concise and move repeatable behavior into reference files and scripts.

```text
a-hydrae-developing-skills/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── source-policy.md
│   ├── platform-routing.md
│   ├── vibe-coding-directives.md
│   ├── output-normalizer.md
│   ├── persistence-policy.md
│   └── source-catalog.json
└── scripts/
    ├── source_search.py
    └── persist_finding.py
```

## Workflow

1. **Classify the request**
   - Language: Python, C, C++, C#, Assembly, shell, mixed.
   - Target: Windows, Linux, .NET, Python runtime, compiler/toolchain, package ecosystem.
   - Risk: version-sensitive, security-sensitive, performance-sensitive, undefined-behavior-prone, packaging-sensitive.

2. **Select sources**
   - Official sources for API contracts and documented behavior.
   - Primary sources for implementation behavior, release changes, and source-level details.
   - Community sources for known errors, workarounds, regressions, and practical examples.

3. **Acquire read-only evidence**
   - Prefer APIs where they exist and are suitable.
   - Use targeted search or direct URL parsing where documentation APIs are incomplete.
   - Never write to external platforms.

4. **Rank and screen**
   - Weight source authority.
   - Check version, freshness, applicability, reproducibility, license, and security.
   - Mark public code and community evidence as `untrusted` until verified.

5. **Normalize**
   - Emit the normalized shape: question, sources, candidate solutions, decision, application, extension registry.

6. **Implement**
   - Apply code only after relevant evidence has been weighed.
   - Verify with tests, builds, local reproduction, or state residual limits.

7. **Persist verified findings**
   - Save only curated, verified findings in the Obsidian wiki.
   - Do not persist raw acquisition output or smoke-test artifacts as solved knowledge.

## Boundary

This skill should not become a generic RAG engine. It is an operating protocol for agents: retrieve sources, evaluate them, then write code.

See [[08 Vibe Coding Directives]], [[09 Output Normalizer]], and [[10 Obsidian Persistence]].
