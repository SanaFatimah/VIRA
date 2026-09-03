import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import main
import run_experiment


class MainConvergenceTests(unittest.TestCase):
    def decision(self, findings, max_cvss, iteration=1, parse_error=False):
        return main.convergence_node({
            "report": {"findings": findings, "parse_error": parse_error},
            "max_cvss": max_cvss,
            "iteration": iteration,
            "max_iterations": 5,
            "cvss_history": [max_cvss],
        })

    def test_empty_findings_zero_cvss_is_clean(self):
        result = self.decision([], 0.0)
        self.assertTrue(result["is_clean"])
        self.assertEqual(result["stop_reason"], "clean")

    def test_empty_findings_positive_cvss_is_not_clean(self):
        result = self.decision([], 5.0)
        self.assertFalse(result["is_clean"])
        self.assertTrue(result["below_threshold"])
        self.assertEqual(result["stop_reason"], "below_threshold")

    def test_nonempty_findings_positive_below_threshold_is_residual(self):
        result = self.decision([{"cwe_id": "CWE-TEST"}], 5.0)
        self.assertFalse(result["is_clean"])
        self.assertTrue(result["below_threshold"])
        self.assertEqual(result["stop_reason"], "below_threshold")

    def test_parser_failure_before_limit_continues(self):
        result = self.decision([], None, iteration=2, parse_error=True)
        self.assertFalse(result["is_clean"])
        self.assertIsNone(result["stop_reason"])

    def test_parser_failure_at_limit_stops_as_parse_error(self):
        result = self.decision([], None, iteration=5, parse_error=True)
        self.assertFalse(result["is_clean"])
        self.assertEqual(result["stop_reason"], "parse_error")


class ExperimentRunnerConvergenceTests(unittest.TestCase):
    def decision(self, findings, max_cvss, iteration=1, parse_error=False):
        return run_experiment.evaluate_convergence(
            findings=findings,
            raw_cvss=max_cvss,
            parse_error=parse_error,
            iteration=iteration,
            cvss_history=[max_cvss],
            max_iterations=5,
        )

    def test_empty_findings_zero_cvss_is_clean(self):
        result = self.decision([], 0.0)
        self.assertTrue(result["is_clean"])
        self.assertEqual(result["stop_reason"], "clean")

    def test_empty_findings_positive_cvss_is_not_clean(self):
        result = self.decision([], 5.0)
        self.assertFalse(result["is_clean"])
        self.assertEqual(result["stop_reason"], "below_threshold")

    def test_nonempty_findings_positive_below_threshold_is_residual(self):
        result = self.decision([{"cwe_id": "CWE-TEST"}], 5.0)
        self.assertFalse(result["is_clean"])
        self.assertTrue(result["below_threshold"])
        self.assertEqual(result["stop_reason"], "below_threshold")

    def test_parser_failure_before_limit_continues(self):
        result = self.decision([], None, iteration=2, parse_error=True)
        self.assertFalse(result["is_clean"])
        self.assertFalse(result["should_stop"])
        self.assertIsNone(result["stop_reason"])
        self.assertIsNone(result["max_cvss"])

    def test_parser_failure_at_limit_stops_as_parse_error(self):
        result = self.decision([], None, iteration=5, parse_error=True)
        self.assertFalse(result["is_clean"])
        self.assertTrue(result["should_stop"])
        self.assertEqual(result["stop_reason"], "parse_error")
        self.assertIsNone(result["max_cvss"])


if __name__ == "__main__":
    unittest.main()
