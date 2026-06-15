# Language and Platform Taxonomy

## Routing Dimensions

The skill should classify requests across:

- `language`: Python, C, C++, C#, Assembly, shell, mixed;
- `platform`: Windows, Linux, cross-platform;
- `runtime`: CPython, .NET, libc, kernel, browser, embedded, package runtime;
- `layer`: application, OS API, runtime, compiler, linker, packaging, deployment, kernel/user boundary;
- `risk`: stable, version-sensitive, security-sensitive, performance-sensitive, undefined-behavior-prone;
- `evidence_needed`: none, official-docs, source-code, community, benchmark, legal/license.

## Multi-Scope Routing

One source can cover several dimensions.

Examples:

- Microsoft Learn: Windows, .NET, Azure, C#, C++, PowerShell.
- Python docs: Python language/runtime, standard library, C API.
- Stack Overflow: many languages, routed through tags and screening.
- GitHub: any language/OS, but only a relevant upstream repository is primary evidence.
- Intel/AMD/ARM manuals: Assembly, ABI, calling conventions, intrinsics.

Routing should:

1. select sources with overlapping scope;
2. prefer specific sources over broad ones;
3. apply authority weight and applicability screening;
4. allow source weights to differ by sub-scope.

## Python

Priority sources:

- Python documentation for language and standard-library behavior.
- PEPs for design decisions and semantics.
- PyPI metadata and upstream documentation for packages.

Common triggers:

- Python version differences;
- packaging and build backends;
- asyncio, threading, multiprocessing;
- C extensions, ABI, wheels.

## C and C++

Priority sources:

- cppreference for practical lookup;
- compiler documentation: MSVC, GCC, Clang;
- standards and proposals when exact semantics matter;
- upstream source for implementation-specific behavior.

Common triggers:

- undefined behavior;
- ABI and calling convention;
- linker/runtime library issues;
- sanitizer and compiler diagnostics.

## C# and .NET

Priority sources:

- Microsoft Learn for .NET and C# APIs.
- dotnet/runtime and dotnet/docs for implementation details.
- NuGet metadata and release notes for package behavior.

Common triggers:

- .NET Framework vs .NET differences;
- async/await, Span, unsafe, P/Invoke;
- Windows-only APIs;
- trimming, AOT, single-file deployment.

## Assembly

Priority sources:

- Intel/AMD manuals for x86/x64.
- ARM Architecture Reference Manual for ARM.
- Official ABI documents.
- Compiler Explorer only as observational evidence.

Common triggers:

- calling convention;
- stack alignment;
- register preservation;
- syscall ABI;
- intrinsics.

## Windows

Priority sources:

- Microsoft Learn for Win32, COM, .NET, PowerShell, WMI.
- Windows SDK headers when docs are incomplete.
- Sysinternals and Microsoft engineering blogs for diagnostics.

Common triggers:

- handles and lifetime;
- Unicode/ANSI APIs;
- security descriptors;
- services, registry, ETW, Event Log;
- COM apartment model.

## Linux

Priority sources:

- man pages and man7.org;
- kernel docs;
- glibc/musl docs;
- freedesktop specs where relevant.

Common triggers:

- syscalls and errno;
- signals, epoll, io_uring;
- permissions, capabilities, namespaces, cgroups;
- systemd, deb/rpm packaging.
