from __future__ import annotations

from pathlib import Path

from gltest.direct import VMContext, create_address, deploy_contract


CONTRACT = Path(__file__).parents[2] / "contracts" / "mandate_proof.py"


def test_deploy_and_schema():
    vm = VMContext()
    owner = create_address("owner")
    with vm.activate():
        vm.sender = owner
        contract = deploy_contract(CONTRACT, vm)
        assert contract.contract_info()["name"] == "MandateProof"
        assert contract.contract_info()["nondet_api"] == "gl.vm.run_nondet"
