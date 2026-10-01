from __future__ import annotations

import pytest


def test_case_a_authorized(env):
    env.full_case(case_id="c1", verdict="AUTHORIZED", reason="PURPOSE_WITHIN_MANDATE")
    env.contract.adjudicate_case("c1")
    env.contract.finalize_case("c1")
    assert env.contract.get_case("c1")["final_verdict"] == "AUTHORIZED"


def test_case_b_material_breach(env):
    env.full_case(case_id="c1", verdict="MATERIAL_BREACH", reason="PURPOSE_OUTSIDE_MANDATE", rules=["RULE_1"])
    env.contract.adjudicate_case("c1")
    env.contract.finalize_case("c1")
    assert env.contract.get_case("c1")["final_verdict"] == "MATERIAL_BREACH"
    assert env.contract.is_action_authorized("a1") is False


def test_case_c_inconclusive(env):
    env.full_case(case_id="c1", verdict="INCONCLUSIVE", reason="INSUFFICIENT_EVIDENCE")
    env.contract.adjudicate_case("c1")
    env.contract.finalize_case("c1")
    assert env.contract.get_case("c1")["final_verdict"] == "INCONCLUSIVE"


def test_case_d_injected_trace_is_still_schema_bounded(env):
    env.full_case(case_id="c1", verdict="AUTHORIZED", reason="PURPOSE_WITHIN_MANDATE")
    env.contract.adjudicate_case("c1")
    assert env.contract.get_case("c1")["original_reason"] == "PURPOSE_WITHIN_MANDATE"


def test_case_e_mutated_evidence_is_not_adverse_semantics(env):
    env.full_case()
    for pattern, response in env.vm._web_mocks:
        if "action" in pattern.pattern and "a1" in pattern.pattern:
            response["body"] = b"replace"
    try:
        env.contract.adjudicate_case("c1")
    except Exception:
        pass
    case = env.contract.get_case("c1")
    assert case["state"] == "ADJUDICATED"
    assert case["original_verdict"] == "INCONCLUSIVE"
