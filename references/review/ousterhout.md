# Ousterhout

Judge the system after the change, not whether the new code is locally
small.

A deep module hides necessary complexity behind a small stable interface.
Flag shallow wrappers, pass-through methods, temporal coupling, and
configuration that moves complexity to callers.

Pull special cases and policy behind the owner. Spend complexity only where
it removes more complexity over the expected life of the system.

The deletion test: removing a module helps only when complexity concentrates
in one clearer owner.
