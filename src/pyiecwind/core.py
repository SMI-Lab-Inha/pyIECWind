"""
IECWind (Python)
================
Generates IEC 61400-1 Ed.3 / IEC 61400-3 Ed.1 extreme wind condition
files (.WND) compatible with AeroDyn.

Translated from IECwind.f90 v5.01.02 (NREL/NWTC, Univ. of Utah /
Windward Engineering).

Usage
-----
    python iec_wind.py              # reads IEC.IPT in the current directory
    python iec_wind.py myinput.ipt  # reads a named file

Dependencies
------------
    numpy  (conda install numpy  OR  pip install numpy)

All internal calculations use SI units (m, m/s, radians).
Output is converted to the unit system chosen in the .IPT file.
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION = "1.0.0 (Python port of IECwind 5.01.02)"
DT      = 0.1    # output time step [s]
VCG     = 15.0   # coherent gust speed [m/s], fixed by IEC
BETA    = 6.4    # EWS shear definition constant
PI      = math.pi

# Reference extreme wind speeds [m/s] indexed by turbine class 1/2/3
VREF: dict[int, float] = {1: 50.0, 2: 42.5, 3: 37.5}

# Turbulence intensity by category
TURB_I: dict[str, float] = {"A": 0.16, "B": 0.14, "C": 0.12}

# Wind shear exponent by IEC edition
ALPHA_BY_EDITION: dict[int, float] = {1: 0.2, 3: 0.14}

# EWM uses a fixed shear exponent (IEC 61400-1 §6.3.2.1)
EWM_ALPHA = 0.11


# ---------------------------------------------------------------------------
# Input Parameters
# ---------------------------------------------------------------------------
@dataclass
class IECParameters:
    """
    All parameters read from the .IPT file.
    Physical quantities are stored in SI units (m, m/s).
    Derived quantities are computed as properties.
    """
    si_unit:     bool   # True = SI (m, m/s), False = English (ft, ft/s)
    t1:          float  # time at which transient starts [s]
    wtc:         int    # wind turbine class: 1, 2, or 3
    catg:        str    # turbulence category: 'A', 'B', or 'C'
    slope_deg:   float  # wind inflow inclination angle [deg]
    iec_edition: int    # IEC standard edition for shear exponent: 1 or 3
    hh:          float  # hub height [m]
    dia:         float  # rotor diameter [m]
    vin:         float  # cut-in wind speed [m/s]
    vrated:      float  # rated wind speed [m/s]
    vout:        float  # cut-out wind speed [m/s]
    conditions:  list[str] = field(default_factory=list)

    # -- Unit helpers --------------------------------------------------------

    @property
    def len_convert(self) -> float:
        """Factor to convert internal SI lengths/speeds to output units."""
        return 3.2808 if not self.si_unit else 1.0

    @property
    def spd_unit(self) -> str:
        return "m/s" if self.si_unit else "ft/s"

    @property
    def len_unit(self) -> str:
        return "m" if self.si_unit else "ft"

    # -- Derived physics -----------------------------------------------------

    @property
    def slope_rad(self) -> float:
        return math.radians(self.slope_deg)

    @property
    def turb_intensity(self) -> float:
        return TURB_I[self.catg.upper()]

    @property
    def alpha(self) -> float:
        """Wind shear exponent (power law), depends on IEC edition."""
        return ALPHA_BY_EDITION[self.iec_edition]

    @property
    def vref(self) -> float:
        """Reference extreme wind speed for the chosen turbine class [m/s]."""
        return VREF[self.wtc]

    @property
    def turb_scale(self) -> float:
        """Turbulence length scale Λ₁ [m], IEC 61400-1 §6.3."""
        return 0.7 * self.hh if self.hh < 60.0 else 42.0

    @property
    def turb_rat(self) -> float:
        """Diameter-to-scale ratio used in shear/gust calculations."""
        return self.dia / self.turb_scale

    @property
    def ve50(self) -> float:
        """50-year extreme wind speed at hub height [m/s]."""
        return 1.4 * self.vref

    @property
    def ve1(self) -> float:
        """1-year extreme wind speed at hub height [m/s]."""
        return 0.8 * self.ve50

    def summary(self) -> str:
        lc = self.len_convert
        lu = self.len_unit
        su = self.spd_unit
        lines = [
            f"  WTC={self.wtc}  CATG={self.catg}  Edition={self.iec_edition}",
            f"  HH={self.hh*lc:.1f} {lu}  Dia={self.dia*lc:.1f} {lu}",
            f"  Vin={self.vin*lc:.1f}  Vrated={self.vrated*lc:.1f}  Vout={self.vout*lc:.1f}  [{su}]",
            f"  TurbI={self.turb_intensity:.2f}  TurbScale={self.turb_scale:.1f} {lu}  "
            f"TurbRat={self.turb_rat:.3f}",
            f"  Vref={self.vref:.1f}  Ve50={self.ve50:.1f}  Ve1={self.ve1:.1f}  [{su}]",
            f"  Alpha={self.alpha}  Slope={self.slope_deg:.1f} deg",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Input File Parser
# ---------------------------------------------------------------------------
FIELD_ALIASES = {
    "si_unit": "si_unit",
    "si_units": "si_unit",
    "units": "si_unit",
    "t1": "t1",
    "transient_start_time": "t1",
    "transient_start": "t1",
    "wtc": "wtc",
    "wind_turbine_class": "wtc",
    "turbine_class": "wtc",
    "catg": "catg",
    "turbulence_category": "catg",
    "category": "catg",
    "slope": "slope_deg",
    "slope_deg": "slope_deg",
    "inflow_angle": "slope_deg",
    "inflow_inclination_deg": "slope_deg",
    "iec_edition": "iec_edition",
    "edition": "iec_edition",
    "hh": "hh",
    "hub_height": "hh",
    "hub_height_m_or_ft": "hh",
    "dia": "dia",
    "rotor_diameter": "dia",
    "diameter": "dia",
    "vin": "vin",
    "cut_in": "vin",
    "cut_in_speed": "vin",
    "vrated": "vrated",
    "rated_speed": "vrated",
    "vout": "vout",
    "cut_out": "vout",
    "cut_out_speed": "vout",
    "condition": "condition",
    "conditions": "conditions",
}

CASE_TYPE_ORDER = ["ECD", "EWS", "EOG", "EDC", "NWP", "EWM"]

CASE_ROW_COMMENTS = {
    "ECD": "Extreme Coherent Gust with Direction Change. Options: +R, -R, +R+du, +R-du, -R+du, -R-du, where du is a user-unit speed modifier",
    "EWS": "Extreme Wind Shear. Options: V+U, V-U, H+U, H-U, where U is a hub-height wind speed in the selected user units",
    "EOG": "Extreme Operating Gust. Options: I, O, R, R+du, R-du, where I=cut-in, O=cut-out, and R=rated",
    "EDC": "Extreme Direction Change. Options: +I, -I, +O, -O, +R, -R, +R+du, -R-du",
    "NWP": "Normal Wind Profile. Options: array of hub-height wind speeds in m/s, for example [4.0, 10.0, 23.7]",
    "EWM": "Extreme Wind Model. Options: 50 or 01, or an array such as [50, 01]",
}


def _normalize_key(raw: str) -> str:
    return raw.strip().lower().replace("-", "_").replace(" ", "_")


def _finalize_parsed_fields(fields: dict[str, str], conditions: list[str]) -> IECParameters:
    required = ["si_unit", "t1", "wtc", "catg", "slope_deg", "iec_edition", "hh", "dia", "vin", "vrated", "vout"]
    missing = [name for name in required if name not in fields]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Missing required input field(s): {missing_list}.")

    si_raw = fields["si_unit"].strip().upper()
    si_unit = si_raw in ("T", "TRUE", ".TRUE.", "YES", "Y", "SI", "METRIC")

    return _build_parameters(
        si_unit=si_unit,
        t1=float(fields["t1"]),
        wtc=int(fields["wtc"]),
        catg=fields["catg"],
        slope_deg=float(fields["slope_deg"]),
        iec_edition=int(fields["iec_edition"]),
        hh_raw=float(fields["hh"]),
        dia_raw=float(fields["dia"]),
        vin_raw=float(fields["vin"]),
        vrated_raw=float(fields["vrated"]),
        vout_raw=float(fields["vout"]),
        conditions=conditions,
    )


def _condition_description(code: str) -> str:
    """Return a concise human-readable description of a condition code."""
    code = code.upper()

    if re.match(r"^ECD([+-])R([+-]?\d*\.?\d*)$", code):
        direction = "positive" if "+" in code[3:4] else "negative"
        if code.endswith("R"):
            return f"enable ECD at Vrated with {direction} direction change"
        modifier = re.match(r"^ECD[+-]R([+-]?\d*\.?\d*)$", code).group(1)
        return f"enable ECD at Vrated{modifier} with {direction} direction change"

    m = re.match(r"^EWS([VH])([+-])(\d+\.?\d*)$", code)
    if m:
        axis = "vertical" if m.group(1) == "V" else "horizontal"
        direction = "positive" if m.group(2) == "+" else "negative"
        return f"enable {direction} {axis} extreme shear at {m.group(3)} user-unit wind speed"

    m = re.match(r"^EOG([IOR])([+-]?\d*\.?\d*)$", code)
    if m:
        ref_map = {"I": "cut-in", "O": "cut-out", "R": "rated"}
        ref = ref_map[m.group(1)]
        modifier = m.group(2)
        if m.group(1) == "R" and modifier:
            return f"enable extreme operating gust at {ref} speed with modifier {modifier}"
        return f"enable extreme operating gust at {ref} speed"

    m = re.match(r"^EDC([+-])([IOR])([+-]?\d*\.?\d*)$", code)
    if m:
        direction = "positive" if m.group(1) == "+" else "negative"
        ref_map = {"I": "cut-in", "O": "cut-out", "R": "rated"}
        ref = ref_map[m.group(2)]
        modifier = m.group(3)
        if m.group(2) == "R" and modifier:
            return f"enable {direction} extreme direction change at {ref} speed with modifier {modifier}"
        return f"enable {direction} extreme direction change at {ref} speed"

    m = re.match(r"^NWP(\d+\.?\d*)$", code)
    if m:
        return f"enable normal wind profile at {m.group(1)} m/s"

    m = re.match(r"^EWM(50|01)$", code)
    if m:
        recurrence = "50-year" if m.group(1) == "50" else "1-year"
        return f"enable {recurrence} extreme wind model"

    return "wind condition code"


def _normalize_case_options_text(text: str) -> str:
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    return text


def _split_case_options(text: str) -> list[str]:
    text = _normalize_case_options_text(text)
    if not text or text.upper() in {"NONE", "NULL"}:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _expand_case_row(case_type: str, options: list[str], *, lineno: int) -> list[str]:
    """Expand a case table row into concrete condition codes."""
    expanded: list[str] = []

    for option in options:
        upper = option.upper()
        if case_type == "ECD":
            expanded.append(f"ECD{upper}")
        elif case_type == "EWS":
            expanded.append(f"EWS{upper}")
        elif case_type == "EOG":
            expanded.append(f"EOG{upper}")
        elif case_type == "EDC":
            expanded.append(f"EDC{upper}")
        elif case_type == "NWP":
            expanded.append(f"NWP{option}")
        elif case_type == "EWM":
            expanded.append(f"EWM{upper}")
        else:
            raise ValueError(f"Unknown case type on line {lineno}: {case_type}")

    return expanded


def _parse_case_row(line: str, *, lineno: int) -> list[str]:
    """Parse a table row from the Cases block."""
    parts = re.split(r"\s{2,}", line, maxsplit=3)
    if len(parts) < 3:
        raise ValueError(
            f"Cannot parse case row on line {lineno}: {line!r}. "
            "Expected '<case_type><spaces><True/False/None><spaces><options>'."
        )

    case_type = parts[0].strip().upper()
    enabled = parts[1].strip().upper()
    options_text = parts[2].strip()

    if case_type not in CASE_TYPE_ORDER:
        raise ValueError(f"Unknown case type on line {lineno}: {case_type}")

    if enabled in {"NONE", "NULL"}:
        return []
    if enabled == "FALSE":
        return []
    if enabled != "TRUE":
        raise ValueError(
            f"Case enable flag on line {lineno} must be True, False, or None. Got: {parts[1]!r}"
        )

    options = _split_case_options(options_text)
    if not options:
        return []

    return _expand_case_row(case_type, options, lineno=lineno)


def _group_conditions_by_type(conditions: list[str]) -> dict[str, list[str]]:
    """Group full condition codes into per-family option lists."""
    grouped = {case_type: [] for case_type in CASE_TYPE_ORDER}

    for code in conditions:
        prefix = code[:3].upper()
        if prefix in grouped:
            grouped[prefix].append(code[3:])

    return grouped


def _parse_condition_value(value: str, *, lineno: int) -> str | None:
    """Parse a condition field with optional True/False/None toggle."""
    tokens = value.split()
    if not tokens:
        raise ValueError(f"Missing condition code on line {lineno}.")

    first = tokens[0].upper()
    if first in {"TRUE", "FALSE"}:
        if len(tokens) < 2:
            raise ValueError(
                f"Condition toggle on line {lineno} must be followed by a condition code."
            )
        return " ".join(tokens[1:]).upper() if first == "TRUE" else None

    if first in {"NONE", "NULL"}:
        return None

    return value.upper()


def _build_parameters(
    *,
    si_unit: bool,
    t1: float,
    wtc: int,
    catg: str,
    slope_deg: float,
    iec_edition: int,
    hh_raw: float,
    dia_raw: float,
    vin_raw: float,
    vrated_raw: float,
    vout_raw: float,
    conditions: list[str],
) -> IECParameters:
    """Validate parsed values and convert user-unit inputs to SI."""
    len_convert = 3.2808 if not si_unit else 1.0

    if wtc not in (1, 2, 3):
        raise ValueError(f"Wind turbine class must be 1, 2, or 3. Got: {wtc}")

    catg = catg.upper()
    if catg not in ("A", "B", "C"):
        raise ValueError(f"Turbulence category must be A, B, or C. Got: {catg!r}")

    if abs(slope_deg) > 8.0:
        print(
            f"WARNING: IEC specifies a maximum inclination angle of 8 deg.\n"
            f"         You specified {slope_deg:.2f} degrees."
        )

    if iec_edition not in (1, 3):
        print(
            f"WARNING: IEC edition should be 1 or 3. Got: {iec_edition}. "
            "Wind shear exponent will default to Alpha=0.14 (Ed.3)."
        )
        iec_edition = 3

    if dia_raw <= 0.0:
        raise ValueError(f"Rotor diameter must be positive. Got: {dia_raw}")
    if hh_raw <= dia_raw / 2.0:
        raise ValueError(
            f"Hub height ({hh_raw}) must be greater than rotor radius "
            f"({dia_raw / 2.0:.2f}). Check your input file."
        )

    hh = hh_raw / len_convert
    dia = dia_raw / len_convert
    vin = vin_raw / len_convert
    vrated = vrated_raw / len_convert
    vout = vout_raw / len_convert

    if vrated <= vin:
        raise ValueError(
            f"Rated speed ({vrated:.2f}) must exceed cut-in ({vin:.2f})."
        )
    if vout <= vrated:
        raise ValueError(
            f"Cut-out speed ({vout:.2f}) must exceed rated ({vrated:.2f})."
        )
    if not conditions:
        raise ValueError("No wind conditions found in input file.")

    return IECParameters(
        si_unit=si_unit,
        t1=t1,
        wtc=wtc,
        catg=catg,
        slope_deg=slope_deg,
        iec_edition=iec_edition,
        hh=hh,
        dia=dia,
        vin=vin,
        vrated=vrated,
        vout=vout,
        conditions=conditions,
    )


def _parse_legacy_input_file(raw_lines: list[str]) -> IECParameters:
    """Parse the original fixed-line IECWind .IPT layout."""
    # Pad to at least 17 lines so we never get IndexError before the loop
    while len(raw_lines) < 17:
        raw_lines.append("")

    def first_token(line: str) -> str:
        """Return the first whitespace-delimited token on a line."""
        tokens = line.strip().split()
        if not tokens:
            raise ValueError(f"Expected a value but got an empty line: {line!r}")
        return tokens[0]

    def line_val(idx: int, name: str) -> str:
        try:
            return first_token(raw_lines[idx])
        except (IndexError, ValueError):
            raise ValueError(f"Premature end of file reading '{name}' at line {idx + 1}.")

    si_raw = line_val(2, "units specifier").upper()
    si_unit = si_raw in ("T", "TRUE", ".TRUE.")
    t1 = float(line_val(3, "transient start time"))
    wtc = int(line_val(5, "wind turbine class"))
    catg = line_val(6, "turbulence category")
    slope_deg = float(line_val(7, "wind inflow angle"))
    iec_edition = int(line_val(8, "IEC edition for wind shear exponent"))
    hh_raw = float(line_val(10, "hub height"))
    dia_raw = float(line_val(11, "rotor diameter"))
    vin_raw = float(line_val(12, "cut-in wind speed"))
    vrated_raw = float(line_val(13, "rated wind speed"))
    vout_raw = float(line_val(14, "cut-out wind speed"))

    conditions: list[str] = []
    for raw in raw_lines[16:]:
        stripped = raw.strip()
        if not stripped:
            break
        conditions.append(stripped.upper())

    return _build_parameters(
        si_unit=si_unit,
        t1=t1,
        wtc=wtc,
        catg=catg,
        slope_deg=slope_deg,
        iec_edition=iec_edition,
        hh_raw=hh_raw,
        dia_raw=dia_raw,
        vin_raw=vin_raw,
        vrated_raw=vrated_raw,
        vout_raw=vout_raw,
        conditions=conditions,
    )


def _parse_keyed_input_file(raw_lines: list[str]) -> IECParameters:
    """Parse a friendlier key/value IECWind input file."""
    fields: dict[str, str] = {}
    conditions: list[str] = []
    in_conditions = False

    for lineno, raw_line in enumerate(raw_lines, start=1):
        content = raw_line.split("!", 1)[0].split("#", 1)[0].strip()
        if not content:
            continue

        if in_conditions:
            item = content.lstrip("-*").strip()
            if not item:
                continue
            conditions.append(item.upper())
            continue

        if "=" in content:
            key, value = content.split("=", 1)
        elif ":" in content:
            key, value = content.split(":", 1)
        else:
            raise ValueError(
                f"Cannot parse line {lineno}: {raw_line!r}. "
                "Use 'key = value' entries or a 'conditions:' block."
            )

        key = FIELD_ALIASES.get(_normalize_key(key))
        if key is None:
            raise ValueError(f"Unknown input key on line {lineno}: {raw_line!r}")

        value = value.strip()
        if key == "conditions":
            in_conditions = True
            if value:
                inline_items = re.split(r"[,\s]+", value)
                conditions.extend(item.upper() for item in inline_items if item)
            continue

        if key == "condition":
            parsed = _parse_condition_value(value, lineno=lineno)
            if parsed is not None:
                conditions.append(parsed)
            continue

        if not value:
            raise ValueError(f"Missing value for '{key}' on line {lineno}.")
        fields[key] = value

    return _finalize_parsed_fields(fields, conditions)


def _parse_openfast_input_file(raw_lines: list[str]) -> IECParameters:
    """Parse OpenFAST-style value/key/comment input lines."""
    fields: dict[str, str] = {}
    conditions: list[str] = []
    in_cases_section = False

    for lineno, raw_line in enumerate(raw_lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith(("!", "#")):
            if stripped.upper().startswith("! CASES"):
                in_cases_section = True
            continue

        if in_cases_section:
            first_token = re.split(r"\s+", stripped, maxsplit=1)[0].upper()
            if first_token in CASE_TYPE_ORDER:
                conditions.extend(_parse_case_row(stripped, lineno=lineno))
                continue

        parts = re.split(r"\s{2,}", stripped, maxsplit=2)
        if len(parts) < 2:
            raise ValueError(
                f"Cannot parse OpenFAST-style line {lineno}: {raw_line!r}. "
                "Expected '<value><spaces><key><spaces>- comment>'."
            )

        value = parts[0].strip()
        key = FIELD_ALIASES.get(_normalize_key(parts[1]))
        if key is None:
            raise ValueError(f"Unknown input key on line {lineno}: {raw_line!r}")

        if key in {"condition", "conditions"}:
            parsed = _parse_condition_value(value, lineno=lineno)
            if parsed is not None:
                conditions.append(parsed)
            continue

        if not value:
            raise ValueError(f"Missing value for '{key}' on line {lineno}.")
        fields[key] = value

    return _finalize_parsed_fields(fields, conditions)


def parse_input_file(filepath: str | Path = "IEC.IPT") -> IECParameters:
    """
    Parse an IECWind .IPT input file.

    The file format (by line number):
        1      Header comment (skipped)
        2      Header comment (skipped)
        3      SI_UNIT  True/False
        4      T1       transient start time [s]
        5      Header comment (skipped)
        6      WTC      wind turbine class (1/2/3)
        7      CATG     turbulence category (A/B/C)
        8      SLOPE    inflow angle [deg]
        9      EDITION  IEC standard for shear exponent (1 or 3)
        10     Header comment (skipped)
        11     HH       hub height
        12     DIA      rotor diameter
        13     VIN      cut-in wind speed
        14     VRATED   rated wind speed
        15     VOUT     cut-out wind speed
        16     Header comment (skipped)
        17+    Condition codes, one per line (blank lines terminate)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find input file '{path}'. "
            "Ensure IEC.IPT is in the current working directory."
        )

    raw_lines = path.read_text(encoding="utf-8").splitlines()

    keyed_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_ -]*\s*(=|:)\s*.*$")
    openfast_pattern = re.compile(r"^\S+\s{2,}[A-Za-z_][A-Za-z0-9_ -]*\s*(?:\s+-.*)?$")
    keyed_format = any(
        stripped
        and not stripped.startswith(("!", "#"))
        and keyed_pattern.match(stripped)
        for stripped in (line.strip() for line in raw_lines)
    )
    openfast_format = any(
        stripped
        and not stripped.startswith(("!", "#"))
        and openfast_pattern.match(stripped)
        for stripped in (line.strip() for line in raw_lines)
    )

    if openfast_format:
        params = _parse_openfast_input_file(raw_lines)
    elif keyed_format:
        params = _parse_keyed_input_file(raw_lines)
    else:
        params = _parse_legacy_input_file(raw_lines)

    print(f"Read {len(params.conditions)} condition(s) from '{path}'.")
    return params


# ---------------------------------------------------------------------------
# .WND File Writer
# ---------------------------------------------------------------------------
class WindFileWriter:
    """
    Builds an AeroDyn-compatible .WND file line by line, then writes it.

    Columns (tab-separated, 9.3f format):
        Time | WindSpeed | WindDir | VertSpeed | HorizShear |
        PwrLawVertShr (Alpha) | LinVertShear | GustSpeed
    """

    TAB = "\t"

    def __init__(self, filepath: Path, p: IECParameters) -> None:
        self.filepath = filepath
        self.p = p
        self._lines: list[str] = []

    # -- Internal helpers ----------------------------------------------------

    def _w(self, text: str = "") -> None:
        self._lines.append(text)

    # -- Header sections -----------------------------------------------------

    def file_header(self) -> None:
        self._w(f"!This file was generated by IECwind (Python) v{VERSION}.")
        self._w("! Wind condition defined by IEC 61400-1 3rd EDITION.")

    def wind_header(self, condition_name: str) -> None:
        p = self.p
        lc, lu = p.len_convert, p.len_unit
        self._w(
            f"! for IEC Turbine Class {p.wtc} "
            f"and IEC Turbulence Category {p.catg.upper()}"
        )
        self._w("!----------------------------------------------------------")
        self._w(f"! Rotor diameter = {p.dia * lc:.1f} {lu}.")
        self._w(
            f"! {p.hh * lc:.1f} {lu} hub-height yields  "
            f"{p.turb_scale:.1f} {lu} turbulence scale."
        )
        self._w("!----------------------------------------------------------")
        self._w(f"! IEC Condition: {condition_name}.")
        self._w("! Stats for this wind file:")

    def time_header(self, duration: float) -> None:
        self._w(f"!     The transient occurs over {duration:.1f} seconds.")

    def gust_header(self, v_gust_max: float, vhub: float, t_max: float) -> None:
        p = self.p
        lc, su = p.len_convert, p.spd_unit
        self._w("!")
        self._w(f"!     The maximum gust speed is {v_gust_max * lc:.3f} {su}.")
        self._w(
            f"!     The maximum total wind speed is "
            f"{(v_gust_max + vhub) * lc:.3f} {su}."
        )
        self._w(f"!     This maximum occurs at {t_max:.3f} seconds.")

    def direction_header(self, max_dir_deg: float, t_max: float) -> None:
        self._w("!")
        self._w(f"!     The extreme direction change is {max_dir_deg:.2f} degrees.")
        self._w(f"!     This extreme occurs at {t_max:.2f} seconds.")

    def shear_header(
        self,
        dir_sign: float,
        is_horizontal: bool,
        shr_max: float,
        t_max: float,
    ) -> None:
        orient = "horizontal" if is_horizontal else "vertical"
        sign_word = "positive" if dir_sign > 0.0 else "negative"
        self._w("!")
        self._w(
            f"!     The extreme linear {orient} wind shear is "
            f"{dir_sign * shr_max:.3f}."
        )
        self._w(f"!     This extreme occurs at {t_max:.2f} seconds.")
        self._w(f"!     This sign of the shear is {sign_word}.")

    def slope_header(self) -> None:
        self._w("!")
        self._w(
            f"!     The wind inflow inclination angle is "
            f"{self.p.slope_deg:.1f} degrees to the horizontal."
        )

    def nwp_header(self, vhub: float) -> None:
        p = self.p
        self._w(f"!     The steady wind speed is {vhub * p.len_convert:.2f} {p.spd_unit}.")

    def ewm_header(self, vhub: float) -> None:
        p = self.p
        self._w(
            f"!     The steady extreme wind speed is "
            f"{vhub * p.len_convert:.2f} {p.spd_unit}."
        )

    def col_headers(self) -> None:
        t   = self.TAB
        su  = f"({self.p.spd_unit})"
        self._w("!----------------------------------------------------------")
        self._w(
            f"! Time{t}Wind{t}Wind{t}Vertical{t}Horiz.{t}"
            f"Pwr.Law{t}Lin.Vert.{t}Gust"
        )
        self._w(
            f"!{t}Speed{t}Dir{t}Speed{t}Shear{t}"
            f"Vert.Shr{t}Shear{t}Speed"
        )
        self._w(f"!(sec){t}{su}{t}(deg){t}{su}{t}{t}{t}{t}{su}")

    # -- Data rows -----------------------------------------------------------

    def data_row(
        self,
        time:           float,
        wind_spd:       float,   # m/s  (internal SI, converted to output)
        wind_dir:       float,   # deg  (no conversion)
        vert_spd:       float,   # m/s  (internal SI, converted to output)
        horiz_shear:    float,   # dimensionless
        alpha:          float,   # dimensionless
        lin_vert_shear: float,   # dimensionless
        gust_spd:       float,   # m/s  (internal SI, converted to output)
    ) -> None:
        lc = self.p.len_convert
        t  = self.TAB
        vals = [
            time,
            wind_spd       * lc,
            wind_dir,
            vert_spd       * lc,
            horiz_shear,
            alpha,
            lin_vert_shear,
            gust_spd       * lc,
        ]
        self._lines.append(t.join(f"{v:9.3f}" for v in vals))

    # -- Finalise ------------------------------------------------------------

    def save(self) -> None:
        self.filepath.write_text("\n".join(self._lines) + "\n", encoding="utf-8")
        print(f"  Generated: {self.filepath.name}")


# ---------------------------------------------------------------------------
# Physics helpers
# ---------------------------------------------------------------------------

def _transient_times(t1: float, duration: float) -> np.ndarray:
    """
    Array of output times during the transient phase.
    Starts at t1, ends at approximately t1+duration, step DT.
    Length = round(duration/DT) + 1  (matches Fortran NINT(T/DT)+1).
    """
    nt = round(duration / DT) + 1
    return t1 + np.arange(nt) * DT


def _hub_components(vhub: float, slope_rad: float) -> tuple[float, float]:
    """Split hub-height wind speed into horizontal and vertical components."""
    return vhub * math.cos(slope_rad), vhub * math.sin(slope_rad)


def _sigma1(turb_i: float, vhub: float) -> float:
    """Longitudinal turbulence standard deviation σ₁, IEC 61400-1 §6.3."""
    return turb_i * (0.75 * vhub + 5.6)


# ---------------------------------------------------------------------------
# Condition Generators
# ---------------------------------------------------------------------------

def gen_ecd(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Extreme Coherent Gust with Direction Change (ECD).

    Code format:  ECD[+/-]R[±spd_mod]
      [+/-]     direction of the yaw excursion
      R         speed is relative to Vrated
      [±spd_mod] optional speed modifier in user units, |mod| ≤ 2 m/s (6.5 ft/s)

    Transient duration: 10 s
    Physics (IEC 61400-1 §6.3.2.4):
        V_cg(t) = 0.5 * VCG * (1 - cos(π·t/T))
        θ(t)    = 0.5 * Theta * (1 - cos(π·t/T))
        Theta   = 180° if Vhub ≤ 4 m/s,  else 720/Vhub  [deg]
    """
    m = re.match(r"^ECD([+-])R([+-]?\d*\.?\d*)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse ECD condition '{code}'. "
            "Expected format: ECD[+/-]R[±speed_modifier]"
        )

    dir_sign  = 1.0 if m.group(1) == "+" else -1.0
    spd_str   = m.group(2)
    spd_mod   = (float(spd_str) / p.len_convert) if spd_str else 0.0

    if abs(spd_mod) > 2.0:
        raise ValueError(
            f"ECD speed modifier must not exceed ±2.0 m/s (±6.5 ft/s). "
            f"Got: {spd_mod * p.len_convert:.2f} {p.spd_unit}  [{code}]"
        )

    vhub = p.vrated + spd_mod
    if vhub > p.vref:
        raise ValueError(
            f"ECD: Vhub ({vhub:.2f} m/s) exceeds Vref ({p.vref:.2f} m/s). [{code}]"
        )

    vhub_h, vhub_v0 = _hub_components(vhub, p.slope_rad)

    # Extreme direction change angle [deg]
    theta = 180.0 if vhub <= 4.0 else 720.0 / vhub
    theta *= dir_sign

    T     = 10.0
    times = _transient_times(p.t1, T)
    tau   = times - p.t1                           # local transient time [s]

    vgust   = 0.5 * VCG * (1.0 - np.cos(PI * tau / T))
    vgust_h = vgust * math.cos(p.slope_rad)        # horizontal gust component
    vhub_v  = (vhub + vgust) * math.sin(p.slope_rad)  # total vertical speed
    theta_t = 0.5 * theta * (1.0 - np.cos(PI * tau / T))

    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header("Extreme Coherent Gust with Direction Change")
    w.time_header(T)
    w.gust_header(VCG, vhub, p.t1 + T)
    w.direction_header(theta, p.t1 + T)
    w.slope_header()
    w.col_headers()

    # t=0 steady row (before transient)
    w.data_row(0.0, vhub_h, 0.0, vhub_v0, 0.0, p.alpha, 0.0, 0.0)
    # Transient rows: t = T1 … T1+T
    for i, t in enumerate(times):
        w.data_row(
            t, vhub_h, float(theta_t[i]), float(vhub_v[i]),
            0.0, p.alpha, 0.0, float(vgust_h[i]),
        )
    w.save()


def gen_ews(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Extreme Wind Shear (EWS) — horizontal or vertical.

    Code format:  EWS[V/H][+/-][nn.n]
      V/H       vertical or horizontal shear
      [+/-]     shear direction
      [nn.n]    hub-height wind speed in user units

    Transient duration: 12 s
    Physics (IEC 61400-1 §6.3.2.5):
        σ₁     = TurbI * (0.75*Vhub + 5.6)
        VG50   = β * σ₁   (β = 6.4)
        ShrMax = 2*(2.5 + 0.2*VG50*TurbRat^0.25) / Vhub
        Shr(t) = ±(ShrMax/2) * (1 - cos(2π·t/T))
    """
    m = re.match(r"^EWS([VH])([+-])(\d+\.?\d*)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse EWS condition '{code}'. "
            "Expected format: EWS[V/H][+/-][wind_speed]"
        )

    is_horizontal = m.group(1) == "H"
    dir_sign      = 1.0 if m.group(2) == "+" else -1.0
    vhub          = float(m.group(3)) / p.len_convert   # convert to SI

    if vhub < p.vin or vhub > p.vout:
        raise ValueError(
            f"EWS wind speed ({vhub * p.len_convert:.1f} {p.spd_unit}) must be "
            f"between Vin ({p.vin * p.len_convert:.1f}) and "
            f"Vout ({p.vout * p.len_convert:.1f}). [{code}]"
        )

    vhub_h, vhub_v = _hub_components(vhub, p.slope_rad)

    sig1   = _sigma1(p.turb_intensity, vhub)
    vg50   = BETA * sig1
    shr_max = 2.0 * (2.5 + 0.2 * vg50 * p.turb_rat ** 0.25) / vhub

    T     = 12.0
    times = _transient_times(p.t1, T)
    tau   = times - p.t1

    shear = dir_sign * 0.5 * shr_max * (1.0 - np.cos(2.0 * PI * tau / T))
    h_shr = shear if is_horizontal else np.zeros_like(shear)
    v_shr = shear if not is_horizontal else np.zeros_like(shear)

    orient = "Horizontal" if is_horizontal else "Vertical"
    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header(f"Extreme {orient} Wind Shear")
    w.time_header(T)
    w.shear_header(dir_sign, is_horizontal, shr_max, p.t1 + T)
    w.slope_header()
    w.col_headers()

    # t=0 steady row
    w.data_row(0.0, vhub_h, 0.0, vhub_v, 0.0, p.alpha, 0.0, 0.0)
    # Transient rows
    for i, t in enumerate(times):
        w.data_row(
            t, vhub_h, 0.0, vhub_v,
            float(h_shr[i]), p.alpha, float(v_shr[i]), 0.0,
        )
    w.save()


def gen_eog(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Extreme Operating Gust (EOG).

    Code format:  EOG[I/O/R][±spd_mod]
      I         Vhub = Vin
      O         Vhub = Vout
      R[±mod]   Vhub = Vrated ± modifier (user units, |mod| ≤ 2 m/s)

    Transient duration: 10.5 s
    Physics (IEC 61400-1 §6.3.2.2):
        σ₁    = TurbI * (0.75*Vhub + 5.6)
        Vgust = min(1.35*(Ve1 - Vhub),  3.3*σ₁/(1 + 0.1*TurbRat))
        u(t)  = Vhub - 0.37*Vgust*sin(3π·t/T)*(1 - cos(2π·t/T))
    """
    m = re.match(r"^EOG([IOR])([+-]?\d*\.?\d*)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse EOG condition '{code}'. "
            "Expected format: EOG[I/O/R][±speed_modifier]"
        )

    speed_key = m.group(1)
    spd_str   = m.group(2)

    if speed_key == "I":
        vhub = p.vin
    elif speed_key == "O":
        vhub = p.vout
    else:  # 'R'
        spd_mod = (float(spd_str) / p.len_convert) if spd_str else 0.0
        if abs(spd_mod) > 2.0:
            raise ValueError(
                f"EOG speed modifier must not exceed ±2.0 m/s. "
                f"Got: {spd_mod * p.len_convert:.2f} {p.spd_unit}  [{code}]"
            )
        vhub = p.vrated + spd_mod

    vhub_h, vhub_v0 = _hub_components(vhub, p.slope_rad)

    sig1  = _sigma1(p.turb_intensity, vhub)
    vgust = min(1.35 * (p.ve1 - vhub), 3.3 * sig1 / (1.0 + 0.1 * p.turb_rat))

    T     = 10.5
    times = _transient_times(p.t1, T)
    tau   = times - p.t1

    # Gust perturbation (horizontal component only)
    gust_factor = -0.37 * vgust * np.sin(3.0 * PI * tau / T) * (1.0 - np.cos(2.0 * PI * tau / T))
    vgust_h     = gust_factor * math.cos(p.slope_rad)
    vhub_v      = (vhub + gust_factor) * math.sin(p.slope_rad)

    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header("Extreme Operating Gust")
    w.time_header(T)
    w.gust_header(2 * 0.37 * vgust, vhub, p.t1 + 0.5 * T)
    w.slope_header()
    w.col_headers()

    w.data_row(0.0, vhub_h, 0.0, vhub_v0, 0.0, p.alpha, 0.0, 0.0)
    for i, t in enumerate(times):
        w.data_row(
            t, vhub_h, 0.0, float(vhub_v[i]),
            0.0, p.alpha, 0.0, float(vgust_h[i]),
        )
    w.save()


def gen_edc(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Extreme Direction Change (EDC).

    Code format:  EDC[+/-][I/O/R][±spd_mod]
      [+/-]     direction of the yaw excursion
      I/O/R     Vin / Vout / Vrated ± modifier

    Transient duration: 6 s
    Physics (IEC 61400-1 §6.3.2.3):
        σ₁    = TurbI * (0.75*Vhub + 5.6)
        Theta = 4 * atan(σ₁ / (Vhub*(1 + 0.1*TurbRat)))  [deg]
        θ(t)  = 0.5 * Theta * (1 - cos(π·t/T))
    """
    m = re.match(r"^EDC([+-])([IOR])([+-]?\d*\.?\d*)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse EDC condition '{code}'. "
            "Expected format: EDC[+/-][I/O/R][±speed_modifier]"
        )

    dir_sign  = 1.0 if m.group(1) == "+" else -1.0
    speed_key = m.group(2)
    spd_str   = m.group(3)

    if speed_key == "I":
        vhub = p.vin
    elif speed_key == "O":
        vhub = p.vout
    else:  # 'R'
        spd_mod = (float(spd_str) / p.len_convert) if spd_str else 0.0
        if abs(spd_mod) > 2.0:
            raise ValueError(
                f"EDC speed modifier must not exceed ±2.0 m/s. "
                f"Got: {spd_mod * p.len_convert:.2f} {p.spd_unit}  [{code}]"
            )
        vhub = p.vrated + spd_mod

    vhub_h, vhub_v = _hub_components(vhub, p.slope_rad)

    sig1  = _sigma1(p.turb_intensity, vhub)
    theta = 4.0 * math.atan(sig1 / (vhub * (1.0 + 0.1 * p.turb_rat)))
    theta = math.degrees(theta) * dir_sign          # convert rad → deg, apply sign

    T     = 6.0
    times = _transient_times(p.t1, T)
    tau   = times - p.t1

    theta_t = 0.5 * theta * (1.0 - np.cos(PI * tau / T))

    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header("Extreme Direction Change")
    w.time_header(T)
    w.direction_header(theta, p.t1 + T)
    w.slope_header()
    w.col_headers()

    w.data_row(0.0, vhub_h, 0.0, vhub_v, 0.0, p.alpha, 0.0, 0.0)
    for i, t in enumerate(times):
        w.data_row(t, vhub_h, float(theta_t[i]), vhub_v, 0.0, p.alpha, 0.0, 0.0)
    w.save()


def gen_nwp(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Normal Wind Profile (NWP) — single steady-state row.

    Code format:  NWP[nn.n]
      [nn.n]    hub-height wind speed in m/s (no unit conversion applied,
                matching original Fortran behaviour).

    This produces a single-row file representing a steady wind state with
    the given hub-height speed and the normal power-law shear profile.
    """
    m = re.match(r"^NWP(\d+\.?\d*)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse NWP condition '{code}'. "
            "Expected format: NWP[wind_speed_in_m/s]"
        )

    # NOTE: Original Fortran does NOT apply a unit conversion here.
    # The speed in the condition code is treated as m/s regardless of SIUnit.
    vhub = float(m.group(1))
    vhub_h, vhub_v = _hub_components(vhub, p.slope_rad)

    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header("Normal Wind Profile")
    w.nwp_header(vhub)
    w.slope_header()
    w.col_headers()

    w.data_row(0.0, vhub_h, 0.0, vhub_v, 0.0, p.alpha, 0.0, 0.0)
    w.save()


def gen_ewm(code: str, p: IECParameters, output_dir: str | Path | None = None) -> None:
    """
    Extreme Wind Model (EWM) — single steady-state row.

    Code format:  EWM[50/01]
      50   →  50-year recurrence: Vhub = Ve50 = 1.4 * Vref
      01   →  1-year  recurrence: Vhub = Ve1  = 0.8 * Ve50

    Uses a fixed shear exponent of 0.11 (IEC 61400-1 §6.3.2.1),
    independent of the Alpha setting.
    """
    m = re.match(r"^EWM(50|01)$", code)
    if not m:
        raise ValueError(
            f"Cannot parse EWM condition '{code}'. "
            "Expected format: EWM50 or EWM01"
        )

    period = m.group(1)
    if period == "50":
        vhub    = p.ve50
        rec_str = "50-year"
    else:
        vhub    = p.ve1
        rec_str = "1-year"

    vhub_h, vhub_v = _hub_components(vhub, p.slope_rad)

    w = WindFileWriter(_resolve_output_path(code, output_dir), p)
    w.file_header()
    w.wind_header(f"{rec_str} Extreme Wind Model")
    w.ewm_header(vhub)
    w.slope_header()
    w.col_headers()

    # EWM uses fixed shear exponent 0.11, not the general alpha
    w.data_row(0.0, vhub_h, 0.0, vhub_v, 0.0, EWM_ALPHA, 0.0, 0.0)
    w.save()


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_GENERATORS = {
    "ECD": gen_ecd,
    "EWS": gen_ews,
    "EOG": gen_eog,
    "EDC": gen_edc,
    "NWP": gen_nwp,
    "EWM": gen_ewm,
}


def _resolve_output_path(code: str, output_dir: str | Path | None = None) -> Path:
    """Return the destination path for a generated condition file."""
    if output_dir is None:
        return Path(f"{code}.wnd")

    dest_dir = Path(output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    return dest_dir / f"{code}.wnd"


def generate_all(p: IECParameters, output_dir: str | Path | None = None) -> int:
    """
    Generate .WND files for every condition listed in p.conditions.
    Returns the number of files successfully written.
    """
    count = 0
    for code in p.conditions:
        prefix = code[:3]
        generator = _GENERATORS.get(prefix)
        if generator is None:
            print(
                f"ERROR: Unknown condition type '{prefix}' in code '{code}'. "
                "Skipping."
            )
            continue
        try:
            generator(code, p, output_dir=output_dir)
            count += 1
        except ValueError as exc:
            print(f"ERROR generating '{code}': {exc}")
    return count


def generate_from_input_file(
    input_file: str | Path = "IEC.IPT",
    *,
    output_dir: str | Path | None = None,
) -> tuple[IECParameters, int]:
    """Parse an input file and generate all requested wind files."""
    params = parse_input_file(input_file)
    return params, generate_all(params, output_dir=output_dir)


# ---------------------------------------------------------------------------
# Template Generator
# ---------------------------------------------------------------------------

_TEMPLATE = """\
! ============================================================
!  IECWind input file  (.IPT)
!  Used by:  python iec_wind.py [this_file.ipt]
!  Run       python iec_wind.py --template  to regenerate this file.
! ============================================================

! ── OUTPUT UNITS ────────────────────────────────────────────
! Choose whether all lengths and speeds are in SI or English.
!   True  → metres (m) and metres-per-second (m/s)   [recommended]
!   False → feet (ft) and feet-per-second (ft/s)
! All values below (hub height, diameter, wind speeds) must be
! in the units selected here.
True        SI_UNIT: True = SI (m, m/s) | False = English (ft, ft/s)

! ── TRANSIENT START TIME ────────────────────────────────────
! Steady wind is held from t = 0 until this time, then the
! transient condition (gust, shear, direction change) begins.
! Typical value: 30–60 s, giving AeroDyn time to reach a
! periodic steady state before the extreme event.
40.0        T1: time at which the transient starts [s]

! ── WIND TURBINE CLASS ──────────────────────────────────────
! Determines the reference extreme wind speed (Vref):
!   Class 1  →  Vref = 50.0 m/s  (high-wind site)
!   Class 2  →  Vref = 42.5 m/s  (medium-wind site)
!   Class 3  →  Vref = 37.5 m/s  (low-wind site)
! From Vref the tool computes:
!   Ve50 = 1.4 × Vref   (50-year extreme wind speed)
!   Ve1  = 0.8 × Ve50   (1-year  extreme wind speed)
2           WTC: wind turbine class (1, 2, or 3)

! ── TURBULENCE CATEGORY ─────────────────────────────────────
! Sets the turbulence intensity (I_ref) used in σ₁ = I_ref×(0.75×V+5.6):
!   A  →  I_ref = 0.16  (higher turbulence)
!   B  →  I_ref = 0.14  (medium turbulence)   ← most common
!   C  →  I_ref = 0.12  (lower turbulence)
B           CATG: turbulence category (A, B, or C)

! ── WIND INFLOW INCLINATION ANGLE ───────────────────────────
! Angle between the mean wind direction and the horizontal plane.
! IEC 61400-1 specifies ±8° as the maximum.
! Use 0.0 for flat terrain (most onshore sites).
! Positive = upward flow; negative = downward flow.
0.0         SLOPE: inflow inclination angle [deg]  (-8 to +8)

! ── IEC EDITION FOR WIND SHEAR EXPONENT ─────────────────────
! Selects the power-law wind shear exponent (α) used in the
! Normal Wind Profile and extreme condition files:
!   1  →  α = 0.20   (IEC 61400-1 Edition 1)
!   3  →  α = 0.14   (IEC 61400-1 Edition 3)   ← current standard
! Note: EWM files always use α = 0.11 regardless of this setting.
3           IEC_EDITION: standard for wind shear exponent (1 or 3)

! ── TURBINE GEOMETRY ────────────────────────────────────────
! Enter values in the unit system chosen above (SI or English).
! Hub height must be greater than rotor radius (Dia/2).
80.0        HH:  hub height                    [m or ft]
80.0        DIA: rotor diameter                [m or ft]

! ── OPERATIONAL WIND SPEEDS ─────────────────────────────────
! Enter values in the unit system chosen above (SI or English).
! Must satisfy:  Vin < Vrated < Vout
4.0         VIN:    cut-in  wind speed          [m/s or ft/s]
10.0        VRATED: rated   wind speed          [m/s or ft/s]
24.0        VOUT:   cut-out wind speed          [m/s or ft/s]

! ── CONDITIONS TO GENERATE ──────────────────────────────────
! List one condition code per line.
! A separate .WND file is created for each code.
! Codes are case-insensitive.  Blank line ends the list.
!
! ┌─────────────────────────────────────────────────────────┐
! │  CONDITION CODE REFERENCE                               │
! ├────────┬────────────────────────────────────────────────┤
! │  ECD   │  Extreme Coherent Gust with Direction Change   │
! │  EWS   │  Extreme Wind Shear                            │
! │  EOG   │  Extreme Operating Gust                        │
! │  EDC   │  Extreme Direction Change                      │
! │  NWP   │  Normal Wind Profile  (steady, no transient)   │
! │  EWM   │  Extreme Wind Model   (steady, no transient)   │
! └────────┴────────────────────────────────────────────────┘
!
! ── ECD  Extreme Coherent Gust with Direction Change ────────
!  Format:  ECD [dir] R [speed_mod]
!
!  [dir]       Direction of the yaw excursion
!                +  →  positive (clockwise viewed from above)
!                -  →  negative (counter-clockwise)
!
!  R           Wind speed is relative to Vrated.
!              (Always R; only rated-speed ECD is defined by IEC.)
!
!  [speed_mod] Optional speed offset from Vrated, in user units.
!              Allowed range: -2.0 to +2.0 m/s  (or -6.5 to +6.5 ft/s).
!              Omit for exactly Vrated.
!
!  Physics: V_cg(t) = 0.5×15×(1−cos(π·t/10))          [m/s, T=10 s]
!           θ(t)    = 0.5×Θ×(1−cos(π·t/10))             [deg]
!           Θ = 180° if Vhub ≤ 4 m/s, else Θ = 720/Vhub
!
!  Examples:
ECD+R         ! +direction, Vhub = Vrated
ECD-R         ! −direction, Vhub = Vrated
ECD+R+2.0     ! +direction, Vhub = Vrated + 2.0 m/s
ECD+R-2.0     ! +direction, Vhub = Vrated − 2.0 m/s
ECD-R+2.0     ! −direction, Vhub = Vrated + 2.0 m/s
ECD-R-2.0     ! −direction, Vhub = Vrated − 2.0 m/s
!
! ── EWS  Extreme Wind Shear ─────────────────────────────────
!  Format:  EWS [plane] [dir] [speed]
!
!  [plane]  Shear plane:
!             V  →  vertical   shear  (wind speed varies with height)
!             H  →  horizontal shear  (wind speed varies across rotor)
!
!  [dir]    Shear direction:
!             +  →  positive (faster wind at top / right)
!             -  →  negative (faster wind at bottom / left)
!
!  [speed]  Hub-height wind speed in user units.
!           Must be between Vin and Vout (inclusive).
!
!  Physics: Shr(t) = ±(ShrMax/2)×(1−cos(2π·t/12))     [T=12 s]
!
!  Examples:
EWSV+12.0     ! vertical shear,   positive, Vhub = 12.0 m/s
EWSV-12.0     ! vertical shear,   negative, Vhub = 12.0 m/s
EWSH+12.0     ! horizontal shear, positive, Vhub = 12.0 m/s
EWSH-12.0     ! horizontal shear, negative, Vhub = 12.0 m/s
!
! ── EOG  Extreme Operating Gust ─────────────────────────────
!  Format:  EOG [speed_ref] [speed_mod]
!
!  [speed_ref]  Reference speed:
!                 I  →  Vhub = Vin    (cut-in)
!                 O  →  Vhub = Vout   (cut-out)
!                 R  →  Vhub = Vrated ± modifier  (rated)
!
!  [speed_mod]  Used only with R. Optional offset in user units.
!               Allowed range: -2.0 to +2.0 m/s.
!               Omit for exactly Vrated.
!
!  Physics: u(t) = Vhub − 0.37×Vg×sin(3π·t/10.5)×(1−cos(2π·t/10.5))
!           Vg   = min(1.35×(Ve1−Vhub),  3.3×σ₁/(1+0.1×D/Λ₁))
!
!  Examples:
EOGI          ! Vhub = Vin
EOGO          ! Vhub = Vout
EOGR          ! Vhub = Vrated
EOGR+2.0      ! Vhub = Vrated + 2.0 m/s
EOGR-2.0      ! Vhub = Vrated − 2.0 m/s
!
! ── EDC  Extreme Direction Change ───────────────────────────
!  Format:  EDC [dir] [speed_ref] [speed_mod]
!
!  [dir]        Direction of yaw excursion:  +  or  -
!  [speed_ref]  I / O / R  (same meaning as EOG above)
!  [speed_mod]  Optional offset from Vrated (only with R).
!
!  Physics: θ(t) = 0.5×Θ×(1−cos(π·t/6))               [T=6 s]
!           Θ    = 4×atan(σ₁/(Vhub×(1+0.1×D/Λ₁)))     [deg]
!
!  Examples:
EDC+I         ! +direction, Vhub = Vin
EDC-I         ! −direction, Vhub = Vin
EDC+O         ! +direction, Vhub = Vout
EDC-O         ! −direction, Vhub = Vout
EDC+R         ! +direction, Vhub = Vrated
EDC-R         ! −direction, Vhub = Vrated
EDC+R+2.0     ! +direction, Vhub = Vrated + 2.0 m/s
EDC-R-2.0     ! −direction, Vhub = Vrated − 2.0 m/s
!
! ── NWP  Normal Wind Profile ────────────────────────────────
!  Format:  NWP [speed]
!
!  [speed]  Hub-height wind speed in m/s.
!           NOTE: Always in m/s regardless of the SI_UNIT setting above.
!
!  Produces a single steady-state row with power-law shear (exponent α).
!  No transient — useful as a baseline or for OpenFAST steady simulations.
!
!  Examples:
NWP4.0        ! steady wind at  4.0 m/s (cut-in)
NWP10.0       ! steady wind at 10.0 m/s (rated)
NWP24.0       ! steady wind at 24.0 m/s (cut-out)
!
! ── EWM  Extreme Wind Model ─────────────────────────────────
!  Format:  EWM [recurrence]
!
!  [recurrence]  50  →  50-year return period, Vhub = Ve50 = 1.4×Vref
!                01  →   1-year return period, Vhub = Ve1  = 0.8×Ve50
!
!  Shear exponent is fixed at α = 0.11 (IEC §6.3.2.1),
!  regardless of the IEC_EDITION setting.
!  Produces a single steady-state row (no transient).
!
!  Examples:
EWM50         ! 50-year extreme wind
EWM01         ! 1-year  extreme wind

"""  # end of template string

def format_openfast_input(params: IECParameters) -> str:
    """Render parameters in an OpenFAST-style value/key/comment layout."""
    lc = params.len_convert
    value_width = 14
    key_width = 12

    def row(value: str, key: str, comment: str) -> str:
        return f"{value:<{value_width}}  {key:<{key_width}} - {comment}"

    def section(title: str) -> list[str]:
        return [
            f"! {title}",
            f"! {'-' * len(title)}",
        ]

    grouped_conditions = _group_conditions_by_type(params.conditions)

    def case_row(case_type: str, enabled: str, options: str, comment: str) -> str:
        return f"{case_type:<14}  {enabled:<5}  {options:<24} - {comment}"

    rows = [
        "! ------- pyIECWind Input File -----------------------------------------------",
        "! Generated by pyIECWind in an OpenFAST-style table layout.",
        "! Each active data row follows: value  key  - comment",
        "",
        *section("General"),
        "",
        row(str(params.si_unit), "si_unit", "True for SI (m, m/s), False for English (ft, ft/s)"),
        row(f"{params.t1:.3f}", "t1", "transient start time [s]"),
        row(f"{params.wtc:d}", "wtc", "wind turbine class (1, 2, or 3)"),
        row(params.catg.upper(), "catg", "turbulence category (A, B, or C)"),
        row(f"{params.slope_deg:.3f}", "slope_deg", "inflow inclination angle [deg]"),
        row(f"{params.iec_edition:d}", "iec_edition", "IEC edition for alpha (1 or 3)"),
        "",
        *section("Turbine"),
        "",
        row(f"{params.hh * lc:.3f}", "hh", f"hub height [{params.len_unit}]"),
        row(f"{params.dia * lc:.3f}", "dia", f"rotor diameter [{params.len_unit}]"),
        "",
        *section("Operating Speeds"),
        "",
        row(f"{params.vin * lc:.3f}", "vin", f"cut-in wind speed [{params.spd_unit}]"),
        row(f"{params.vrated * lc:.3f}", "vrated", f"rated wind speed [{params.spd_unit}]"),
        row(f"{params.vout * lc:.3f}", "vout", f"cut-out wind speed [{params.spd_unit}]"),
        "",
        *section("Cases"),
        "",
        "! Format: case_type  use_case  options_array  - allowed options and notes",
        "! Set use_case to True to generate the listed options, False to skip the row, or None as a placeholder.",
        "! For NWP, the listed speeds are always interpreted in m/s, matching the legacy IECWind behavior.",
        "",
    ]

    for case_type in CASE_TYPE_ORDER:
        options = grouped_conditions[case_type]
        if options:
            options_text = "[" + ", ".join(options) + "]"
            enabled = "True"
        elif case_type == "EWM":
            options_text = "[50]"
            enabled = "False"
        elif case_type == "NWP":
            options_text = "[10.0]"
            enabled = "False"
        else:
            options_text = "[None]"
            enabled = "False"

        rows.append(case_row(case_type, enabled, options_text, CASE_ROW_COMMENTS[case_type]))

    rows.append(case_row("EWM", "None", "[None]", "placeholder row; ignored by the parser"))
    return "\n".join(rows) + "\n"


_TEMPLATE = format_openfast_input(
    IECParameters(
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
        conditions=[
            "ECD+R",
            "ECD-R",
            "EWSV+12.0",
            "EWSH-12.0",
            "EOGR+2.0",
            "EDC+R",
            "NWP23.7",
            "EWM50",
        ],
    )
)


def write_template(dest: str | Path = "IEC_template.ipt") -> None:
    """Write a fully commented template .IPT file to *dest*."""
    path = Path(dest)
    path.write_text(_TEMPLATE, encoding="utf-8")
    print(f"Template written to: {path}")
    print("Edit the values and condition list, then run:")
    print(f"  python iec_wind.py {path}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

_USAGE = """\
Usage:
  python iec_wind.py                   run with IEC.IPT in current directory
  python iec_wind.py <file.ipt>        run with a named input file
  python iec_wind.py --template        write a commented template .IPT file
  python iec_wind.py --template <out>  write template to a named file
  python iec_wind.py --help            show this message
"""


def main() -> None:
    args = sys.argv[1:]

    # -- Help ----------------------------------------------------------------
    if "--help" in args or "-h" in args:
        print(f"IECWind (Python) v{VERSION}\n")
        print(_USAGE)
        return

    # -- Template generation -------------------------------------------------
    if "--template" in args:
        idx  = args.index("--template")
        dest = args[idx + 1] if idx + 1 < len(args) else "IEC_template.ipt"
        write_template(dest)
        return

    # -- Normal run ----------------------------------------------------------
    ipt_file = args[0] if args else "IEC.IPT"

    print(f"IECWind (Python) v{VERSION}")
    print(f"Reading input from: {ipt_file}\n")

    try:
        params = parse_input_file(ipt_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"FATAL: {exc}")
        sys.exit(1)

    print(params.summary())
    print()

    n = generate_all(params)
    print(f"\n{n} wind file(s) generated.")


if __name__ == "__main__":
    main()
