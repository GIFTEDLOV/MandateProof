# Independent release audit

Audit date: 2026-10-01

Audited implementation commit: `147251e6aceb146c3021f1da4d086930141c4c2e`

Audited contract SHA-256: `0ec9129b112eb8af6589c5b163b30e850a89e6400a16a56eb71efbf09f0ab916`

The contract source was frozen before this review. No contract patch was made during the independent audit.

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
| Error domains | PASS | Deterministic validation errors remain distinct from evidence unavailable, integrity, model, and consensus paths. |
| Runtime/schema compatibility | PASS with finding A-01 | Local pinned harness and Studio-dev schema endpoint were both probed; see A-01. |
| Deployment consequence and value/fee | NOT YET QUALIFIED | Deployment is intentionally after local audit and source freeze. No funds were sent and no transaction was broadcast in this audit. |
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

## Severity disposition

Critical: 0

High: 0

Medium: 1, A-01 mitigated pending live preflight

Low: 2, A-02 and A-03 accepted and documented

The contract was not patched after audit because no Critical or High finding was identified. The only Medium finding is a release qualification requirement and is addressed by the schema/runtime preflight gates, not by changing contract semantics.
