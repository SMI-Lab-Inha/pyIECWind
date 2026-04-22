"""Shared models and constants for pyIECWind."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

VERSION = "1.0.0"
DT = 0.1
VCG = 15.0
BETA = 6.4
PI = math.pi
EWM_ALPHA = 0.11

DEFAULT_INPUT_FILENAME = "pyiecwind.ipt"
DEFAULT_TEMPLATE_FILENAME = "pyiecwind_template.ipt"

VREF: dict[int, float] = {1: 50.0, 2: 42.5, 3: 37.5}
TURB_I: dict[str, float] = {"A": 0.16, "B": 0.14, "C": 0.12}
ALPHA_BY_EDITION: dict[int, float] = {1: 0.2, 3: 0.14}

CASE_TYPE_ORDER = ["ECD", "EWS", "EOG", "EDC", "NWP", "EWM"]
CASE_PREFIXES = {case_type: case_type for case_type in CASE_TYPE_ORDER}

TRUE_TOKENS = {"TRUE"}
FALSE_TOKENS = {"FALSE"}
NONE_TOKENS = {"NONE", "NULL"}

CASE_ROW_COMMENTS = {
    "ECD": "Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, +R-du, -R+du, -R-du",
    "EWS": "Extreme Wind Shear. Options: V+U, V-U, H+U, H-U",
    "EOG": "Extreme Operating Gust. Options: I, O, R, R+du, R-du",
    "EDC": "Extreme Direction Change. Options: +I, -I, +O, -O, +R, -R, +R+du, -R-du",
    "NWP": "Normal Wind Profile. Options: array of hub-height wind speeds in m/s",
    "EWM": "Extreme Wind Model. Options: 50 or 01, or an array such as [50, 01]",
}


@dataclass
class IECParameters:
    """Validated input parameters stored internally in SI units."""

    si_unit: bool
    t1: float
    wtc: int
    catg: str
    slope_deg: float
    iec_edition: int
    hh: float
    dia: float
    vin: float
    vrated: float
    vout: float
    conditions: list[str] = field(default_factory=list)

    @property
    def len_convert(self) -> float:
        return 1.0 if self.si_unit else 3.2808

    @property
    def spd_unit(self) -> str:
        return "m/s" if self.si_unit else "ft/s"

    @property
    def len_unit(self) -> str:
        return "m" if self.si_unit else "ft"

    @property
    def slope_rad(self) -> float:
        return math.radians(self.slope_deg)

    @property
    def turb_intensity(self) -> float:
        return TURB_I[self.catg.upper()]

    @property
    def alpha(self) -> float:
        return ALPHA_BY_EDITION[self.iec_edition]

    @property
    def vref(self) -> float:
        return VREF[self.wtc]

    @property
    def turb_scale(self) -> float:
        return 0.7 * self.hh if self.hh < 60.0 else 42.0

    @property
    def turb_rat(self) -> float:
        return self.dia / self.turb_scale

    @property
    def ve50(self) -> float:
        return 1.4 * self.vref

    @property
    def ve1(self) -> float:
        return 0.8 * self.ve50

    def summary(self) -> str:
        lc = self.len_convert
        lu = self.len_unit
        su = self.spd_unit
        return "\n".join(
            [
                f"  WTC={self.wtc}  CATG={self.catg}  Edition={self.iec_edition}",
                f"  HH={self.hh * lc:.1f} {lu}  Dia={self.dia * lc:.1f} {lu}",
                f"  Vin={self.vin * lc:.1f}  Vrated={self.vrated * lc:.1f}  Vout={self.vout * lc:.1f}  [{su}]",
                f"  TurbI={self.turb_intensity:.2f}  TurbScale={self.turb_scale:.1f} {lu}  TurbRat={self.turb_rat:.3f}",
                f"  Vref={self.vref:.1f}  Ve50={self.ve50:.1f}  Ve1={self.ve1:.1f}  [{su}]",
                f"  Alpha={self.alpha}  Slope={self.slope_deg:.1f} deg",
            ]
        )
