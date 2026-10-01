# Test matrix

The direct gate is `scripts/run_direct_tests.py` and runs against the selected `v0.3.0-rc7` GenVM runner through the local compatibility bridge.

| Area | Current coverage |
|---|---:|
| Direct lifecycle | 8 |
| Adversarial | 9 |
| Property/invariant | 5 |
| Controlled semantic fixtures | 5 |
| Mutation catalog | 1 catalog covering 21 mutations |
| Total direct cases | 28 |

Core scenarios include mandate creation, duplicate/version isolation, revocation, exact agent and action-version binding, timestamp boundary semantics, evidence identity substitution, URI/hash/length/address bounds, freeze immutability, snapshot determinism, strict result keys, prompt injection, unavailable/mutated transport, one-shot adjudication, appeal limits, terminal finality, pagination, and authorization readback.

The mutation catalog is intentionally explicit: each listed mutation has a source anchor asserted by the gate. It is a fast security regression guard, not a claim that an external mutation-testing engine ran every generated mutant.
