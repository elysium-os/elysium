# Cronus Style

This documents the style used in **Cronus**. Note that this is an extension on the Elysium-wide style guide found [here](../style/index.md).

## Global Names

These rules apply to all global (available via headers) names whether that is symbols, types, macros.

Prefixes (in this order, left to right):

- Symbols to be implemented by every architecture shall be prefixed with `arch_`. Practically this means all symbols in `arch/` headers.
- Symbols for a specific architecture shall be prefixed with its name (ex. `x86_64_`).
- Internal symbols, global symbols shared across files but only to be used within its subsystem, shall be further prefixed with `internal_`.
- Prefixed with the name of their corresponding header. For example, a symbol in the header `vm.h` shall be prefixed with `vm_`.
