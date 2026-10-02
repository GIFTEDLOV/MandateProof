# MandateProof submission

Project name: MandateProof

One-liner: Authenticated GenLayer adjudication of whether an autonomous AI agent acted within its frozen, versioned mandate.

Description: MandateProof stores immutable mandate versions, exact action and trace artifact identities, bounded evidence, and an append-only dispute lifecycle. Deterministic contract code binds principals, agents, versions, timestamps, hashes, byte lengths, authority, snapshots, permissions, appeals, and terminal state. GenLayer consensus independently verifies the frozen artifacts and decides only AUTHORIZED, MATERIAL_BREACH, or INCONCLUSIVE. One bounded appeal creates a new snapshot while retaining the original result.

Exact reviewer path: `contracts/mandate_proof.py` -> `tests/direct` -> `tests/adversarial` -> `tests/property` -> `tests/semantic` -> `tests/mutation` -> `docs/AUDIT.md` -> `docs/QUALIFICATION.md`.

Expected verification outcome: The reviewer can extract a 21-method schema, run 28 direct cases, verify strict artifact identity and state-machine guards, inspect the independent validator path, and confirm that unavailable or mutated evidence never becomes an adverse semantic verdict automatically.

GitHub URL: https://github.com/GIFTEDLOV/MandateProof

Submission release: `v1.0.3` (to be created after final exact-head CI verification)

Contract explorer link: Studio-dev does not expose an explorer URL in its network profile; verify the address and source through the Studio-dev RPC: https://studio-dev.genlayer.com/api.

Deployment details: network `studio-dev`, chain `61997`, RPC `https://studio-dev.genlayer.com/api`; deployment transaction `0xf969e99ff7eb05feb6d03a55101f0e97dc60c341ed08eaa4e58588513a4887b1`; contract `0xC481670D8CA2703f1e2cD960ad08Ed319937DaAD`.

Source SHA-256: `711ecf20f438ce8126b3833e5ceee696286bf158ab8553fd48b949535209d462` (`contracts/mandate_proof.py`); source commit `b1dfd2a329d67f55002d4d4a542df7adc13cdf40`.

Test summary: compile PASS; 28 direct cases PASS; adversarial 9; property 5; semantic 5; 21 defined executable security mutants, 21 executed, 21 killed, 0 survived; mutation catalog 21 anchors; local and Studio-dev schema 21 methods; provenance/secret checks PASS. Exact-head `release-gates` must be green on the final v1.0.3 release target; the exact run ID is recorded in the GitHub Release metadata.

Live proof: existing Studio-dev cases safely finalized `INCONCLUSIVE / INSUFFICIENT_EVIDENCE`; no live `AUTHORIZED` or `MATERIAL_BREACH` claim is made. Controlled local proof covers `AUTHORIZED`, `MATERIAL_BREACH`, and `INCONCLUSIVE`.

Audit summary: independent audit recorded in `docs/AUDIT.md`; Critical 0, High 0, Medium 5 (A-01 MITIGATED, A-04/A-05/A-06 REMEDIATED, A-08 OPEN / ACCEPTED RELEASE LIMITATION), Low 3 (A-02 ACCEPTED, A-03 HISTORICAL / PARTIALLY REMEDIATED, A-07 ACCEPTED TOOLCHAIN LIMITATION). Final source parity and Studio-dev schema readback passed.

Known limitations: external HTTPS artifacts must remain available; the current Studio-dev state has no non-mutating semantic retrieval preflight for a fresh case, so no new live semantic case was broadcast; semantic prose is not consensus state; one appeal round is supported; the integrity-defect appeal basis is a bounded governance claim rather than a cryptographic audit proof.
