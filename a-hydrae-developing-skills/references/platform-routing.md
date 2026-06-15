# Platform Routing

Sources are multi-scope. Do not model the catalog as `one language -> one source`.

Routing dimensions:

- `languages`: Python, C, C++, C#, Assembly, shell, mixed;
- `platforms`: Windows, Linux, macOS, cross-platform, embedded;
- `runtimes`: .NET, CPython, PyPy, libc, kernel, compiler;
- `layers`: application, OS API, runtime, compiler, linker, packaging, deployment, kernel/user boundary;
- `topics`: security, performance, interop, async, ABI, syscalls, packaging, diagnostics.

Routing steps:

1. Extract language, platform, runtime, versions, API names, error strings, and package names from the user request.
2. Select sources whose scopes overlap.
3. Prefer more specific sources over broad community sources.
4. Apply authority weight and applicability screening.
5. Allow different weights by sub-scope when a source is authoritative in one area and weak in another.

Examples:

- Microsoft Learn: C#, C++, PowerShell, Windows, .NET, Azure.
- Stack Overflow: broad, but route through tags and screen answers.
- GitHub: primary only for the relevant upstream project/repository.
- Intel/AMD/ARM manuals: Assembly and intrinsics; combine with ABI docs for OS-specific calling conventions.
