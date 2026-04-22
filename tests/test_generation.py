from __future__ import annotations

import unittest
from pathlib import Path

from pyiecwind.core import EWM_ALPHA, gen_ecd, gen_edc, gen_eog, gen_ewm, gen_ews, gen_nwp, generate_all

from helpers import WorkspaceTestCaseMixin, default_parameters


class GenerationTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def test_each_generator_writes_expected_file(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters()

        gen_ecd("ECD+R", params, output_dir=tmp)
        gen_ews("EWSV+12.0", params, output_dir=tmp)
        gen_eog("EOGR+2.0", params, output_dir=tmp)
        gen_edc("EDC+R", params, output_dir=tmp)
        gen_nwp("NWP10.0", params, output_dir=tmp)
        gen_ewm("EWM50", params, output_dir=tmp)

        expected = [
            "ECD+R.wnd",
            "EWSV+12.0.wnd",
            "EOGR+2.0.wnd",
            "EDC+R.wnd",
            "NWP10.0.wnd",
            "EWM50.wnd",
        ]
        for name in expected:
            self.assertTrue((tmp / name).exists(), name)

    def test_generate_all_creates_nested_output_directory(self) -> None:
        tmp = self.workspace_tempdir()
        output_dir = tmp / "nested" / "wind"
        params = default_parameters(conditions=["EWM50", "NWP10.0"])

        count = generate_all(params, output_dir=output_dir)

        self.assertEqual(count, 2)
        self.assertTrue((output_dir / "EWM50.wnd").exists())
        self.assertTrue((output_dir / "NWP10.0.wnd").exists())

    def test_ewm_uses_fixed_alpha_in_output(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["EWM50"])

        gen_ewm("EWM50", params, output_dir=tmp)
        last_line = (tmp / "EWM50.wnd").read_text(encoding="utf-8").strip().splitlines()[-1]
        columns = last_line.split()
        self.assertAlmostEqual(float(columns[5]), EWM_ALPHA, places=3)

    def test_nwp_in_english_units_still_uses_speed_in_mps(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["NWP10.0"], si_unit=False)

        gen_nwp("NWP10.0", params, output_dir=tmp)
        last_line = (tmp / "NWP10.0.wnd").read_text(encoding="utf-8").strip().splitlines()[-1]
        columns = last_line.split()
        self.assertAlmostEqual(float(columns[1]), 10.0 * 3.2808, places=3)

    def test_generated_file_contains_case_header(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["EWSV+12.0"])

        gen_ews("EWSV+12.0", params, output_dir=tmp)
        contents = (tmp / "EWSV+12.0.wnd").read_text(encoding="utf-8")
        self.assertIn("Extreme Vertical Wind Shear", contents)
        self.assertIn("Time", contents)
