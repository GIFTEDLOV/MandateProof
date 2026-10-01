# Studio-dev qualification

Status at source freeze: preflight complete; deployment not yet broadcast.

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
| Deployment | not attempted in this checkpoint |

The fee baseline is not a deployment authorization. Before broadcast, the exact deploy fee must be estimated from the final deployable source/profile and checked against the selected deployer balance. Deployment must broadcast exactly once, persist the transaction hash immediately, reconcile that same hash, and require finality, successful execution, contract address, schema readback, and `contract_info` readback.

## Qualification status

Local proof: PASS.

Controlled semantic proof: PASS for AUTHORIZED, MATERIAL_BREACH, INCONCLUSIVE, prompt-injected data, and mutated/unavailable artifacts.

Network schema proof: PASS.

Live contract proof: pending deployment authorization and exact fee simulation.
