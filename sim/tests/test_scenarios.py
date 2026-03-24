"""Integration tests: run each scenario and verify all assertions pass."""

import unittest
import importlib

from sim.engine.simulation import Simulation
from sim.types import reset_ids


class ScenarioTestCase(unittest.TestCase):
    """Base for scenario tests."""

    def _run_scenario(self, module_path: str):
        reset_ids()
        module = importlib.import_module(module_path)
        sim = Simulation()
        module.setup(sim)
        result = module.run(sim)
        assertions = module.assertions(sim, result)

        for a in assertions:
            with self.subTest(assertion=a.name):
                self.assertTrue(a.passed, f"{a.name}: {a.detail}")

        return sim, result, assertions


class TestS01NormalCycle(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s01_normal_cycle")


class TestS02LGA(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s02_lga")


class TestS03DCA(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s03_dca")


class TestS04CommitmentGate(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s04_commitment_gate")


class TestS05CVMAlert(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s05_cvm_alert")


class TestS06ParallelOps(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s06_parallel_ops")


class TestS07VFRIFRMix(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s07_vfr_ifr_mix")


class TestS08LLMGroundController(ScenarioTestCase):
    def test_scenario(self):
        self._run_scenario("sim.scenarios.s08_llm_ground_controller")


if __name__ == "__main__":
    unittest.main()
