# A Hydrae Developing Skills Wiki

This vault documents the design of `a-hydrae-developing-skills`: a source-grounded coding skill for agents.

The core idea is simple: when a user asks for code, the agent should first retrieve and weigh relevant technical sources, then implement. Official and primary sources are treated as contracts when they match the target version and environment. Community sources are useful as practical memory, but they must be screened before use.

## Main Notes

- [[01 Vision and Principles]]
- [[02 Skill Architecture]]
- [[03 Sources and Connectors]]
- [[04 Language and Platform Taxonomy]]
- [[05 Retrieval and Ranking]]
- [[06 Roadmap]]
- [[07 Open Decisions]]
- [[08 Vibe Coding Directives]]
- [[09 Output Normalizer]]
- [[10 Obsidian Persistence]]

## Project Thesis

The skill is not a static knowledge base. It is an operating protocol for research, screening, implementation, verification, and reuse.

It should:

- identify the language, OS, runtime, library, API, and version involved in a request;
- acquire information from live or indexed read-only sources;
- cite provenance when external knowledge influences an answer;
- prefer official documentation for API contracts and guaranteed behavior;
- use Stack Overflow, Reddit, GitHub repositories, and similar sources as practical signals;
- require explicit user authorization before adding persistent sources or parsers;
- distinguish documented facts, community observations, source-code evidence, and inference.

## Skill Name

`a-hydrae-developing-skills`
