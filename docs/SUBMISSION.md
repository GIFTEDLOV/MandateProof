# MandateProof submission

Project name: MandateProof

One-liner: Authenticated GenLayer adjudication of whether an autonomous AI agent acted within its frozen, versioned mandate.

Description: MandateProof stores immutable mandate versions, exact action and trace artifact identities, bounded evidence, and an append-only dispute lifecycle. Deterministic contract code binds principals, agents, versions, timestamps, hashes, byte lengths, authority, snapshots, permissions, appeals, and terminal state. GenLayer consensus independently verifies the frozen artifacts and decides only AUTHORIZED, MATERIAL_BREACH, or INCONCLUSIVE. One bounded appeal creates a new snapshot while retaining the original result.

Exact reviewer path: `contracts/mandate_proof.py` -> `tests/direct` -> `tests/adversarial` -> `tests/property` -> `tests/semantic` -> `tests/mutation` -> `docs/AUDIT.md` -> `docs/QUALIFICATION.md`.

Expected verification outcome: The reviewer can extract a 21-method schema, run 28 direct cases, verify strict artifact identity and state-machine guards, inspect the independent validator path, and confirm that unavailable or mutated evidence never becomes an adverse semantic verdict automatically.

GitHub URL: pending repository publication.

Contract explorer link: pending deployment.

Deployment details: network `studio-dev`, chain `61997`, RPC `https://studio-dev.genlayer.com/api`; deployment transaction and contract address pending.

Source SHA-256: `0ec9129b112eb8af6589c5b163b30e850a89e6400a16a56eb71efbf09f0ab916` (`contracts/mandate_proof.py`).

Test summary: compile PASS; 28 direct cases PASS; 21 mutation anchors; local schema PASS with 21 public methods; Studio-dev code-to-schema probe PASS with 21 public methods; secret scan PASS.

Audit summary: independent audit recorded in `docs/AUDIT.md`; Critical 0, High 0, Medium 1 mitigated pending live preflight, Low 2 accepted and documented.

Known limitations: external HTTPS artifacts must remain available; semantic prose is not consensus state; one appeal round is supported; the integrity-defect appeal basis is a bounded governance claim rather than a cryptographic audit proof.
