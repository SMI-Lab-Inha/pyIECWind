from __future__ import annotations

import unittest

from helpers import WorkspaceTestCaseMixin, default_parameters
from pyiecwind.core import IECWindWarning, _build_parameters, _parse_case_row, generate_all


class ValidationTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def test_invalid_wtc_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Wind turbine class must be 1, 2, or 3"):
            _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=4,
                catg="B",
                slope_deg=0.0,
                iec_edition=3,
                hh_raw=80.0,
                dia_raw=80.0,
                vin_raw=4.0,
                vrated_raw=10.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )

    def test_invalid_category_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Turbulence category must be A, B, or C"):
            _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=2,
                catg="Z",
                slope_deg=0.0,
                iec_edition=3,
                hh_raw=80.0,
                dia_raw=80.0,
                vin_raw=4.0,
                vrated_raw=10.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )

    def test_invalid_geometry_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Hub height"):
            _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=2,
                catg="B",
                slope_deg=0.0,
                iec_edition=3,
                hh_raw=30.0,
                dia_raw=80.0,
                vin_raw=4.0,
                vrated_raw=10.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )

    def test_invalid_speed_order_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Rated speed"):
            _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=2,
                catg="B",
                slope_deg=0.0,
                iec_edition=3,
                hh_raw=80.0,
                dia_raw=80.0,
                vin_raw=10.0,
                vrated_raw=4.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )

    def test_invalid_case_enable_flag_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be True, False, or None"):
            _parse_case_row("ECD             Maybe  [+R]                    - invalid flag", lineno=1)

    def test_unknown_case_type_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown case type"):
            _parse_case_row("XYZ             True   [+R]                    - invalid type", lineno=1)

    def test_slope_beyond_iec_limit_warns(self) -> None:
        with self.assertWarns(IECWindWarning):
            _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=2,
                catg="B",
                slope_deg=12.0,
                iec_edition=3,
                hh_raw=80.0,
                dia_raw=80.0,
                vin_raw=4.0,
                vrated_raw=10.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )

    def test_unsupported_edition_warns_and_defaults_to_edition_3(self) -> None:
        with self.assertWarns(IECWindWarning):
            params = _build_parameters(
                si_unit=True,
                t1=40.0,
                wtc=2,
                catg="B",
                slope_deg=0.0,
                iec_edition=2,
                hh_raw=80.0,
                dia_raw=80.0,
                vin_raw=4.0,
                vrated_raw=10.0,
                vout_raw=24.0,
                conditions=["EWM50"],
            )
        self.assertEqual(params.iec_edition, 3)
        self.assertEqual(params.alpha, 0.14)

    def test_generate_all_skips_invalid_conditions(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["EWM50", "ABC123", "EWSV+99.0"])
        result = generate_all(params, output_dir=tmp)
        self.assertEqual(result.count, 1)
        self.assertEqual(len(result), 1)
        self.assertFalse(result.ok)
        self.assertEqual([error.code for error in result.errors], ["ABC123", "EWSV+99.0"])
        self.assertIn("ABC123", str(result.errors[0]))

    def test_generate_all_strict_raises_on_first_invalid_condition(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["EWM50", "ABC123"])
        with self.assertRaisesRegex(ValueError, "Unknown condition type 'ABC'"):
            generate_all(params, output_dir=tmp, strict=True)
