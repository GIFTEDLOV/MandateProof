from __future__ import annotations

import hashlib

import pytest


def test_snapshot_and_evidence_are_stable_after_freeze(env):
    env.full_case()
    before = env.contract.get_case("c1")
    with pytest.raises(ValueError, match="EVIDENCE_FROZEN"):
        env.contract.commit_evidence(
            "c1", "late", "CONTEXT", "late", "authority", 1,
            hashlib.sha256(b"late").hexdigest(), 4, "https://artifacts.example/late",
        )
    after = env.contract.get_case("c1")
    assert after["snapshot_fingerprint"] == before["snapshot_fingerprint"]
    assert after["evidence_count"] == before["evidence_count"]


def test_mandate_version_isolation(env):
    env.mandate()
    env.action()
    env.sender(env.owner)
    env.contract.supersede_mandate(
        "m1", 2, "policy-artifact-2", hashlib.sha256(b"policy2").hexdigest(), 7,
        "https://artifacts.example/policy-2", "policy-authority",
        "2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z", hashlib.sha256(b"metadata-2").hexdigest(), ["RULE_1"],
    )
    assert env.contract.get_action("a1")["mandate_version"] == 1
    assert env.contract.get_mandate("m1", 1)["superseded"] is True
    assert env.contract.get_mandate("m1", 2)["superseded"] is False


def test_authorization_derives_only_from_final_state(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    assert env.contract.is_action_authorized("a1") is False
    env.contract.finalize_case("c1")
    assert env.contract.is_action_authorized("a1") is True


def test_terminal_state_and_one_shot_adjudication(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    with pytest.raises(ValueError, match="INVALID_ADJUDICATION_STATE"):
        env.contract.adjudicate_case("c1")
    env.contract.finalize_case("c1")
    final = env.contract.get_case("c1")
    assert final["state"] == "FINAL"
    assert final["final_verdict"] == "AUTHORIZED"


def test_appeal_count_is_at_most_one(env):
    env.full_case()
    env.contract.adjudicate_case("c1")
    env.sender(env.owner)
    env.contract.open_appeal("c1", "INTEGRITY_DEFECT", "SNAPSHOT_BINDING_ERROR")
    with pytest.raises(ValueError, match="INVALID_APPEAL_STATE"):
        env.contract.open_appeal("c1", "INTEGRITY_DEFECT", "SNAPSHOT_BINDING_ERROR")

