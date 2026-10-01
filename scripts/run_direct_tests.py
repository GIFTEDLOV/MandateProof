"""Run direct contract tests without gltest's legacy pytest plugin bootstrap."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


bridge = load("mandateproof_direct_bridge", ROOT / "tests" / "direct" / "conftest.py")
suite = load("mandateproof_direct_lifecycle", ROOT / "tests" / "direct" / "test_lifecycle.py")
adversarial = load("mandateproof_adversarial", ROOT / "tests" / "adversarial" / "test_security.py")
properties = load("mandateproof_properties", ROOT / "tests" / "property" / "test_invariants.py")
semantic = load("mandateproof_semantic", ROOT / "tests" / "semantic" / "test_semantic_fixtures.py")
mutations = load("mandateproof_mutations", ROOT / "tests" / "mutation" / "test_mutation_catalog.py")

passed = 0
failed = []
for module in (suite, adversarial, properties, semantic, mutations):
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        fn = getattr(module, name)
        label = module.__name__ + ":" + name
        try:
            if len(inspect.signature(fn).parameters) == 0:
                fn()
            else:
                with bridge.env_session() as env:
                    fn(env)
            print(f"PASS {label}")
            passed += 1
        except BaseException as exc:
            print(f"FAIL {label}: {type(exc).__name__}: {exc}")
            failed.append(label)

print(f"DIRECT_TESTS passed={passed} failed={len(failed)} total={passed + len(failed)}")
if failed:
    raise SystemExit(1)
