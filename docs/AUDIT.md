# Independent release audit

Audit date: 2026-10-01

Audited implementation commit: `b1dfd2a329d67f55002d4d4a542df7adc13cdf40`

Audited contract SHA-256: `711ecf20f438ce8126b3833e5ceee696286bf158ab8553fd48b949535209d462`

This is the post-qualification remediation audit. The contract source was frozen before this review; no contract patch was made during this audit.

## Review checklist

| Subsystem | Result | Evidence |
|---|---|---|
| Authorization and party binding | PASS | Principal-only mandate mutation; exact agent action binding; principal/agent/bound-counterparty case access; `action_cases` prevents competing case result shopping. |
| State machine and terminal finality | PASS | Explicit state checks in `_freeze`, `_adjudicate`, `open_appeal`, and `finalize_case`; `FINAL` has no outgoing transition. |
| Identity and versioning | PASS | Composite mandate key; monotonic versions; action stores exact mandate version; core evidence subject/version checks. |
| Evidence integrity and admissibility | PASS | HTTPS validation, exact SHA-256/byte-length checks, canonical core artifact equality, append-only IDs, pre-freeze-only writes. |
| Snapshot and replay | PASS | Canonical JSON fingerprint stored at freeze and rechecked at adjudication; one original round and one appeal round. |
| URL parser and bounds | PASS | UTF-8 byte bounds, credentials/fragments/control-character/port/hostname checks, private literal rejection, bounded evidence and prompt sizes. |
| Semantic authority | PASS | Only three verdicts; strict exact-key grammar; reason/verdict compatibility; sorted bounded rule IDs. |
| Validator independence | PASS | Validator re-fetches and re-evaluates the frozen snapshot; stable result comparison excludes prose. |
| Prompt injection | PASS | Prompt labels all artifacts as untrusted data and rejects embedded instructions, fake JSON, and fake validator/system prompts. |
| Storage and persistence | PASS | All persistent fields are class-declared `TreeMap`/`DynArray` fields or bounded storage records; nondeterministic closures perform no writes. |
| Timestamps | PASS | Runtime message timestamp is parsed and normalized; chronological comparisons use datetime values; `valid_until` is inclusive. |
| Pagination | PASS | Indexed case/evidence arrays with bounded page limits; case count is capped. |
| Appeals | PASS | One bounded appeal; new snapshot; original adjudication retained; terminal appeal result is canonical. |
| Error domains | PASS after A-04/A-05 | Deterministic validation errors remain distinct. Nondeterministic retrieval, integrity, size, and model failures normalize to the safe `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` result rather than serializing runner-specific `UserError` objects; structured JSON output is requested for reliable semantic success. |
| Runtime/schema compatibility | PASS with finding A-01 | Local pinned harness and Studio-dev schema endpoint were both probed; see A-01. |
| Deployment consequence and value/fee | PASS with qualification record | Final deployment `0xf969e99ff7eb05feb6d03a55101f0e97dc60c341ed08eaa4e58588513a4887b1` finalized with successful execution; address, schema, `contract_info`, and exact remote source parity were read back. |
| Provenance and secret hygiene | PASS | Source SHA and schema artifact recorded; repository secret scan found no credential pattern. |

## Findings

### A-01 — MEDIUM — runtime surface split requires release preflight

- Subsystem: runtime compatibility / deployment.
- Evidence: the local `genlayer-test 0.29.2` harness selected runner `v0.3.0-rc7` with the current top-level SDK surface; read-only Studio-dev `gen_getContractSchemaForCode` with the source header `py-genlayer:latest` resolved network runner `5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng` and returned a valid 21-method schema. An explicit local bootloader hash returned `invalid_contract runner malformed` on the network endpoint.
- Reproduction: POST the source as UTF-8 hex to `https://studio-dev.genlayer.com/api` using JSON-RPC method `gen_getContractSchemaForCode`.
- Impact: a deployment toolchain that silently substitutes a different runner could fail before contract execution or expose a different import surface.
- Remediation: source uses the network-supported `py-genlayer:latest` tag, compatibility imports, and a narrow nondeterministic API fallback. Release must repeat schema extraction and deployment simulation against the same network before broadcast.
- Status: MITIGATED and verified by final Studio-dev schema/deployment preflight.

### A-02 — LOW — appeal integrity defects are governance claims

- Subsystem: appeal admission.
- Evidence: `INTEGRITY_DEFECT` accepts only one of four stable defect identifiers, but the contract cannot independently prove the historical defect without an external audit artifact.
- Reproduction: an authorized case party can submit a permitted defect code after the original adjudication.
- Impact: the appeal path is permissioned but not a cryptographic proof system for the defect claim.
- Remediation: retain the original immutable snapshot and require the bounded defect code; for stronger governance, a future version can bind a signed audit artifact without changing this contract’s one-round rule.
- Status: ACCEPTED design limitation; it cannot cause automatic adverse semantics and does not overwrite the original result.

### A-03 — LOW — mutation suite is source-anchor based

- Subsystem: testing.
- Evidence: the original v1.0.0 mutation test asserted 21 deliberate security anchors, but did not invoke a third-party mutation engine to generate and execute every mutant. The v1.0.1 release adds an executable harness that materializes and runs all 21 defined mutants in isolation.
- Impact: mutation adequacy is a regression guard, not statistical mutation score.
- Remediation: v1.0.1 added `scripts/run_mutations.py`; it executed 21/21 defined mutants and killed 21/21. A third-party exhaustive mutation engine remains future work if reliable GenVM process isolation becomes available.
- Status: HISTORICAL / PARTIALLY REMEDIATED by the executable mutation harness; the remaining third-party tooling limitation is accepted and explicit in `docs/TEST_MATRIX.md`.

### A-04 - MEDIUM - serialized UserError incompatibility on semantic failure path

- Subsystem: runtime compatibility / nondeterministic error handling.
- Evidence: live transaction `0xa7c114cd7843240adde94a07b9cefdc0bba744fc5369568979628c45f16d73f9` reached `UNDETERMINED`; the leader returned `MODEL_ERROR`, while validators reported `UserError.__init__() missing 1 required positional argument: 'data'` and VM error disagreement. The case remained `FROZEN` and no result was stored.
- Reproduction: adjudicate a frozen Studio-dev snapshot whose external/model path produces a typed nondeterministic failure under the pre-remediation source.
- Impact: a safe failure could become consensus-undetermined instead of a canonical safe outcome, preventing finalization and live qualification.
- Remediation: the hardened source classifies the failure internally and returns the bounded, non-adverse result `INCONCLUSIVE / INSUFFICIENT_EVIDENCE`; it also accepts either byte or UTF-8 string web bodies before exact length and SHA-256 verification. The local adversarial and semantic suites pass after the change.
- Status: REMEDIATED in `e2dd07c`; final source safely normalizes the path in local and live execution.

### A-05 - MEDIUM - text response mode was too permissive for live JSON qualification

- Subsystem: semantic model result transport.
- Evidence: the first remediated live adjudication finalized safely as `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` even though the authenticated fixture was intentionally authorized. The local runner showed that its JSON response decoder expects a serialized JSON payload, while the prior text mode left the result shape dependent on runner behavior.
- Reproduction: run the authorized fixture against the `e2dd07c` replacement source using `response_format="text"`.
- Impact: valid semantic decisions could be conservatively downgraded to `INCONCLUSIVE`, reducing live qualification quality without creating an adverse verdict.
- Remediation: `b1dfd2a` requests `response_format="json"` and retains the contract-owned exact-key parser; the direct harness bridge serializes only its mock JSON payload to match the pinned decoder. Local semantic and adversarial suites pass.
- Status: REMEDIATED before final deployment. Final live artifact transport remained unavailable and therefore produced the documented safe `INCONCLUSIVE` outcome; no adverse or authorized claim is inferred from that transport failure.

### A-06 - MEDIUM - CI did not execute the release gates

- Subsystem: release engineering.
- Evidence: the prior workflow ran only compile and the source-anchor mutation catalog; it did not run the 28-case direct runner, category suites, executable mutations, provenance checks, or linter commands.
- Reproduction: inspect the pre-remediation `.github/workflows/ci.yml` at the v1.0.0 release head.
- Impact: a green CI result did not demonstrate the documented release test matrix.
- Remediation: CI now installs the pinned development toolchain, runs all 28 direct cases and each category suite, executes 21 isolated mutants, runs the linter compatibility gate, and verifies release provenance.
- Status: REMEDIATED.

### A-07 - LOW - current genvm-linter artifact bundle is incompatible with Studio-dev runner

- Subsystem: static analysis/toolchain.
- Evidence: `genvm-linter 0.11.0` runs, but reports only the known indirect-equivalence E010 warnings for the contract; validate, schema, and typecheck fail to load `py-genlayer` from the linter release bundle.
- Reproduction: run `python scripts/run_linter_gate.py` with the current source and toolchain.
- Impact: linter SDK-based validation cannot independently reproduce the Studio-dev schema in this environment.
- Remediation: CI records the limitation explicitly; authoritative schema validation remains the local pinned harness plus Studio-dev `gen_getContractSchemaForCode`, both of which return 21 methods. No contract semantics were changed to silence E010.
- Status: ACCEPTED toolchain limitation; monitor for a linter release containing the current runner.

### A-08 - MEDIUM - no non-mutating Studio-dev semantic retrieval preflight exists for terminal-only state

- Subsystem: live semantic qualification.
- Evidence: the public Vercel alias returns exact static bytes with HTTP 200 and matching hashes. The available Studio-dev write simulation against existing cases fails deterministically at `INVALID_ADJUDICATION_STATE` because all existing cases are terminal; it cannot exercise `gl.nondet.web.get` without a fresh frozen case.
- Reproduction: run the documented `genlayer estimate-fees ... adjudicate_case --args live-c7` simulation and inspect the deterministic lifecycle error.
- Impact: a fresh live `AUTHORIZED` or `MATERIAL_BREACH` semantic result cannot be proven without broadcasting a new case lifecycle write.
- Remediation: do not create a new case under uncertain preflight. Preserve the existing safe live `INCONCLUSIVE` result and distinguish it from controlled local semantic proof.
- Status: OPEN / ACCEPTED RELEASE LIMITATION for live proof; no contract-source defect established.

## Severity disposition

Critical: 0

High: 0

Medium: 5, A-01 MITIGATED, A-04 REMEDIATED, A-05 REMEDIATED, A-06 REMEDIATED, A-08 OPEN / ACCEPTED RELEASE LIMITATION

Low: 3, A-02 ACCEPTED, A-03 HISTORICAL / PARTIALLY REMEDIATED, and A-07 ACCEPTED TOOLCHAIN LIMITATION

No Critical or High findings remain. A-04, A-05, and A-06 were remediated without changing the deployed contract source. A-08 remains a documented qualification limitation.
