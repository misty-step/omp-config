---
name: ast-grep
description: Structural code search, linting, and AST-pattern rewriting across TypeScript, JavaScript, Rust, Python, Go, and C. Use for structural pattern matching, syntax-aware refactoring, codemods, and AST lint rules.
---

# ast-grep

`ast-grep` (`sg`) is a CLI tool for structural search and syntax-aware rewriting based on tree-sitter ASTs.

## Core Commands

### 1. Structural Search

Search for code matching an AST pattern:

```bash
ast-grep run --pattern '$OBJ.map($FN)' --lang ts
ast-grep -p 'fn $NAME($$$ARGS) -> Result<$T, $E> { $$$BODY }' -l rust
```

### 2. Structural Rewrite (Codemod)

Search and replace code structurally:

```bash
ast-grep run \
  --pattern 'console.log($$$ARGS)' \
  --rewrite 'logger.debug($$$ARGS)' \
  --lang ts \
  --interactive
```

Apply in batch across files:

```bash
ast-grep run \
  --pattern 'assert_eq!($A, true)' \
  --rewrite 'assert!($A)' \
  --lang rust \
  --update-all
```

### 3. Scan with Rules

Run AST lint rules defined in `sgconfig.yml` or rule directories:

```bash
ast-grep scan
ast-grep scan --rule path/to/rule.yml
```

## Pattern Syntax

- `$NAME`: Captures a single AST node (identifiers, expressions, literals).
  - Multiple occurrences of the same metavariable enforce equality (`$A === $A` matches `x === x`, not `x === y`).
- `$$$NAMES`: Captures zero or more AST sibling nodes (function arguments, statements, parameters).
- `$_`: Wildcard matching any single AST node without capturing.
- `$$$_`: Wildcard matching zero or more AST nodes.

## Rules YAML Format

```yaml
id: no-unsafe-type-assertion
language: typescript
rule:
  pattern: $A as unknown as $B
fix: $A as $B
message: "Avoid double type assertion ($A as unknown as $B)"
severity: warning
```

## Relational Constraints

Rules support nested relational sub-matchers:

- `inside`: Match only within an enclosing node (e.g. inside an `async` function).
- `has`: Match if a descendant node exists.
- `follows` / `precedes`: Match based on sibling node sequence.
- `not`: Negate a condition.

```yaml
id: require-await-in-async
language: typescript
rule:
  pattern: async function $NAME($$$ARGS) { $$$BODY }
  not:
    has:
      pattern: await $_
```

## OMP Harness Integration

In OMP agent sessions, preferred tool routes for structural edits:
1. `xd://ast_edit`: In-memory staged AST rewrites with auto-validation.
2. `ast-grep` CLI in `bash`: For repository-wide scans, lint audits, and batch refactors.
