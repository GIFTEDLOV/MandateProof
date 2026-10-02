# Studio-dev qualification

Status: final source deployed and live-qualified on Studio-dev. The canonical final-address fixtures safely resolved to `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` because the external artifact transport was unavailable to the semantic runner; no result was retried or rewritten. Local controlled semantic proof covers all three verdicts.

## Preflight facts

| Check | Result |
|---|---|
| Network profile | `studio-dev` / GenLayer Studio Devnet |
| RPC | `https://studio-dev.genlayer.com/api` |
| Chain ID | `61997` (`eth_chainId = 0xf22d`) |
| GenVM | `v0.3.0-rc7-x86_64-linux-release` reported by schema probe |
| Network runner | `py-genlayer:latest` resolved to `5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng` |
| Read-only code schema | PASS; 21 public methods |
| Local extracted schema | PASS; 21 public methods; SHA-256 `e246b92ebeb97a225760171540a8b73c88478c71620a1ff5fc98a1867d642018` |
| Frozen final source | commit `b1dfd2a329d67f55002d4d4a542df7adc13cdf40`; contract SHA-256 `711ecf20f438ce8126b3833e5ceee696286bf158ab8553fd48b949535209d462` |
| Selected deployer | `deployer` / `0xf39fd6e51aad88ce7596c73fc557cca4cc600c82` |
| Deployer status | unlocked |
| Deployer balance | `75561.260810361573380482 GEN` at preflight |
| Fee baseline | CLI `estimate-fees --json` returned `feeValue=100000000000010352` wei for the default profile |
| Faucet | not used |
| Deployment preflight | PASS; measured explicit fee value below selected deployer balance |

The fee baseline is not a deployment authorization. The measured explicit fee value for the replacement deployment is `100000000000010352` wei, below the selected deployer balance. Deployment must broadcast exactly once for the frozen replacement source, persist the transaction hash immediately, reconcile that same hash, and require finality, successful execution, contract address, schema readback, and `contract_info` readback.

## Historical failed attempt

The first and only attempt before fee correction used `genlayer deploy --fee-preset standard` without an explicit fee value. Studio-dev recorded the same hash on read-only receipt lookup:

- transaction: `0xb2482901489bc50d86ba3a2a08ac8f89f1ed609935b3d9b10d7239a8f0c437e6`
- receipt status: `0x0`
- revert reason: `FeeValueMustBeNonZero(1)`
- contract address: none

The corrected CLI attempt also printed the explicit fee but still encoded an EVM value of zero and reverted:

- transaction: `0x74d10fc23ae20457f58ea14371ecbf47d1f412b740c3725edc7ec0c6e649e1b6`
- receipt status: `0x0`
- revert reason: `FeeValueMustBeNonZero(1)`
- contract address: none

The cause was isolated to the CLI deploy parameter path: its fee profile was not supplying a complete distribution. A complete deploy fee profile is now recorded at `artifacts/deploy-fee-profile.json`; its read-only estimate reproduces the nonzero fee value above. No blind rebroadcast was made.

## Qualification status

Local proof: PASS.

Controlled semantic proof: PASS for AUTHORIZED, MATERIAL_BREACH, INCONCLUSIVE, prompt-injected data, and mutated/unavailable artifacts.

Network schema proof: PASS.

Original live contract proof: deployment/schema/contract-info PASS; semantic error-path qualification found A-04. The first replacement address finalized a safe `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` result and exposed A-05; it is not the final release address.

## Final deployment

| Check | Result |
|---|---|
| Source commit | `b1dfd2a329d67f55002d4d4a542df7adc13cdf40` |
| Contract SHA-256 | `711ecf20f438ce8126b3833e5ceee696286bf158ab8553fd48b949535209d462` |
| Deployment transaction | `0xf969e99ff7eb05feb6d03a55101f0e97dc60c341ed08eaa4e58588513a4887b1` |
| Contract address | `0xC481670D8CA2703f1e2cD960ad08Ed319937DaAD` |
| Deployment receipt | FINALIZED; `FINISHED_WITH_RETURN`; `MAJORITY_AGREE` |
| Remote source parity | PASS; 46,010 bytes and exact SHA-256 match |
| Schema readback | PASS; 21 public methods |
| `contract_info` readback | PASS; version 1.0.0, one appeal round, terminal state FINAL |

## Live qualification

The final release address was exercised with two independent frozen cases. Every write used a read precondition, the measured fee value, one broadcast, same-hash reconciliation, finality/execution checks, and canonical readback.

| Fixture | Case | Snapshot | Final result | Authorization | Evidence |
|---|---|---|---|---|---|
| Authorized transport fixture | `live-c5` | `698c56fd44e288807cb471d4a94be69eec23162fb4a2062918828cb8993a7a84` | `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` | `false` | final tx `0x36f599d07c8970e5ba03b6c14800efde4180d90de694cc62b7737d8f7db4de18` |
| Alternate transport fixture | `live-c7` | `b3ff118ddfe469f4771a08209839bdf0a3f3404fc0b924ffbab2a233f28b6d58` | `INCONCLUSIVE / INSUFFICIENT_EVIDENCE` | `false` | final tx `0xfdbff47bc5efddca4ed7c3dadef9e10effa718e65930740d16b79b8a247c07f9` |

`live-c5` was adjudicated by `0x961fc942b25e76cf98ae31648922d33242d8e74abc1a99628ee53a9ccd47059b`; `live-c7` by `0x914f6e73b36815c359e4b468b2562e8ac9b32886057eb51d82643c48771c60a2`. Both cases are terminal and immutable. The safe live result is not treated as proof of a breach or authorization. Controlled local semantic fixtures independently prove `AUTHORIZED`, `MATERIAL_BREACH`, and `INCONCLUSIVE`; the live network limitation is recorded rather than converted into a semantic claim.

Historical live observations: the first deployment exposed the runner-specific `UserError` incompatibility (`0xa7c114cd7843240adde94a07b9cefdc0bba744fc5369568979628c45f16d73f9`); the remediated replacement then exposed the permissive text response mode. Those findings drove the frozen final source and are retained in `docs/AUDIT.md`.
