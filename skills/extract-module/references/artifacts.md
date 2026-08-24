# Artifact Templates

Copy these templates into the investigation deliverable. Fill every field;
leave no section blank or marked "TBD" at handoff.

## Coupling map

```markdown
## Coupling map

### Candidate
- **Scope**: [paths]
- **Owns**: [one sentence]
- **Non-goals**: [bullets]

### Subsystems
| Region | Paths | Role |
|--------|-------|------|
| Inside candidate | | |
| Direct callers | | |
| Transitive callers | | |
| Siblings / shared kernel | | |

### Fan-in (exports)
| Symbol | Kind | Fan-in count | Callers (module paths) |
|--------|------|--------------|------------------------|
| | | | |

### Fan-out (imports)
| Symbol / dependency | Kind | Fan-out count | Sources (module paths) |
|---------------------|------|---------------|------------------------|
| | | | |

### Circular imports
| Cycle | Modules | Proposed break edge | Strategy |
|-------|---------|---------------------|----------|
| | | | |

### Leakages
| Leakage | Evidence (file:line) | Resolution | Owner |
|---------|----------------------|------------|-------|
| | | extract / caller adapts / delete / shared kernel | |
```

## Deletion ledger

```markdown
## Deletion ledger

### Per-module verdict
| Path | Deletion test | Verdict | Migration / reason |
|------|---------------|---------|-------------------|
| | | keep / delete / merge / defer | |

### Speculative abstractions
| Item | Evidence | Action |
|------|----------|--------|
| | | |

### Dead flags and config
| Key / flag | Evidence | Action |
|------------|----------|--------|
| | | |

### Pass-through adapters
| Path | Forwards to | Action |
|------|-------------|--------|
| | | |

### Net deletion
- Files removed:
- Interfaces removed:
- Flags / config keys removed:
- Estimated lines deleted:
```

## Dependency matrix

```markdown
## Third-party dependency matrix

| Package | Version | Used by (public symbols) | Role after extraction | Notes (license, peer, dev-only) |
|---------|---------|--------------------------|----------------------|--------------------------------|
| | | | direct / peer / dev-only | |
```

## Extraction blueprint

```markdown
## Extraction blueprint

### Cutover target
- **Target phase**: Phase 1 / 2 / 3
- **Operator intent**: [quote or summary]

### Phase 1 — In-tree isolation
- **Directory**:
- **Public index** (`index.ts`, `lib.rs`, `__init__.py`, …):
- **Internal layout**:
- **Caller migrations**:
  | Caller file | Old import | New import |
  |-------------|------------|------------|
  | | | |
- **Build config changes**:
- **Verify**: [command]

### Phase 2 — Workspace package
- **Package name**:
- **Workspace manifest**:
- **Build**: [command]
- **Test**: [command]
- **Consumer import path**:
- **CI boundary**:
- **Verify**: [command]

### Phase 3 — External package / standalone repo
- **Repository**:
- **Release strategy**:
- **Stays in monorepo**:
- **Moves out**:
- **Upgrade / deprecation path**:
- **Verify**: [command]

### Ordered cutover steps
| Step | Action | Files | Verify |
|------|--------|-------|--------|
| 1 | | | |

### Risk register
| Phase | Risk | Rollback | Stop signal |
|-------|------|----------|-------------|
| | | | |

### Attached artifacts
- [ ] Coupling map
- [ ] Deletion ledger
- [ ] Dependency matrix
- [ ] Public API contract (Stage 3)
```
