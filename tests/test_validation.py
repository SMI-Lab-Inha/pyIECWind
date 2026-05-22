from __future__ import annotations

import dataclasses
import unittest

from helpers import WorkspaceTestCaseMixin, default_parameters
from pyiecwind import IECParameters
from pyiecwind.core import IECWindWarning, generate_all
from pyiecwind.parsing import _build_parameters, _parse_case_row


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

    def test_unsupported_edition_raises_by_default(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported IEC edition"):
            _build_parameters(
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

    def test_unsupported_edition_coerced_only_under_legacy(self) -> None:
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
                legacy=True,
            )
        self.assertEqual(params.iec_edition, 3)
        self.assertEqual(params.alpha, 0.14)

    def test_generate_all_skips_invalid_conditions(self) -> None:
        tmp = self.workspace_tempdir()
        params = default_parameters(conditions=["EWM50", "ABC123", "EWSV+99.0"])
        result = generate_all(params, output_dir=tmp, strict=False)
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


def _valid_kwargs(**overrides):
    base = dict(
        si_unit=True,
        t1=40.0,
        wtc=2,
        catg="B",
        slope_deg=0.0,
        iec_edition=3,
        hh=80.0,
        dia=80.0,
        vin=4.0,
        vrated=10.0,
        vout=24.0,
        conditions=["EWM50"],
    )
    base.update(overrides)
    return base


class DirectConstructionTests(unittest.TestCase):
    """IECParameters must be impossible to construct in an invalid state."""

    def test_valid_parameters_construct(self) -> None:
        params = IECParameters(**_valid_kwargs())
        self.assertEqual(params.conditions, ("EWM50",))

    def test_conditions_are_stored_immutably(self) -> None:
        params = IECParameters(**_valid_kwargs(conditions=["EWM50", "NWP10.0"]))
        self.assertIsInstance(params.conditions, tuple)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            params.vrated = 99.0  # type: ignore[misc]

    def test_invalid_fields_are_rejected(self) -> None:
        cases = {
            "class": _valid_kwargs(wtc=4),
            "category": _valid_kwargs(catg="Z"),
            "edition": _valid_kwargs(iec_edition=2),
            "geometry": _valid_kwargs(hh=30.0, dia=80.0),
            "speed_order": _valid_kwargs(vin=10.0, vrated=4.0),
            "non_finite": _valid_kwargs(vrated=float("nan")),
            "negative_diameter": _valid_kwargs(dia=-1.0),
        }
        for name, kwargs in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    IECParameters(**kwargs)
