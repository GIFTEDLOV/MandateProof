from __future__ import annotations

import hashlib
import json


def h(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def expect_error(fn, code: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert code in str(exc), f"expected {code}, got {exc}"
    else:
        raise AssertionError(f"expected {code}")


def _supersede_args():
    return (
        "m1", 2, "policy-artifact-2", h(b"policy2"), 7,
        "https://artifacts.example/policy-2", "policy-authority",
        "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", h(b"metadata-2"), ["RULE_1"],
    )


def m01_principal_authorization(env):
    env.mandate()
    env.sender(env.counterparty)
    expect_error(
        lambda: env.contract.create_mandate(
            "m1", env.agent, env.zero, 2, "policy-artifact-2", h(b"policy2"), 7,
            "https://artifacts.example/policy-2", "policy-authority",
            "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", h(b"metadata-2"), ["RULE_1"],
        ),
        "UNAUTHORIZED_MANDATE_OWNER",
    )


def m02_agent_binding(env):
    env.mandate()
    env.sender(env.owner)
    expect_error(
        lambda: env.contract.register_action(
            "a1", "m1", 1, "action-artifact", h(b"approve"), 7,
            "https://artifacts.example/action-a1", "trace-artifact", h(b"trace"), 5,
            "https://artifacts.example/trace-a1", "2026-06-01T00:00:00Z",
        ),
        "UNAUTHORIZED_AGENT",
    )


def m03_mandate_version_binding(env):
    env.mandate()
    env.action()
    env.sender(env.owner)
    env.contract.supersede_mandate(*_supersede_args())
    expect_error(
        lambda: env.contract.open_case("c2", "m1", 2, "a1", "Does the action comply?"),
        "ACTION_MANDATE_MISMATCH",
    )


def m04_hash_verification(env):
    env.full_case()
    for pattern, response in env.vm._web_mocks:
        if "action" in pattern.pattern and "a1" in pattern.pattern:
            response["body"] = b"replace"
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m05_byte_length_verification(env):
    env.full_case()
    action = env.contract.actions.get("a1")
    action.action_byte_length = 999
    case = env.contract.cases.get("c1")
    snapshot = env.contract._build_snapshot("c1", case, False)
    case.snapshot_fingerprint = snapshot["fingerprint"]
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m06_https_only(env):
    env.sender(env.owner)
    expect_error(
        lambda: env.contract.create_mandate(
            "http-m", env.agent, env.zero, 1, "p", h(b"p"), 1,
            "http://example.com/p", "authority",
            "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", h(b"m"), [],
        ),
        "INVALID_URI",
    )


def m07_private_literal_rejection(env):
    env.sender(env.owner)
    expect_error(
        lambda: env.contract.create_mandate(
            "private-m", env.agent, env.zero, 1, "p", h(b"p"), 1,
            "https://10.0.0.1/p", "authority",
            "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", h(b"m"), [],
        ),
        "INVALID_URI",
    )


def m08_post_freeze_evidence(env):
    env.full_case()
    expect_error(
        lambda: env.contract.commit_evidence(
            "c1", "late", "CONTEXT", "late", "authority", 1, h(b"late"), 4,
            "https://artifacts.example/late",
        ),
        "EVIDENCE_FROZEN",
    )


def m09_snapshot_validation(env):
    env.full_case()
    env.contract.cases.get("c1").snapshot_fingerprint = "0" * 64
    expect_error(lambda: env.contract.adjudicate_case("c1"), "SNAPSHOT_MUTATED")


def m10_one_shot_adjudication(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    expect_error(lambda: env.contract.adjudicate_case("c1"), "INVALID_ADJUDICATION_STATE")


def m11_one_appeal(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    env.sender(env.owner)
    env.contract.open_appeal("c1", "NEW_EVIDENCE", "evidence-better")
    expect_error(
        lambda: env.contract.open_appeal("c1", "NEW_EVIDENCE", "second-appeal"),
        "INVALID_APPEAL_STATE",
    )


def m12_terminal_finality(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    env.contract.finalize_case("c1")
    expect_error(lambda: env.contract.finalize_case("c1"), "INVALID_FINALIZE_STATE")


def _set_model(env, value: dict):
    env.vm._llm_mocks.clear()
    env.vm.mock_llm(".*", json.dumps(value))


def m13_exact_result_keys(env):
    env.full_case()
    _set_model(env, {"verdict": "AUTHORIZED", "reason_code": "PURPOSE_WITHIN_MANDATE", "violated_rule_ids": [], "extra": 1})
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m14_required_result_keys(env):
    env.full_case()
    _set_model(env, {"verdict": "AUTHORIZED", "reason_code": "PURPOSE_WITHIN_MANDATE"})
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m15_allowed_verdicts(env):
    env.full_case()
    _set_model(env, {"verdict": "BREACH", "reason_code": "PURPOSE_OUTSIDE_MANDATE", "violated_rule_ids": []})
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m16_reason_compatibility(env):
    env.full_case()
    _set_model(env, {"verdict": "AUTHORIZED", "reason_code": "PURPOSE_OUTSIDE_MANDATE", "violated_rule_ids": []})
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m17_sorted_rule_ids(env):
    env.mandate()
    env.contract.mandates.get("m1@1").rule_ids_csv = "RULE_1,RULE_2"
    env.action()
    env.case()
    env.evidence()
    env.sender(env.owner)
    env.contract.freeze_case("c1")
    _set_model(env, {"verdict": "AUTHORIZED", "reason_code": "PURPOSE_WITHIN_MANDATE", "violated_rule_ids": ["RULE_2", "RULE_1"]})
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m18_unavailable_not_breach(env):
    env.full_case()
    for pattern, response in env.vm._web_mocks:
        if "action" in pattern.pattern and "a1" in pattern.pattern:
            response["status"] = 503
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_verdict"] == "INCONCLUSIVE"


def m19_subject_binding(env):
    env.mandate()
    env.action()
    env.case()
    env.sender(env.owner)
    expect_error(
        lambda: env.contract.commit_evidence(
            "c1", "e1", "MANDATE", "wrong", "policy-authority", 1,
            h(b"purpose RULE_1"), 14, "https://artifacts.example/policy-1",
        ),
        "EVIDENCE_SUBJECT_MISMATCH",
    )


def m20_authority_binding(env):
    env.mandate()
    env.action()
    env.case()
    env.sender(env.owner)
    expect_error(
        lambda: env.contract.commit_evidence(
            "c1", "e1", "MANDATE", "m1", "impostor-authority", 1,
            h(b"purpose RULE_1"), 14, "https://artifacts.example/policy-1",
        ),
        "AUTHORITY_BINDING_MISMATCH",
    )


def m21_validator_independence(env):
    env.full_case()
    from genlayer.vm import Return
    snapshot = env.contract._build_snapshot("c1", env.contract.cases.get("c1"), False)
    _set_model(env, {"verdict": "MATERIAL_BREACH", "reason_code": "PURPOSE_OUTSIDE_MANDATE", "violated_rule_ids": []})
    leader = Return({"verdict": "AUTHORIZED", "reason_code": "PURPOSE_WITHIN_MANDATE", "violated_rule_ids": []})
    assert env.contract._validate_leader_result(leader, snapshot) is False
