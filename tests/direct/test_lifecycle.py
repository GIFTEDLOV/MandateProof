from __future__ import annotations

import hashlib
import json

import pytest


def h(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def test_mandate_identity_versioning_and_revocation(env):
    env.mandate()
    assert env.contract.get_mandate("m1", 1)["version"] == 1
    with pytest.raises(ValueError, match="DUPLICATE_MANDATE"):
        env.mandate()
    env.sender(env.owner)
    env.contract.supersede_mandate(
        "m1", 2, "policy-artifact-2", h(b"policy2"), 7,
        "https://artifacts.example/policy-2", "policy-authority",
        "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", h(b"metadata-2"), ["RULE_1"],
    )
    assert env.contract.get_mandate("m1", 1)["superseded"] is True
    env.contract.revoke_mandate("m1", 1)
    assert env.contract.get_mandate("m1", 1)["revoked"] is True


def test_action_requires_exact_agent_and_version(env):
    env.mandate()
    env.sender(env.owner)
    with pytest.raises(ValueError, match="UNAUTHORIZED_AGENT"):
        env.contract.register_action(
            "a1", "m1", 1, "action-artifact", h(b"approve"), 7,
            "https://artifacts.example/action-a1", "trace-artifact", h(b"trace"), 5,
            "https://artifacts.example/trace-a1", "2026-06-01T00:00:00Z",
        )
    env.sender(env.agent)
    with pytest.raises(ValueError, match="MANDATE_NOT_FOUND"):
        env.action(version=2)
    env.action()
    assert env.contract.get_action("a1")["mandate_version"] == 1


def test_action_valid_until_boundary_is_inclusive_and_after_is_rejected(env):
    env.mandate()
    env.sender(env.agent)
    env.contract.register_action(
        "at-boundary", "m1", 1, "action-boundary", h(b"ok"), 2,
        "https://artifacts.example/action-boundary", "trace-boundary", h(b"ok"), 2,
        "https://artifacts.example/trace-boundary", "2027-01-01T00:00:00Z",
    )
    with pytest.raises(ValueError, match="ACTION_OUTSIDE_MANDATE_WINDOW"):
        env.contract.register_action(
            "after-boundary", "m1", 1, "action-after", h(b"ok"), 2,
            "https://artifacts.example/action-after", "trace-after", h(b"ok"), 2,
            "https://artifacts.example/trace-after", "2027-01-01T00:00:00.001Z",
        )


def test_case_requires_bound_action_and_core_evidence(env):
    env.mandate()
    env.action()
    env.case()
    with pytest.raises(ValueError, match="INSUFFICIENT_EVIDENCE"):
        env.contract.freeze_case("c1")
    env.evidence()
    env.contract.freeze_case("c1")
    case = env.contract.get_case("c1")
    assert case["state"] == "FROZEN"
    assert len(case["snapshot_fingerprint"]) == 64
    with pytest.raises(ValueError, match="EVIDENCE_FROZEN"):
        env.contract.commit_evidence(
            "c1", "late", "CONTEXT", "late", "authority", 1,
            h(b"late"), 4, "https://artifacts.example/late",
        )


def test_semantic_result_is_canonical_and_final_authorization_is_read_only(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    assert env.validate_last() is True
    case = env.contract.get_case("c1")
    assert case["state"] == "ADJUDICATED"
    assert case["original_verdict"] == "AUTHORIZED"
    env.contract.finalize_case("c1")
    assert env.contract.is_action_authorized("a1") is True
    assert env.contract.get_case("c1")["state"] == "FINAL"
    with pytest.raises(ValueError, match="INVALID_FINALIZE_STATE"):
        env.contract.finalize_case("c1")


def test_one_bounded_appeal_retains_original(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    env.sender(env.owner)
    env.contract.open_appeal("c1", "NEW_EVIDENCE", "evidence-better")
    body = b"additional context"
    url = "https://artifacts.example/appeal-context"
    env.web(url, body)
    env.contract.commit_appeal_evidence(
        "c1", "ae1", "CONTEXT", "context-1", "counterparty", 1,
        h(body), len(body), url,
    )
    env.contract.freeze_appeal("c1")
    env.model("INCONCLUSIVE", "INSUFFICIENT_EVIDENCE", [])
    env.contract.adjudicate_appeal("c1")
    case = env.contract.get_case("c1")
    assert case["original_verdict"] == "AUTHORIZED"
    assert case["appeal_verdict"] == "INCONCLUSIVE"
    env.contract.finalize_case("c1")
    assert env.contract.is_action_authorized("a1") is False
    with pytest.raises(ValueError, match="INVALID_APPEAL_STATE"):
        env.contract.open_appeal("c1", "INTEGRITY_DEFECT", "SNAPSHOT_BINDING_ERROR")


def test_integrity_mismatch_fails_closed_without_breach(env):
    env.full_case()
    # Replace the action response with bytes whose length/hash do not match.
    for pattern, response in env.vm._web_mocks:
        if "action" in pattern.pattern and "a1" in pattern.pattern:
            response["body"] = b"replace"
    try:
        env.contract.adjudicate_case("c1")
    except Exception:
        pass
    # Direct harness errors, or a non-result path, leave the frozen snapshot untouched.
    assert env.contract.get_case("c1")["state"] == "FROZEN"


def test_exact_key_parser_rejects_extra_keys(env):
    env.full_case()
    env.model_response = json.dumps({
        "verdict": "AUTHORIZED",
        "reason_code": "PURPOSE_WITHIN_MANDATE",
        "violated_rule_ids": [],
        "extra": "reject",
    })
    env.vm._llm_mocks.clear()
    env.vm.mock_llm(".*", env.model_response)
    with pytest.raises(Exception):
        env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["state"] == "FROZEN"
