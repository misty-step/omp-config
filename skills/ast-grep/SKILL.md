---
name: ast-grep
description: Use syntax-aware search and rewriting for structural code work in supported languages.
---

# ast-grep

Text replacement can corrupt code or miss equivalent syntax. `ast-grep` matches
tree-sitter syntax trees across TypeScript, JavaScript, Rust, Python, Go, and C.

Use `xd://ast_edit` for OMP codemods. It stages matches for review before apply.
Use the `sg` CLI for read-only exploration or repository-owned rules.

```sh
sg -p 'console.log($A)' src
sg scan
```

Patterns use `$NAME` for one node and `$$$NAME` for zero or more nodes. Reusing
a name requires the same syntax. Patterns and replacements must each parse as
one node; wrap fragments in a valid parent construct when needed.

For a rewrite, inspect staged matches, confirm syntax and scope, then resolve
with one reason. Use LSP instead for symbol renames and reference-aware
refactors.

Done when every intended syntax form changed and unrelated forms did not.
