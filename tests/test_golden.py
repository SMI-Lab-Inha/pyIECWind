"""Golden-file regression tests.

The committed ``tests/golden`` corpus locks the trusted numeric output of every
generator. Comment/header lines are compared exactly (after masking the version
stamp, which legitimately changes between releases); data rows are compared
column-by-column within a tolerance matching the rendered three-decimal output.

To regenerate the corpus after an intentional change, run::

    PYIECWIND_UPDATE_GOLDEN=1 python -m pytest tests/test_golden.py

and review the diff before committing.
"""

from __future__ import annotations

import os
import re
import unittest

from golden_cases import SCENARIOS, Scenario
from helpers import WorkspaceTestCaseMixin
from pyiecwind.generation import _GENERATORS

# Half of the rendered precision (output uses "%9.3f"): catches any change of one
# displayed digit while tolerating signed-zero and last-bit rounding noise.
ABS_TOL = 5e-4

_VERSION_STAMP = re.compile(r"pyIECWind v\S+")


def _mask(line: str) -> str:
    return _VERSION_STAMP.sub("pyIECWind vX", line)


def _generate(scenario: Scenario, code: str, output_dir) -> str:
    params = scenario.parameters()
    generator = _GENERATORS[code[:3]]
    return generator(code, params, output_dir=output_dir).read_text(encoding="utf-8")


def regenerate_golden() -> int:
    """Write the golden corpus to disk, returning the number of files written."""

    written = 0
    for scenario in SCENARIOS:
        scenario.directory().mkdir(parents=True, exist_ok=True)
        for code in scenario.conditions:
            _generate(scenario, code, scenario.directory())
            written += 1
    return written


class GoldenTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def test_output_matches_golden_corpus(self) -> None:
        if os.environ.get("PYIECWIND_UPDATE_GOLDEN"):
            self.skipTest("regenerating golden corpus")

        tmp = self.workspace_tempdir()
        for scenario in SCENARIOS:
            for code in scenario.conditions:
                with self.subTest(scenario=scenario.name, code=code):
                    golden_path = scenario.directory() / f"{code}.wnd"
                    self.assertTrue(golden_path.exists(), f"missing golden file: {golden_path}")
                    expected = golden_path.read_text(encoding="utf-8")
                    actual = _generate(scenario, code, tmp)
                    self._assert_equivalent(expected, actual, scenario.name, code)

    def _assert_equivalent(self, expected: str, actual: str, scenario: str, code: str) -> None:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        self.assertEqual(
            len(expected_lines),
            len(actual_lines),
            f"{scenario}/{code}: line count {len(actual_lines)} != golden {len(expected_lines)}",
        )
        for lineno, (exp, act) in enumerate(zip(expected_lines, actual_lines, strict=True), start=1):
            if exp.startswith("!"):
                self.assertEqual(_mask(exp), _mask(act), f"{scenario}/{code} header line {lineno}")
                continue
            exp_values = [float(token) for token in exp.split()]
            act_values = [float(token) for token in act.split()]
            self.assertEqual(len(exp_values), len(act_values), f"{scenario}/{code} column count on line {lineno}")
            for col, (a, b) in enumerate(zip(exp_values, act_values, strict=True)):
                self.assertLessEqual(
                    abs(a - b),
                    ABS_TOL,
                    f"{scenario}/{code} line {lineno} col {col}: {b} != golden {a}",
                )


if __name__ == "__main__":
    if os.environ.get("PYIECWIND_UPDATE_GOLDEN"):
        count = regenerate_golden()
        print(f"Wrote {count} golden files.")
    else:
        unittest.main()
