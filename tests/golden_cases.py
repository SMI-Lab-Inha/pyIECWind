"""Golden-reference scenario matrix for pyIECWind.

Each :class:`Scenario` pins a set of IEC parameters and the conditions generated
from them. The committed ``tests/golden/<scenario>/<code>.wnd`` files are the
trusted reference output; :mod:`test_golden` regenerates them and compares.

The matrix is representative rather than exhaustive: it covers every case family
(ECD, EWS, EOG, EDC, NWP, EWM) across both unit systems, both supported IEC
editions, the full turbine-class / turbulence-category range, and a non-zero
inflow inclination.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyiecwind.core import IECParameters

GOLDEN_ROOT = Path(__file__).resolve().parent / "golden"

# Baseline parameters are stored internally in SI units, exactly as the wizard
# and parser produce them. Scenarios override only what they exercise.
_BASE: dict[str, Any] = {
    "si_unit": True,
    "t1": 40.0,
    "wtc": 2,
    "catg": "B",
    "slope_deg": 0.0,
    "iec_edition": 3,
    "hh": 80.0,
    "dia": 80.0,
    "vin": 4.0,
    "vrated": 10.0,
    "vout": 24.0,
}


@dataclass(frozen=True)
class Scenario:
    name: str
    overrides: dict[str, Any]
    conditions: tuple[str, ...]

    def parameters(self) -> IECParameters:
        return IECParameters(conditions=list(self.conditions), **{**_BASE, **self.overrides})

    def directory(self) -> Path:
        return GOLDEN_ROOT / self.name


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "si_baseline",
        {},
        (
            "ECD+R",
            "ECD-R",
            "ECD+R+1.5",
            "ECD-R-2.0",
            "EWSV+12.0",
            "EWSH-12.0",
            "EWSV-8.0",
            "EOGI",
            "EOGO",
            "EOGR",
            "EOGR+2.0",
            "EDC+I",
            "EDC-I",
            "EDC+O",
            "EDC+R",
            "EDC-R+1.0",
            "NWP4.0",
            "NWP10.0",
            "NWP23.7",
            "EWM50",
            "EWM01",
        ),
    ),
    Scenario(
        "english_baseline",
        {"si_unit": False},
        (
            "ECD+R",
            "ECD-R",
            "EWSV+40.0",
            "EWSH-40.0",
            "EOGI",
            "EOGO",
            "EOGR",
            "EDC+R",
            "NWP10.0",
            "EWM50",
            "EWM01",
        ),
    ),
    Scenario(
        "edition1",
        {"iec_edition": 1},
        ("ECD+R", "EWSV+12.0", "EOGR", "EDC+R", "NWP10.0", "EWM50"),
    ),
    Scenario(
        "class1_cat_a",
        {"wtc": 1, "catg": "A"},
        ("ECD+R", "EWSV+12.0", "EOGR", "EDC+R", "EWM50", "EWM01"),
    ),
    Scenario(
        "class3_cat_c",
        {"wtc": 3, "catg": "C"},
        ("ECD+R", "EWSV+12.0", "EOGR", "EDC+R", "EWM50", "EWM01"),
    ),
    Scenario(
        "slope8",
        {"slope_deg": 8.0},
        ("ECD+R", "EWSV+12.0", "EOGR", "EDC+R", "NWP10.0", "EWM50"),
    ),
)
