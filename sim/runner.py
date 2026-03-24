"""CLI entry point for running simulation scenarios.

Usage:
    python -m sim.runner                  # run all scenarios
    python -m sim.runner s02_lga          # run specific scenario
    python -m sim.runner s02_lga --verbose # verbose output
"""

from __future__ import annotations

import importlib
import sys
import types

from sim.engine.simulation import Simulation
from sim.scenarios.scenario_base import AssertionResult


SCENARIOS = [
    "sim.scenarios.s01_normal_cycle",
    "sim.scenarios.s02_lga",
    "sim.scenarios.s03_dca",
    "sim.scenarios.s04_commitment_gate",
    "sim.scenarios.s05_cvm_alert",
    "sim.scenarios.s06_parallel_ops",
    "sim.scenarios.s07_vfr_ifr_mix",
    "sim.scenarios.s08_llm_ground_controller",
]


def run_scenario_module(
    module: types.ModuleType,
    verbose: bool = False,
) -> tuple[bool, list[AssertionResult]]:
    """Run a single scenario module, return (all_passed, results)."""
    sim = Simulation()

    if verbose:
        print(f"\n{'='*60}")
        print(f"  {module.name}")
        print(f"  {module.description}")
        print(f"{'='*60}")

    module.setup(sim)
    result = module.run(sim)

    assertions = module.assertions(sim, result)

    all_passed = True
    for a in assertions:
        status = "PASS" if a.passed else "FAIL"
        if not a.passed:
            all_passed = False
        if verbose or not a.passed:
            print(f"  [{status}] {a.name}")
            if a.detail and (verbose or not a.passed):
                print(f"         {a.detail}")

    if verbose:
        print(f"\n  Events: {len(result.events)}")
        print(f"  Alerts: {len(result.alerts)}")
        print(f"  Violations: {len(result.violations)}")
        if result.violations:
            for v in result.violations:
                print(f"    {v.invariant_id}: {v.description}")
        print(f"  Sim time: {result.final_time:.0f}s")

    return all_passed, assertions


def run_scenario(scenario_name: str, verbose: bool = False) -> bool:
    """Run a single scenario by name."""
    # Find matching module
    for mod_path in SCENARIOS:
        if scenario_name in mod_path:
            module = importlib.import_module(mod_path)
            passed, _ = run_scenario_module(module, verbose)
            return passed

    print(f"Unknown scenario: {scenario_name}")
    print(f"Available: {[s.split('.')[-1] for s in SCENARIOS]}")
    return False


def run_all(verbose: bool = False) -> dict[str, bool]:
    """Run all scenarios, print summary."""
    results: dict[str, bool] = {}

    for mod_path in SCENARIOS:
        module = importlib.import_module(mod_path)
        passed, assertions = run_scenario_module(module, verbose)
        results[module.name] = passed

        if not verbose:
            status = "PASS" if passed else "FAIL"
            passed_count = sum(1 for a in assertions if a.passed)
            total_count = len(assertions)
            print(f"  [{status}] {module.name} ({passed_count}/{total_count} assertions)")

    # Summary
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n{'='*40}")
    print(f"  {passed}/{total} scenarios passed")
    print(f"{'='*40}")

    return results


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args:
        success = run_scenario(args[0], verbose)
    else:
        results = run_all(verbose)
        success = all(results.values())

    sys.exit(0 if success else 1)
