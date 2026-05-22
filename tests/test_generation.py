from __future__ import annotations

import os
import unittest
from pathlib import Path

from helpers import WorkspaceTestCaseMixin, default_parameters
from pyiecwind.core import EWM_ALPHA, gen_ecd, gen_edc, gen_eog, gen_ewm, gen_ews, gen_nwp, generate_all


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

        result = generate_all(params, output_dir=output_dir)

        self.assertEqual(result.count, 2)
        self.assertTrue(result.ok)
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

    def test_generators_return_written_path(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters()
        path = gen_nwp("NWP10.0", params, output_dir=tmp)
        self.assertEqual(path, tmp / "NWP10.0.wnd")
        self.assertTrue(path.exists())

    def test_generator_writes_to_cwd_when_output_dir_is_none(self) -> None:
        tmp = self.workspace_tempdir()
        cwd = Path.cwd()
        os.chdir(tmp)
        try:
            path = gen_ewm("EWM01", default_parameters())
        finally:
            os.chdir(cwd)
        self.assertEqual(path.name, "EWM01.wnd")
        self.assertTrue((tmp / "EWM01.wnd").exists())

    def test_eog_and_edc_inflow_outflow_references(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters()
        for code in ("EOGI", "EOGO", "EDC+I", "EDC-O"):
            gen = gen_eog if code.startswith("EOG") else gen_edc
            self.assertTrue(gen(code, params, output_dir=tmp).exists(), code)


class GeneratorErrorTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = self.workspace_tempdir()
        self.params = default_parameters()

    def test_unparseable_codes_raise_value_error(self) -> None:
        cases = [
            (gen_ecd, "ECDX"),
            (gen_ews, "EWSX+12.0"),
            (gen_eog, "EOGZ"),
            (gen_edc, "EDCX"),
            (gen_nwp, "NWPfast"),
            (gen_ewm, "EWM99"),
        ]
        for generator, code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(ValueError, "Cannot parse"):
                    generator(code, self.params, output_dir=self.tmp)

    def test_speed_modifier_above_two_raises(self) -> None:
        for generator, code in ((gen_ecd, "ECD+R+3.0"), (gen_eog, "EOGR+3.0"), (gen_edc, "EDC+R+3.0")):
            with self.subTest(code=code):
                with self.assertRaisesRegex(ValueError, "must not exceed"):
                    generator(code, self.params, output_dir=self.tmp)

    def test_ews_speed_outside_operating_range_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be between"):
            gen_ews("EWSV+99.0", self.params, output_dir=self.tmp)
