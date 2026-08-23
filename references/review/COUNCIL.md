# Review Council

One council contract serves `/deliver` and `/code-review`.

## Select

A trivial change is local, changes no public interface or state, and touches no
error, security, persistence, or concurrency path. Use one scout with
`thermo.md` and `torvalds.md`.

Use three parallel groups otherwise:

| Group | References | Job |
|---|---|---|
| structure | `torvalds.md`, `ousterhout.md`, `hickey.md`, `taelin.md` | Data, ownership, module depth, necessary complexity, deletion |
| behavior | `uncle-bob.md`, `kcd.md` | Correctness, errors, recovery, behavioral contracts, tests |
| practicality | `carmack.md`, `thermo.md`, `ponytail.md` | Inspectability, hot paths, code growth, YAGNI |

Auth, secrets, untrusted input, privilege, cryptography, and material trust
boundary changes require a separate `/security-review`. Stop and ask the
operator to run it. Resume only from its triaged findings. Do not silently
replace that program with a general scout.

Completion criterion: The group set is fixed with its reason, and required
security triage is present.

## Run

Launch one read-only scout per selected group in parallel. Give each scout:

- accepted intent and scope;
- complete diff and relevant surrounding system;
- tests and product-surface QA observations;
- inspected evidence;
- only its group reference files.

Each returns zero to five findings. A finding states:

- exact file, symbol, behavior, or missing proof;
- trigger and failing mechanism;
- observed evidence and impact;
- smallest coherent repair;
- severity: `block`, `should`, or `note`;
- scope: `in` or `out`.

Completion criterion: Every selected group returns, and every claim is
grounded.

## Classify

Dedupe findings. A supported correctness, safety, security, data-integrity, or
contract defect is a **Blocker**. Taste never suppresses it.

A non-blocking finding is a **Take** only when its repair:

- removes a dual owner or invalid representable state;
- deletes incidental machinery or decomplects concerns;
- makes a failure visible and recoverable;
- creates a smaller stable interface; or
- defends accepted behavior against a plausible regression.

Classify style, naming, comments, speculative flexibility, and unrelated
cleanup as **Drop** unless they cause a supported defect.

Completion criterion: Every supported finding is Blocker, Take, or Drop.
