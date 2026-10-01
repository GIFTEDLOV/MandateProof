# Studio-dev qualification

Status: preflight complete; one fee-invalid deployment attempt is recorded; corrected deployment retry is separately fee-qualified and still pending.

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
| Selected deployer | `deployer` / `0xf39fd6e51aad88ce7596c73fc557cca4cc600c82` |
| Deployer status | unlocked |
| Deployer balance | `75561.260810361573380482 GEN` at preflight |
| Fee baseline | CLI `estimate-fees --json` returned `feeValue=100000000000010352` wei for the default profile |
| Faucet | not used |
| Deployment preflight | first CLI attempt omitted a nonzero fee value; corrected explicit fee value is now measured below |

The fee baseline is not a deployment authorization. The measured explicit fee value for the corrected deployment retry is `100000000000010352` wei, below the selected deployer balance. Deployment must broadcast exactly once for the corrected parameters, persist the transaction hash immediately, reconcile that same hash, and require finality, successful execution, contract address, schema readback, and `contract_info` readback.

## Historical failed attempt

The first and only attempt before fee correction used `genlayer deploy --fee-preset standard` without an explicit fee value. Studio-dev recorded the same hash on read-only receipt lookup:

- transaction: `0xb2482901489bc50d86ba3a2a08ac8f89f1ed609935b3d9b10d7239a8f0c437e6`
- receipt status: `0x0`
- revert reason: `FeeValueMustBeNonZero(1)`
- contract address: none

No blind rebroadcast was made. The retry is conditioned on the measured explicit fee value above.

## Qualification status

Local proof: PASS.

Controlled semantic proof: PASS for AUTHORIZED, MATERIAL_BREACH, INCONCLUSIVE, prompt-injected data, and mutated/unavailable artifacts.

Network schema proof: PASS.

Live contract proof: pending corrected deployment.
