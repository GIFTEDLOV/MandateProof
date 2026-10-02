"""Compatibility bridge for gltest 0.29.2 with runner v0.3.0-rc7.

The installed direct harness still assumes the legacy ``genlayer.py`` module
layout.  Studio-dev's selected runner uses the current top-level
``genlayer.calldata``/``genlayer.storage`` layout.  These patches affect only
the local test harness, never the contract source or live network.
"""

from __future__ import annotations

import os
import sys
import hashlib
import json
import re
from contextlib import contextmanager

import pytest

from gltest.direct import loader
from gltest.direct.vm import VMContext


def _inject_current_message(vm):
    import genlayer.calldata as calldata
    from genlayer import Address

    sender = vm.sender
    if isinstance(sender, bytes):
        sender = Address(sender)
    elif hasattr(sender, "as_bytes"):
        sender = Address(sender.as_bytes)
    contract = vm._contract_address
    if isinstance(contract, bytes):
        contract = Address(contract)
    origin = vm.origin
    if isinstance(origin, bytes):
        origin = Address(origin)
    elif hasattr(origin, "as_bytes"):
        origin = Address(origin.as_bytes)
    message = {
        "contract_address": contract,
        "sender_address": sender,
        "origin_address": origin,
        "stack": [],
        "value": vm._value,
        "datetime": vm._datetime,
        "is_init": False,
        "chain_id": vm._chain_id,
        "entry_kind": 0,
        "entry_data": b"",
        "entry_stage_data": None,
    }
    encoded = calldata.encode(message)
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, encoded)
    finally:
        os.close(write_fd)
    vm._original_stdin_fd = os.dup(0)
    os.dup2(read_fd, 0)
    os.close(read_fd)


def _allocate_current(contract_cls, vm, *args, **kwargs):
    from genlayer.storage import Root, ROOT_SLOT_ID
    from genlayer.storage._internal.generate import ORIGINAL_INIT_ATTR, _BuilderCtx, _storage_build

    descriptor = _storage_build(_BuilderCtx.empty(), contract_cls)
    slot = vm._storage.get_store_slot(ROOT_SLOT_ID)
    instance = descriptor.get(slot, 0)
    init = getattr(descriptor, "cls", None)
    init = getattr(init or contract_cls, "__init__", None)
    if init is not None:
        init = getattr(init, ORIGINAL_INIT_ATTR, init)
        init(instance, *args, **kwargs)
    Root.MANAGER = vm._storage
    _patch_current_nondet()
    return instance


def _patch_current_nondet():
    import io
    import genlayer.calldata as calldata
    import genlayer.vm as current_vm
    import genlayer._internal.on_chain.gl_call as current_gl_call
    from genlayer.types import Lazy
    from gltest.direct import wasi_mock

    if getattr(current_vm, "_mandateproof_direct_patch", False):
        return

    def current_imp(data):
        active_vm = wasi_mock.get_vm()
        request = calldata.decode(data)
        response = wasi_mock._handle_gl_call(active_vm, request)
        # The pinned direct harness mock returns a dict for JSON prompts, while
        # the v0.3.0-rc7 decoder expects the JSON response payload as text.
        if (
            isinstance(response, dict)
            and isinstance(response.get("ok"), dict)
            and isinstance(request, dict)
            and isinstance(request.get("ExecPrompt"), dict)
            and request["ExecPrompt"].get("response_format") == "json2"
        ):
            response["ok"] = json.dumps(response["ok"], separators=(",", ":"))
        if response is None:
            return 2**32 - 1
        encoded = response if isinstance(response, bytes) else calldata.encode(response)
        fd_buffers = wasi_mock._local.fd_buffers
        fd = wasi_mock._local.fd_counter
        wasi_mock._local.fd_counter = fd + 1
        fd_buffers[fd] = io.BytesIO(encoded)
        return fd

    def direct_run(leader_fn, validator_fn, /, **kwargs):
        active_vm = wasi_mock.get_vm()
        result = leader_fn()
        if not hasattr(active_vm, "_current_validators"):
            active_vm._current_validators = []
        active_vm._current_validators.append((result, validator_fn))
        return result

    def direct_lazy(leader_fn, validator_fn, /, **kwargs):
        return Lazy(lambda: direct_run(leader_fn, validator_fn, **kwargs))

    direct_run.lazy = direct_lazy
    current_gl_call._imp_raw = current_imp
    current_vm.run_nondet = direct_run
    current_vm.run_nondet_default = direct_run
    current_vm._mandateproof_direct_patch = True


def _roundtrip_current(args, kwargs):
    import genlayer.calldata as calldata

    obj = {}
    if args:
        obj["args"] = list(args)
    if kwargs:
        obj["kwargs"] = kwargs
    if not obj:
        return args, kwargs
    decoded = calldata.decode(calldata.encode(obj))
    return tuple(decoded.get("args", [])), decoded.get("kwargs", {})


loader._inject_message_to_fd0 = _inject_current_message
loader._allocate_contract = _allocate_current
loader._calldata_roundtrip_args = _roundtrip_current


_original_refresh = VMContext._refresh_gl_message


def _refresh_current_message(vm):
    _original_refresh(vm)
    module = sys.modules.get("genlayer.message")
    if module is None:
        return
    from genlayer import Address, u256

    sender = vm.sender
    if not isinstance(sender, Address):
        sender = Address(sender.as_bytes if hasattr(sender, "as_bytes") else sender)
    origin = vm.origin
    if not isinstance(origin, Address):
        origin = Address(origin.as_bytes if hasattr(origin, "as_bytes") else origin)
    module.sender_address = sender
    module.origin_address = origin
    module.value = u256(vm._value)
    module.datetime = vm._datetime


VMContext._refresh_gl_message = _refresh_current_message


class ContractEnv:
    """Small test-only façade; all contract behavior remains on-chain code."""

    def __init__(self, vm, contract, Address):
        self.vm = vm
        self.contract = contract
        self.Address = Address
        self.owner = Address(hashlib.sha256(b"owner").digest()[:20])
        self.agent = Address(hashlib.sha256(b"agent").digest()[:20])
        self.counterparty = Address(hashlib.sha256(b"counterparty").digest()[:20])
        self.zero = Address(b"\x00" * 20)

    @staticmethod
    def digest(body):
        return hashlib.sha256(body).hexdigest()

    def sender(self, address):
        self.vm.sender = address

    def web(self, url, body=b"", status=200):
        self.vm.mock_web(re.escape(url), {"status": status, "headers": {}, "body": body})

    def model(self, verdict="AUTHORIZED", reason="PURPOSE_WITHIN_MANDATE", rules=None):
        self.vm._llm_mocks.clear()
        self.vm.mock_llm(
            ".*",
            json.dumps({
                "verdict": verdict,
                "reason_code": reason,
                "violated_rule_ids": rules or [],
            }),
        )

    def mandate(self, *, mandate_id="m1", version=1, policy=b"purpose RULE_1"):
        self._policy_body = policy
        self.sender(self.owner)
        self.contract.create_mandate(
            mandate_id,
            self.agent,
            self.zero,
            version,
            "policy-artifact-" + str(version),
            self.digest(policy),
            len(policy),
            "https://artifacts.example/policy-" + str(version),
            "policy-authority",
            "2026-01-01T00:00:00Z",
            "2027-01-01T00:00:00Z",
            self.digest(b"metadata-" + str(version).encode()),
            ["RULE_1"],
        )
        self.web("https://artifacts.example/policy-" + str(version), policy)

    def action(self, *, action_id="a1", mandate_id="m1", version=1, action=b"approve", trace=b"trace"):
        self._action_body = action
        self._trace_body = trace
        self.sender(self.agent)
        self.contract.register_action(
            action_id,
            mandate_id,
            version,
            "action-artifact",
            self.digest(action),
            len(action),
            "https://artifacts.example/action-" + action_id,
            "trace-artifact",
            self.digest(trace),
            len(trace),
            "https://artifacts.example/trace-" + action_id,
            "2026-06-01T00:00:00Z",
        )
        self.web("https://artifacts.example/action-" + action_id, action)
        self.web("https://artifacts.example/trace-" + action_id, trace)

    def case(self, *, case_id="c1", mandate_id="m1", version=1, action_id="a1", claim="Does the action comply?"):
        self.sender(self.owner)
        self.contract.open_case(case_id, mandate_id, version, action_id, claim)

    def evidence(self, *, case_id="c1", mandate_id="m1", version=1, action_id="a1"):
        policy = getattr(self, "_policy_body", b"purpose RULE_1")
        action = getattr(self, "_action_body", b"approve")
        trace = getattr(self, "_trace_body", b"trace")
        rows = [
            ("e1", "MANDATE", mandate_id, "policy-authority", policy, f"policy-{version}"),
            ("e2", "ACTION", action_id, "action-authority", action, f"action-{action_id}"),
            ("e3", "TRACE", action_id, "trace-authority", trace, f"trace-{action_id}"),
        ]
        for evidence_id, kind, subject, authority, body, label in rows:
            url = f"https://artifacts.example/{label}"
            self.sender(self.owner)
            self.contract.commit_evidence(
                case_id,
                evidence_id,
                kind,
                subject,
                authority,
                version,
                self.digest(body),
                len(body),
                url,
            )

    def full_case(self, *, case_id="c1", verdict="AUTHORIZED", reason="PURPOSE_WITHIN_MANDATE", rules=None):
        self.mandate()
        self.action()
        self.case(case_id=case_id)
        self.evidence(case_id=case_id)
        self.sender(self.owner)
        self.contract.freeze_case(case_id)
        self.model(verdict, reason, rules)

    def validate_last(self):
        """Run the captured validator independently in the direct harness."""
        from genlayer.vm import Return

        result, validator = self.vm._current_validators[-1]
        return validator(Return(result))


@contextmanager
def env_session():
    vm = VMContext()
    vm.sender = hashlib.sha256(b"owner").digest()[:20]
    with vm.activate():
        contract_path = os.environ.get(
            "MANDATEPROOF_CONTRACT_PATH",
            os.path.join(os.getcwd(), "contracts", "mandate_proof.py"),
        )
        contract = loader.deploy_contract(
            contract_path,
            vm,
            sdk_version="v0.3.0-rc7",
        )
        from genlayer import Address

        yield ContractEnv(vm, contract, Address)


@pytest.fixture
def env():
    with env_session() as current:
        yield current
