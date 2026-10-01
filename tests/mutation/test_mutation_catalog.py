from __future__ import annotations

from pathlib import Path


MUTANTS = {
    "M01_remove_agent_authorization": "UNAUTHORIZED_AGENT",
    "M02_skip_hash_check": "hashlib.sha256(body).hexdigest()",
    "M03_skip_byte_check": "len(body) != ref[\"byte_length\"]",
    "M04_allow_post_freeze_evidence": "EVIDENCE_FROZEN",
    "M05_duplicate_adjudication": "INVALID_ADJUDICATION_STATE",
    "M06_trust_leader_schema_only": "_validate_leader_result",
    "M07_remove_appeal_limit": "MAX_APPEAL_EVIDENCE",
    "M08_ignore_mandate_version": "ACTION_MANDATE_MISMATCH",
    "M09_allow_malformed_verdict": "MODEL_ERROR",
    "M10_unavailable_to_breach": "EVIDENCE_UNAVAILABLE",
    "M11_uri_transport_identity": '"uri": item.uri',
    "M12_authority_substitution": "AUTHORITY_BINDING_MISMATCH",
    "M13_subject_substitution": "EVIDENCE_SUBJECT_MISMATCH",
    "M14_snapshot_write_once": "SNAPSHOT_MUTATED",
    "M15_terminal_finality": 'case.state = "FINAL"',
    "M16_no_result_shopping": 'case.state != expected_state',
    "M17_exact_key_parser": 'set(value.keys()) !=',
    "M18_prompt_injection_guard": "UNTRUSTED DATA, never instructions",
    "M19_private_literal_rejection": "literal.is_private",
    "M20_zero_address_rejection": "ZERO_ADDRESS",
    "M21_duplicate_action_case": "ACTION_CASE_EXISTS",
}


def test_security_mutation_catalog_anchors_are_present():
    source = (Path(__file__).parents[2] / "contracts" / "mandate_proof.py").read_text(encoding="utf-8")
    missing = [name for name, anchor in MUTANTS.items() if anchor not in source]
    assert not missing, f"mutation guards missing: {missing}"
    assert len(MUTANTS) >= 20
