# MandateProof architecture

## Deterministic boundary

The contract owns identity, authorization, time windows, version binding, admissibility, evidence ordering, snapshot hashing, state transitions, and canonical final state. It rejects malformed hashes, lengths, URLs, addresses, timestamps, identifiers, enums, and model output before any result is stored.

The nondeterministic closure receives a frozen snapshot only. It fetches each referenced artifact, checks HTTP success, exact byte length, SHA-256, and UTF-8 decoding, then asks a bounded prompt to classify mandate compliance. The closure does not write storage. The validator repeats artifact retrieval, integrity checks, and semantic evaluation independently; it compares only the exact structured result.

## Artifact identity

`MANDATE` evidence must equal the mandate policy artifact’s hash, byte length, and canonical URI and must use the mandate policy authority. `ACTION` and `TRACE` evidence must equal the action’s corresponding artifact identity. Additional evidence kinds are bound by subject, version, authority, hash, length, and URI in the snapshot. URI is never allowed to redefine an artifact.

## Snapshot

The snapshot is canonical JSON with sorted keys and compact separators. It includes the case, mandate version, action, claim, ordered evidence records, artifact identities, authority bindings, and frozen rule IDs. The SHA-256 fingerprint is stored once at freeze and must match at adjudication. Any post-freeze mutation or readback divergence prevents adjudication.

## Parties

The mandate principal creates, supersedes, and revokes mandates. Only its exact agent address may register an action. A case may be opened by the principal, the exact agent, or the mandate’s explicitly bound counterparty; the opener becomes the immutable complainant. Only these bound parties can commit evidence or advance the case.

## Errors

Deterministic business and integrity failures are raised before semantic execution. Nondeterministic failures remain typed as `EVIDENCE_UNAVAILABLE`, `INTEGRITY_ERROR`, `EVIDENCE_TOO_LARGE`, or `MODEL_ERROR`; they never become `AUTHORIZED` or `MATERIAL_BREACH`. Consensus disagreement is represented by the runner’s failed validator path, not by a semantic verdict.

## Appeal

An appeal is one new snapshot. `NEW_EVIDENCE` requires at least one appeal evidence record. `INTEGRITY_DEFECT` requires one of the bounded defect identifiers. The original result remains in `original_*` fields. The appeal result becomes canonical only after `finalize_case`; a second appeal or terminal mutation is rejected.
