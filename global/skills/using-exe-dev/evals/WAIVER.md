# /using-exe-dev eval waiver

expires: 2026-09-10

## Reason

The acceptance surface needs a live exe.dev account, an operator-owned SSH
identity, and an authorized VM. The repository has no credential-free fixture
that can prove destination routing, host-key checks, or credential isolation.

## Disposition

Before expiry, add an eval that uses a disposable VM and scoped repository
integration, proves both SSH destinations, removes the VM, and records
credential-free evidence. Otherwise, renew the waiver with a current reason
and expiry date.
