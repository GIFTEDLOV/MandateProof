# Independent release audit

Audit date: 2026-10-01

Audited implementation commit: `e2dd07cc1429435025a2bd5f3491c3ba3204eb56`

Audited contract SHA-256: `e9bcbb24f4aa11151ea58e03d9a130bd6acd9f8fbe3aa8a62990b1be3d9e4eba`

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
| Error domains | PASS after A-04 | Deterministic validation errors remain distinct. Nondeterministic retrieval, integrity, size, and model failures normalize to the safe `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` result rather than serializing runner-specific `UserError` objects. |
| Runtime/schema compatibility | PASS with finding A-01 | Local pinned harness and Studio-dev schema endpoint were both probed; see A-01. |
| Deployment consequence and value/fee | PASS with qualification record | The first deployment reached schema and contract-info readback; its semantic error path exposed A-04 during live qualification. Replacement deployment remains subject to the frozen-source gates. |
| Provenance and secret hygiene | PASS | Source SHA and schema artifact recorded; repository secret scan found no credential pattern. |

## Findings

### A-01 — MEDIUM — runtime surface split requires release preflight

- Subsystem: runtime compatibility / deployment.
- Evidence: the local `genlayer-test 0.29.2` harness selected runner `v0.3.0-rc7` with the current top-level SDK surface; read-only Studio-dev `gen_getContractSchemaForCode` with the source header `py-genlayer:latest` resolved network runner `5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng` and returned a valid 21-method schema. An explicit local bootloader hash returned `invalid_contract runner malformed` on the network endpoint.
- Reproduction: POST the source as UTF-8 hex to `https://studio-dev.genlayer.com/api` using JSON-RPC method `gen_getContractSchemaForCode`.
- Impact: a deployment toolchain that silently substitutes a different runner could fail before contract execution or expose a different import surface.
- Remediation: source uses the network-supported `py-genlayer:latest` tag, compatibility imports, and a narrow nondeterministic API fallback. Release must repeat schema extraction and deployment simulation against the same network before broadcast.
- Status: mitigated for release qualification; live deployment still pending.

### A-02 — LOW — appeal integrity defects are governance claims

- Subsystem: appeal admission.
- Evidence: `INTEGRITY_DEFECT` accepts only one of four stable defect identifiers, but the contract cannot independently prove the historical defect without an external audit artifact.
- Reproduction: an authorized case party can submit a permitted defect code after the original adjudication.
- Impact: the appeal path is permissioned but not a cryptographic proof system for the defect claim.
- Remediation: retain the original immutable snapshot and require the bounded defect code; for stronger governance, a future version can bind a signed audit artifact without changing this contract’s one-round rule.
- Status: accepted design limitation; it cannot cause automatic adverse semantics and does not overwrite the original result.

### A-03 — LOW — mutation suite is source-anchor based

- Subsystem: testing.
- Evidence: the mutation test asserts 21 deliberate security anchors, but does not invoke a third-party mutation engine to generate and execute every mutant.
- Impact: mutation adequacy is a regression guard, not statistical mutation score.
- Remediation: run an external mutation engine in a future CI expansion if its GenVM process isolation is reliable.
- Status: accepted for the time-boxed release; explicit in `docs/TEST_MATRIX.md`.

### A-04 - MEDIUM - serialized UserError incompatibility on semantic failure path

- Subsystem: runtime compatibility / nondeterministic error handling.
- Evidence: live transaction `0xa7c114cd7843240adde94a07b9cefdc0bba744fc5369568979628c45f16d73f9` reached `UNDETERMINED`; the leader returned `MODEL_ERROR`, while validators reported `UserError.__init__() missing 1 required positional argument: 'data'` and VM error disagreement. The case remained `FROZEN` and no result was stored.
- Reproduction: adjudicate a frozen Studio-dev snapshot whose external/model path produces a typed nondeterministic failure under the pre-remediation source.
- Impact: a safe failure could become consensus-undetermined instead of a canonical safe outcome, preventing finalization and live qualification.
- Remediation: the hardened source classifies the failure internally and returns the bounded, non-adverse result `INCONCLUSIVE / INSUFFICIENT_EVIDENCE`; it also accepts either byte or UTF-8 string web bodies before exact length and SHA-256 verification. The local adversarial and semantic suites pass after the change.
- Status: remediated in `e2dd07c`; replacement deployment must prove the path live.

## Severity disposition

Critical: 0

High: 0

Medium: 2, A-01 mitigated and A-04 remediated pending replacement live proof

Low: 2, A-02 and A-03 accepted and documented

No Critical or High findings remain. A-04 was remediated before the replacement release audit; the replacement source remains frozen until live qualification is complete.
