# MandateProof

MandateProof is a standalone GenLayer Intelligent Contract for one high-value trust question:

> Did an autonomous AI agent act within its frozen mandate?

An owner creates an immutable, versioned mandate. The agent later commits an action and trace by exact artifact identity. A bound principal, agent, or mandate counterparty can open a case. The contract freezes a deterministic evidence snapshot, then GenLayer consensus interprets only that snapshot as `AUTHORIZED`, `MATERIAL_BREACH`, or `INCONCLUSIVE`.

This repository contains the contract, direct VM tests, adversarial tests, semantic fixtures, mutation guards, runtime probe, audit record, and deployment provenance. It intentionally contains no frontend and no token economics.

## Why GenLayer

Hashing, byte lengths, addresses, versions, timestamps, permissions, evidence admissibility, lifecycle transitions, and final state are deterministic contract responsibilities. The semantic question—whether an authenticated action satisfies the mandate’s purpose and qualitative constraints—is the only nondeterministic boundary. The leader and validator independently fetch the same frozen artifact identities, verify their bytes, run the same bounded task, and compare only the strict consensus fields.

Artifacts are transport-independent identities: HTTPS URI is only a transport hint; SHA-256, exact UTF-8 byte length, authority, subject, and version are bound on-chain. Artifact contents are untrusted data. Prompt instructions, fake JSON, fake system prompts, and validator instructions embedded in evidence are explicitly ignored.

## Domain and lifecycle

Mandates are immutable records keyed by `(mandate_id, version)`. A new version creates a new record. Actions bind to one exact mandate version and cannot be rewritten by later versions. Evidence is append-only and core `MANDATE`, `ACTION`, and `TRACE` evidence must match the governing artifact identities exactly.

Cases move through:

`OPEN -> EVIDENCE_OPEN -> FROZEN -> ADJUDICATED -> FINAL`

or through one bounded appeal:

`ADJUDICATED -> APPEAL_OPEN -> APPEAL_FROZEN -> APPEAL_ADJUDICATED -> FINAL`

An appeal requires new admissible evidence or a specific integrity-defect code. It creates a new immutable snapshot and retains the original adjudication. There is no third semantic round and no result shopping. `FINAL` is terminal. `is_action_authorized(action_id)` reads only the canonical final state and is not equivalent to successful execution of an action.

## Public surface

The ABI has 21 public methods: mandate creation/versioning/revocation and reads; action registration/read; case opening, evidence, freezing, adjudication, appeal, finalization, pagination, authorization read, and `contract_info`. Exact schema is generated from the target runner and recorded under `artifacts/` during release qualification.

## Runtime

The probed Studio-dev target is chain `61997` at `https://studio-dev.genlayer.com/api`, with GenVM `v0.3.0-rc7` and network-supported `py-genlayer:latest` resolving to the currently accepted runner. The contract uses `gl.contract.Contract`, class-declared `gl.storage` types, deterministic `gl.message.datetime`, HTTPS `gl.nondet.web.get`, and a narrow `run_nondet_default`/`run_nondet` compatibility selection. See [the runtime probe](docs/RUNTIME_PROBE.md) for exact facts and the isolated local harness compatibility bridge.

## Verification

Run the direct suite with the pinned Studio harness interpreter:

```powershell
$py = 'C:\Users\DELL\AppData\Local\Beacon\studionet-stable-harness\venv\Scripts\python.exe'
& $py scripts\run_direct_tests.py
```

The suite covers deterministic lifecycle rules, authorization and identity substitution, URL/hash/byte bounds, malformed semantic results, prompt injection, unavailable evidence, pagination, snapshot stability, version isolation, terminal immutability, controlled semantic cases, and 21 executable security mutants plus the source-anchor catalog.

The local test bridge exists only because the installed `gltest 0.29.2` bootstrap still assumes the legacy `genlayer.py` layout. It adapts the harness to the probed runner without changing production contract code.

## Release and live proof

Deployment is deliberately separate from local proof. The release process freezes the source SHA, extracts the schema, performs read-only Studio-dev preflight, estimates fees, broadcasts once, reconciles the same transaction hash, checks finality and execution success, and reads back schema and `contract_info`. Live qualification records preconditions, transaction hashes, verdicts, source parity, and known limitations in [docs/SUBMISSION.md](docs/SUBMISSION.md). A dedicated anonymous Vercel static transport is independently verified for exact bytes, but no new case is broadcast when Studio-dev lacks a non-mutating semantic retrieval preflight.

## Known limitations

Artifact transport is external and must remain available at adjudication time. The contract intentionally fails closed on unavailable or mutated artifacts rather than guessing a semantic breach. Semantic output is bounded to three verdicts, a bounded reason code, and stable rule IDs; prose explanations are not consensus state. The current release supports one appeal round.
