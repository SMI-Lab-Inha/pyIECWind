"""Shared models and constants for pyIECWind."""

from __future__ import annotations

import math
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

__all__ = [
    "ALPHA_BY_EDITION",
    "BETA",
    "CASE_PREFIXES",
    "CASE_ROW_COMMENTS",
    "CASE_TYPE_ORDER",
    "DEFAULT_INPUT_FILENAME",
    "DEFAULT_TEMPLATE_FILENAME",
    "DT",
    "EWM_ALPHA",
    "FALSE_TOKENS",
    "IECParameters",
    "IECWindWarning",
    "NONE_TOKENS",
    "PI",
    "TRUE_TOKENS",
    "TURB_I",
    "VALID_CATEGORIES",
    "VALID_CLASSES",
    "VALID_EDITIONS",
    "VCG",
    "VERSION",
    "VREF",
]


def _resolve_version() -> str:
    """Return the installed distribution version (the single source of truth).

    The version is declared once, in ``pyproject.toml``. Reading it back through
    package metadata guarantees code and packaging can never drift apart. When
    the package is run from a source tree without being installed, metadata is
    unavailable and we fall back to a clearly non-release marker.
    """

    try:
        return _distribution_version("pyiecwind")
    except PackageNotFoundError:  # pragma: no cover - only when running uninstalled
        return "0.0.0+unknown"


VERSION = _resolve_version()


class IECWindWarning(UserWarning):
    """Advisory warning for non-fatal IEC validation concerns.

    Emitted for inputs that are accepted but fall outside IEC guidance (for
    example an inclination angle beyond 8 deg). Callers who want strict
    behaviour can escalate these to errors::

        import warnings
        warnings.simplefilter("error", IECWindWarning)
    """


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


VALID_CLASSES = (1, 2, 3)
VALID_CATEGORIES = ("A", "B", "C")
VALID_EDITIONS = (1, 3)


@dataclass(frozen=True)
class IECParameters:
    """Validated, immutable input parameters stored internally in SI units.

    Construction is the single validation gate: every public path (the parser,
    the wizard, direct API use) goes through ``__post_init__``, which enforces the
    IEC turbine class/category/edition, finite and positive geometry, and a
    physically ordered cut-in < rated < cut-out speed range. A frozen dataclass
    with a tuple of ``conditions`` makes an invalid object impossible to create
    and impossible to mutate into one afterwards.

    Length and speed fields are stored in SI (m, m/s); ``si_unit`` only controls
    how values are rendered in output files and how condition-code speeds are
    interpreted.

    Parameters
    ----------
    si_unit : bool
        Render output in SI (m, m/s) when ``True``, English (ft, ft/s) when ``False``.
    t1 : float
        Transient start time [s].
    wtc : int
        IEC turbine class: 1, 2, or 3.
    catg : str
        Turbulence category: ``"A"``, ``"B"``, or ``"C"`` (normalised to upper case).
    slope_deg : float
        Inflow inclination angle [deg].
    iec_edition : int
        IEC 61400-1 edition for the power-law shear exponent: 1 or 3.
    hh : float
        Hub height [m].
    dia : float
        Rotor diameter [m]; must be positive and less than twice the hub height.
    vin, vrated, vout : float
        Cut-in, rated, and cut-out wind speeds [m/s]; must satisfy
        ``0 < vin < vrated < vout``.
    conditions : tuple of str, optional
        Condition codes to generate (e.g. ``("ECD+R", "EWM50")``). Stored as a tuple.

    Raises
    ------
    ValueError
        If any field is non-finite or out of its allowed range.
    """

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
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Normalise the category before validating, then freeze conditions as a tuple.
        object.__setattr__(self, "catg", str(self.catg).upper())
        object.__setattr__(self, "conditions", tuple(self.conditions))

        for name in ("t1", "slope_deg", "hh", "dia", "vin", "vrated", "vout"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{name} must be a finite number. Got: {value!r}")

        if self.wtc not in VALID_CLASSES:
            raise ValueError(f"Wind turbine class must be 1, 2, or 3. Got: {self.wtc!r}")
        if self.catg not in VALID_CATEGORIES:
            raise ValueError(f"Turbulence category must be A, B, or C. Got: {self.catg!r}")
        if self.iec_edition not in VALID_EDITIONS:
            raise ValueError(f"IEC edition must be 1 or 3. Got: {self.iec_edition!r}")

        if self.dia <= 0.0:
            raise ValueError(f"Rotor diameter must be positive. Got: {self.dia}")
        if self.hh <= self.dia / 2.0:
            raise ValueError(f"Hub height ({self.hh}) must be greater than rotor radius ({self.dia / 2.0:.3f}).")

        if not (0.0 < self.vin < self.vrated < self.vout):
            raise ValueError(
                "Operating speeds must satisfy 0 < cut-in < rated < cut-out. "
                f"Got vin={self.vin}, vrated={self.vrated}, vout={self.vout}."
            )

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
