"""Property/invariant tests for the generators.

These lock structural and physical properties that must hold regardless of the
exact numbers: transient durations and row counts, column shape, the power-law
exponent used, unit scaling, and direction-change endpoints.
"""

from __future__ import annotations

import math
import unittest

from helpers import WorkspaceTestCaseMixin, default_parameters
from pyiecwind.generation import gen_ecd, gen_edc, gen_eog, gen_ewm, gen_ews, gen_nwp
from pyiecwind.models import DT, EWM_ALPHA


def _data_rows(path) -> list[list[float]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("!"):
            rows.append([float(token) for token in line.split()])
    return rows


class TransientShapeTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = self.workspace_tempdir()
        self.params = default_parameters()

    def test_transient_row_counts_follow_duration(self) -> None:
        # One leading row at t=0 plus round(duration/DT)+1 transient samples.
        cases = [
            (gen_ecd, "ECD+R", 10.0),
            (gen_ews, "EWSV+12.0", 12.0),
            (gen_eog, "EOGR", 10.5),
            (gen_edc, "EDC+R", 6.0),
        ]
        for generator, code, duration in cases:
            with self.subTest(code=code):
                rows = _data_rows(generator(code, self.params, output_dir=self.tmp))
                self.assertEqual(len(rows), round(duration / DT) + 2)

    def test_steady_cases_emit_single_row(self) -> None:
        for generator, code in ((gen_nwp, "NWP10.0"), (gen_ewm, "EWM50")):
            with self.subTest(code=code):
                self.assertEqual(len(_data_rows(generator(code, self.params, output_dir=self.tmp))), 1)

    def test_every_row_has_eight_columns(self) -> None:
        for generator, code in ((gen_ecd, "ECD+R"), (gen_ews, "EWSH+12.0"), (gen_edc, "EDC+R")):
            with self.subTest(code=code):
                rows = _data_rows(generator(code, self.params, output_dir=self.tmp))
                self.assertTrue(all(len(row) == 8 for row in rows))

    def test_first_row_is_at_time_zero(self) -> None:
        rows = _data_rows(gen_ecd("ECD+R", self.params, output_dir=self.tmp))
        self.assertEqual(rows[0][0], 0.0)


class PhysicsInvariantTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = self.workspace_tempdir()

    def test_ewm_uses_fixed_shear_exponent(self) -> None:
        rows = _data_rows(gen_ewm("EWM50", default_parameters(), output_dir=self.tmp))
        self.assertAlmostEqual(rows[0][5], EWM_ALPHA, places=3)

    def test_transient_cases_use_edition_shear_exponent(self) -> None:
        params = default_parameters()  # edition 3 -> alpha 0.14
        rows = _data_rows(gen_ecd("ECD+R", params, output_dir=self.tmp))
        self.assertTrue(all(abs(row[5] - params.alpha) < 1e-9 for row in rows))

    def test_english_units_scale_wind_speed_column(self) -> None:
        si_rows = _data_rows(gen_nwp("NWP10.0", default_parameters(), output_dir=self.tmp))
        en_rows = _data_rows(gen_nwp("NWP10.0", default_parameters(si_unit=False), output_dir=self.tmp))
        self.assertAlmostEqual(en_rows[0][1], si_rows[0][1] * 3.2808, places=3)

    def test_direction_change_returns_to_full_theta(self) -> None:
        # EDC direction ramps from 0 to the full extreme angle theta.
        params = default_parameters()
        sigma1 = params.turb_intensity * (0.75 * params.vrated + 5.6)
        theta = math.degrees(4.0 * math.atan(sigma1 / (params.vrated * (1.0 + 0.1 * params.turb_rat))))
        rows = _data_rows(gen_edc("EDC+R", params, output_dir=self.tmp))
        self.assertEqual(rows[0][2], 0.0)
        self.assertAlmostEqual(rows[-1][2], theta, places=3)


if __name__ == "__main__":
    unittest.main()
