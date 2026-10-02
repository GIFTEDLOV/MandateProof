# Test matrix

The direct gate is `scripts/run_direct_tests.py` and runs against the selected `v0.3.0-rc7` GenVM runner through the local compatibility bridge.

| Area | Current coverage |
|---|---:|
| Direct lifecycle | 8 |
| Adversarial | 9 |
| Property/invariant | 5 |
| Controlled semantic fixtures | 5 |
| Executable mutation hardening | 21 isolated mutants, 21 killed |
| Mutation catalog | 1 source-anchor regression catalog covering 21 mutation classes |
| Total direct cases | 28 |

Core scenarios include mandate creation, duplicate/version isolation, revocation, exact agent and action-version binding, timestamp boundary semantics, evidence identity substitution, URI/hash/length/address bounds, freeze immutability, snapshot determinism, strict result keys, prompt injection, unavailable/mutated transport, one-shot adjudication, appeal limits, terminal finality, pagination, and authorization readback.

The source-anchor catalog remains a fast regression guard. The release also runs `scripts/run_mutations.py`, which materializes each of the 21 deliberate source mutants outside the repository, runs its targeted security case, records the mutant as killed or survived, and deletes the mutant. The current executable result is 21/21 killed; this is an explicit deterministic harness, not a statistical third-party mutation score.
