# Runtime Probe — 2026-10-01

## Scope

Read-only inspection only. No deployment and no faucet use.

## Local toolchain

| Tool | Observed |
|---|---|
| Python | 3.14.3 |
| pip | 25.3 |
| Node | 24.14.0 |
| pnpm | 11.0.9 |
| git | 2.53.0.windows.2 |
| GenLayer CLI | 0.40.0-rc.3 |
| genlayer-py | 0.18.0 |
| genlayer-test distribution | 0.29.2 in StudioNet harness |
| genvm-linter | not found as a standalone executable |
| genlayer-test executable | not found as a standalone executable; harness exposes `gltest`/pytest plugin |

The harness Python is `C:\Users\DELL\AppData\Local\Beacon\studionet-stable-harness\venv\Scripts\python.exe`.

## Target network probe

| Field | Value |
|---|---|
| Network | studio-dev |
| RPC | `https://studio-dev.genlayer.com/api` |
| `eth_chainId` | `0xf22d` (61997) |
| `net_version` | `61997` |
| CLI network profile | `studio-dev`, built-in GenLayer Studio Devnet |

Guessed version methods (`genlayer_getVersion`, `genlayer_version`, `gl_getVersion`, `genlayer_getNetworkInfo`) returned JSON-RPC `-32601 Method not found`; they are not treated as supported runtime APIs.

## Exact runner / contract surface

The installed `genlayer-test 0.29.2` direct harness extracted SDK runner `v0.3.0-rc7` from its cache. The selected current runner uses the newer top-level `genlayer` namespace.

- Contract base: `genlayer.contract.Contract`, imported through `import genlayer as gl` and used as `gl.contract.Contract`.
- Public ABI: `@gl.public.view` and `@gl.public.write` (non-payable unless explicitly marked payable).
- Address: `genlayer.Address`, 20-byte value with canonical `.as_hex`; equality is value-based on bytes.
- Storage: `DynArray`, `Array`, `TreeMap`, and `genlayer.storage.allow`; persistent fields are class annotations.
- Nondeterminism: `gl.vm.run_nondet_default(leader_fn, validator_fn)` is the current recommended API; `gl.vm.run_nondet` also exists. The old `run_nondet_unsafe` API was not found in the selected current runner.
- Nondeterministic result wrappers: `gl.vm.Return`, `gl.vm.UserError(data)`, `gl.vm.VMError`; `run_nondet_default` compares typed error domains and runs the validator in a sandbox.
- Web API: `gl.nondet.web.get`, `post`, `request`, etc., returning `gl.nondet.web.Response(status, headers, body)`.
- Schema: contract class `__get_schema__()` exists; CLI schema endpoint is `gen_getContractSchema` and code-to-schema endpoint on Studio is `gen_getContractSchemaForCode`.
- Simulation: GenLayer CLI exposes deployment and write fee/simulation paths; the direct harness exposes `gltest` pytest fixtures and client simulation helpers. Deployment is intentionally deferred.

The read-only Studio-dev probe of `gen_getContractSchemaForCode` established the currently accepted network surface. A source header of `py-genlayer:latest` resolved on Studio-dev to runner hash `5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng`; the endpoint executed GenVM `v0.3.0-rc7` and returned a valid 21-method schema. That network runner does not export `DynArray` from the top-level namespace, so the contract uses a compatibility import from `genlayer.storage` when necessary. An explicit local cache hash for the newer bootloader runner produced `invalid_contract runner malformed` on the network probe; it is not used as the deploy header. The source therefore pins the network-supported `py-genlayer:latest` tag while the local harness is selected explicitly at `v0.3.0-rc7`.

## Timestamp probe

The current runner exposes the deterministic message context field `gl.message.datetime` as an ISO string and supports `VMContext.warp()` in the test harness. The contract parses this bounded ISO representation deterministically and does not rely on the previous `message_raw` assumption.

## Runtime assumptions carried into implementation

1. Prefer the probed `gl.vm.run_nondet_default`; the contract has a narrow fallback to `gl.vm.run_nondet` for the network runner surface if the default alias is absent.
2. Keep nondeterministic closures read-only; persistent writes occur after the call returns.
3. Keep ABI values bounded and calldata-serializable.
4. Extract schema locally from the contract class and, after source is frozen, re-check with `gen_getContractSchemaForCode`/CLI tooling.

The successful network schema probe was read-only and did not deploy, request funds, or mutate chain state.
