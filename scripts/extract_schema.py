"""Extract the ABI schema with the exact pinned Studio-dev runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from gltest.direct.vm import VMContext

ROOT = Path(__file__).parents[1]
CONTRACT = ROOT / "contracts" / "mandate_proof.py"
OUTPUT = ROOT / "artifacts" / "schema.json"


def load_bridge():
    path = ROOT / "tests" / "direct" / "conftest.py"
    spec = importlib.util.spec_from_file_location("mandateproof_schema_bridge", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load direct bridge")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    bridge = load_bridge()
    vm = VMContext()
    vm._contract_address = hashlib.sha256(b"mandateproof-schema").digest()[:20]
    vm.sender = hashlib.sha256(b"mandateproof-schema-sender").digest()[:20]
    with vm.activate():
        contract_cls = bridge.loader.load_contract_class(CONTRACT, vm, "v0.3.0-rc7")
        schema = json.loads(contract_cls.__get_schema__())
    methods = schema.get("methods", [])
    if len(methods) != 21:
        raise RuntimeError(f"expected 21 public methods, got {len(methods)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SCHEMA_METHODS={len(methods)}")
    print(f"SCHEMA_SHA256={hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}")
    print(f"SCHEMA_PATH={OUTPUT}")


if __name__ == "__main__":
    main()
