# Sources and Connectors

## Strategy

Use three source tiers:

1. **Official/normative**: vendor or project documentation.
2. **Primary technical evidence**: standards, release notes, upstream source, SDK headers, man pages.
3. **Community evidence**: Stack Overflow, Reddit, blogs, forums, and public repositories.

Sources can cover multiple languages, platforms, runtimes, layers, and topics. Routing should not be modeled as a one-to-one `language -> source` map.

## Initial Sources

| Source | Language Scope | OS/Runtime Scope | Access | Use | Treatment |
| --- | --- | --- | --- | --- | --- |
| Microsoft Learn | C#, C++, PowerShell, mixed | Windows, .NET, Azure | Direct URL/search | API contracts, official examples, version notes | Official when target and version match |
| Python docs, PEPs | Python, C extensions | Cross-platform Python | Direct URL/search | Standard library, language/runtime behavior | Official |
| cppreference, compiler docs | C, C++ | Cross-platform, compiler-specific | Direct URL/search | Language/library semantics and implementation details | Strong reference; distinguish standard vs compiler behavior |
| man7.org, kernel docs, distro docs | C, C++, shell, Python, mixed | Linux, libc, kernel/userspace | Direct URL/search | Syscalls, errno, signals, filesystems, process behavior | Primary or official-like; verify distro/kernel version |
| Stack Exchange API | Many | Cross-platform | API | Q&A, accepted answers, high-signal historical debugging | Candidate evidence; screening required |
| Reddit | Many | Cross-platform | Public JSON/API or search | Real-world experience and weak signals | Never normative; severe screening |
| GitHub repositories | Any | Any | Repository search/direct URL | Code examples, libraries, upstream context | Weight 55, sorted by stars, issues/PRs excluded by default, always `untrusted` |
| PyPI JSON API | Python | Python packaging | API | Package metadata and versions | Registry metadata; linked code remains `untrusted` |

## Extensible Catalog

The initial list is not closed. An agent may propose new sources during a task, but it must ask the user before adding them persistently.

A new source proposal must include:

- name and base URL;
- category;
- language/platform/runtime/layer/topic scopes;
- initial weight and rationale;
- access method;
- policy, robots, and rate-limit notes;
- parser plan;
- citation rules;
- risks.

Do not persist sources that require personal login, bypass paywalls, ignore policy/robots, or cannot be cited transparently.

## API Notes

- Microsoft Learn catalog APIs expose training/certification metadata and are not a complete technical-docs content API.
- Stack Exchange API returns useful metadata for ranking and screening.
- Reddit access and AI/crawling policy require caution; treat it as read-only weak evidence.
- GitHub default acquisition should use repository search, not issues/PR search, because issues are often too noisy for code generation.
