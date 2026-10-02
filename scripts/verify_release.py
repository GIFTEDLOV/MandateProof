"""Verify release identity and provenance invariants without network writes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).parents[1]
EXPECTED_SHA = "711ecf20f438ce8126b3833e5ceee696286bf158ab8553fd48b949535209d462"
EXPECTED_ADDRESS = "0xC481670D8CA2703f1e2cD960ad08Ed319937DaAD"
EXPECTED_DEPLOYMENT = "0xf969e99ff7eb05feb6d03a55101f0e97dc60c341ed08eaa4e58588513a4887b1"


def main() -> int:
    source = (ROOT / "contracts" / "mandate_proof.py").read_bytes()
    actual_sha = hashlib.sha256(source).hexdigest()
    schema = json.loads((ROOT / "artifacts" / "schema.json").read_text(encoding="utf-8"))
    methods = schema.get("methods", {})
    provenance = json.loads((ROOT / "artifacts" / "PROVENANCE.json").read_text(encoding="utf-8"))
    docs = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("README.md", "docs/SUBMISSION.md", "docs/QUALIFICATION.md"))
    if actual_sha != EXPECTED_SHA:
        raise SystemExit(f"contract SHA mismatch: {actual_sha}")
    if len(methods) != 21:
        raise SystemExit(f"schema method mismatch: {len(methods)}")
    if provenance.get("contract_address") != EXPECTED_ADDRESS or provenance.get("deployment_tx") != EXPECTED_DEPLOYMENT:
        raise SystemExit("deployment provenance mismatch")
    for value in (EXPECTED_ADDRESS, EXPECTED_DEPLOYMENT, EXPECTED_SHA, "61997", "studio-dev"):
        if value not in docs:
            raise SystemExit(f"missing provenance string: {value}")
    suspicious = re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY|api[_-]?key\s*[:=]", re.I)
    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            if suspicious.search(path.read_text(encoding="utf-8", errors="ignore")):
                raise SystemExit(f"secret pattern in {path}")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print(f"RELEASE_HEAD={head}")
    print(f"CONTRACT_SHA={actual_sha}")
    print("SCHEMA_METHODS=21")
    print("PROVENANCE_CHECK=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
