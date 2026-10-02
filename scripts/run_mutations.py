"""Execute isolated source mutants against targeted security cases.

Every mutant is materialized outside the repository and selected through the
test-only MANDATEPROOF_CONTRACT_PATH override. The production source is never
modified; the temporary mutant is deleted after its case completes.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


bridge = load("mandateproof_mutation_bridge", ROOT / "tests" / "direct" / "conftest.py")
cases = load("mandateproof_executable_mutation_cases", ROOT / "tests" / "mutation" / "executable_cases.py")

MUTANTS = [
    ("M01_principal_authorization", "if previous.principal != sender:\n                _fail(\"UNAUTHORIZED_MANDATE_OWNER\")", "if False:\n                pass", "m01_principal_authorization"),
    ("M02_agent_binding", "if mandate.agent != gl.message.sender_address:\n            _fail(\"UNAUTHORIZED_AGENT\")", "if False:\n            pass", "m02_agent_binding"),
    ("M03_mandate_version_binding", "if action.mandate_id != mandate_id or int(action.mandate_version) != mandate_version:", "if action.mandate_id != mandate_id:", "m03_mandate_version_binding"),
    ("M04_hash_verification", "if hashlib.sha256(body_bytes).hexdigest() != ref[\"sha256\"]:", "if False:", "m04_hash_verification"),
    ("M05_byte_length_verification", "if len(body_bytes) != ref[\"byte_length\"]:", "if False:", "m05_byte_length_verification"),
    ("M06_https_only", "parsed.scheme.lower() != \"https\"", "False", "m06_https_only"),
    ("M07_private_literal_rejection", "literal.is_private", "False", "m07_private_literal_rejection"),
    ("M08_post_freeze_evidence", "if round_number == 0 and case.state not in {\"OPEN\", \"EVIDENCE_OPEN\"}:", "if False:", "m08_post_freeze_evidence"),
    ("M09_snapshot_validation", "if snapshot[\"fingerprint\"] != stored_fingerprint:", "if False:", "m09_snapshot_validation"),
    ("M10_one_shot_adjudication", "if case.state != expected_state:\n            _fail(\"INVALID_ADJUDICATION_STATE\")", "if False:\n            pass", "m10_one_shot_adjudication"),
    ("M11_one_appeal", "if case.state != \"ADJUDICATED\":\n            _fail(\"INVALID_APPEAL_STATE\")", "if False:\n            pass", "m11_one_appeal"),
    ("M12_terminal_finality", "else:\n            _fail(\"INVALID_FINALIZE_STATE\")", "else:\n            return", "m12_terminal_finality"),
    ("M13_exact_result_keys", "set(value.keys()) != {", "False and {", "m13_exact_result_keys"),
    ("M14_required_result_keys", "set(value.keys()) != {", "(value.setdefault(\"violated_rule_ids\", []) and False) or False and {", "m14_required_result_keys"),
    ("M15_allowed_verdicts", "if not isinstance(verdict, str) or verdict not in VERDICTS:", "if not isinstance(verdict, str):", "m15_allowed_verdicts"),
    ("M16_reason_compatibility", "if verdict == \"AUTHORIZED\" and reason not in {", "if verdict == \"AUTHORIZED\" and False and reason not in {", "m16_reason_compatibility"),
    ("M17_sorted_rule_ids", "if violations != sorted(violations) or len(set(violations)) != len(violations):", "if len(set(violations)) != len(violations):", "m17_sorted_rule_ids"),
    ("M18_unavailable_not_breach", '"verdict": "INCONCLUSIVE",\n        "reason_code": "INSUFFICIENT_EVIDENCE",', '"verdict": "MATERIAL_BREACH",\n        "reason_code": "PURPOSE_OUTSIDE_MANDATE",', "m18_unavailable_not_breach"),
    ("M19_subject_binding", "if kind == \"MANDATE\" and (subject_id != case.mandate_id or version != int(case.mandate_version)):", "if False:", "m19_subject_binding"),
    ("M20_authority_binding", "if authority != mandate.policy_authority:", "if False:", "m20_authority_binding"),
    ("M21_validator_independence", "return _result(leader_result.calldata, snapshot[\"rule_ids\"]) == independent", "return True", "m21_validator_independence"),
]


def run_case(case_name: str) -> None:
    with bridge.env_session() as env:
        getattr(cases, case_name)(env)


def main() -> int:
    source_path = ROOT / "contracts" / "mandate_proof.py"
    source = source_path.read_text(encoding="utf-8")
    os.environ.pop("MANDATEPROOF_CONTRACT_PATH", None)
    baseline_failures = []
    for name, _, _, case_name in MUTANTS:
        try:
            run_case(case_name)
        except BaseException as exc:
            baseline_failures.append(f"{name}: {type(exc).__name__}: {exc}")
    if baseline_failures:
        print("BASELINE_FAILURES")
        print("\n".join(baseline_failures))
        return 2

    killed = []
    survived = []
    with tempfile.TemporaryDirectory(prefix="mandateproof-mutants-") as temp_dir:
        for name, needle, replacement, case_name in MUTANTS:
            if source.count(needle) != 1:
                print(f"{name}: INVALID_SPEC needle_count={source.count(needle)}")
                survived.append(name)
                continue
            mutant = source.replace(needle, replacement, 1)
            mutant_path = Path(temp_dir) / f"{name}.py"
            mutant_path.write_text(mutant, encoding="utf-8")
            os.environ["MANDATEPROOF_CONTRACT_PATH"] = str(mutant_path)
            try:
                run_case(case_name)
            except BaseException as exc:
                killed.append(name)
                print(f"KILLED {name}: {type(exc).__name__}")
            else:
                survived.append(name)
                print(f"SURVIVED {name}")
        os.environ.pop("MANDATEPROOF_CONTRACT_PATH", None)

    total = len(MUTANTS)
    print(f"MUTATION_RESULT defined={total} executed={total} killed={len(killed)} survived={len(survived)} score={len(killed)}/{total}")
    if survived:
        print("SURVIVORS=" + ",".join(survived))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
