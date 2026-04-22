"""Input parsing and validation helpers for pyIECWind."""

from __future__ import annotations

import re
from pathlib import Path

from .models import (
    CASE_PREFIXES,
    CASE_TYPE_ORDER,
    DEFAULT_INPUT_FILENAME,
    FALSE_TOKENS,
    IECParameters,
    NONE_TOKENS,
    TRUE_TOKENS,
)

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


def _normalize_key(raw: str) -> str:
    return raw.strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_case_options_text(text: str) -> str:
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        return text[1:-1].strip()
    return text


def _split_case_options(text: str) -> list[str]:
    text = _normalize_case_options_text(text)
    if not text or text.upper() in NONE_TOKENS:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _expand_case_row(case_type: str, options: list[str], *, lineno: int) -> list[str]:
    if case_type not in CASE_PREFIXES:
        raise ValueError(f"Unknown case type on line {lineno}: {case_type}")
    prefix = CASE_PREFIXES[case_type]
    if case_type == "NWP":
        return [f"{prefix}{option}" for option in options]
    return [f"{prefix}{option.upper()}" for option in options]


def _parse_case_row(line: str, *, lineno: int) -> list[str]:
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
    if enabled in NONE_TOKENS or enabled in FALSE_TOKENS:
        return []
    if enabled not in TRUE_TOKENS:
        raise ValueError(
            f"Case enable flag on line {lineno} must be True, False, or None. Got: {parts[1]!r}"
        )

    options = _split_case_options(options_text)
    if not options:
        return []
    return _expand_case_row(case_type, options, lineno=lineno)


def _group_conditions_by_type(conditions: list[str]) -> dict[str, list[str]]:
    grouped = {case_type: [] for case_type in CASE_TYPE_ORDER}
    for code in conditions:
        prefix = code[:3].upper()
        if prefix in grouped:
            grouped[prefix].append(code[3:])
    return grouped


def _parse_condition_value(value: str, *, lineno: int) -> str | None:
    tokens = value.split()
    if not tokens:
        raise ValueError(f"Missing condition code on line {lineno}.")

    first = tokens[0].upper()
    if first in TRUE_TOKENS | FALSE_TOKENS:
        if len(tokens) < 2:
            raise ValueError(
                f"Condition toggle on line {lineno} must be followed by a condition code."
            )
        return " ".join(tokens[1:]).upper() if first in TRUE_TOKENS else None
    if first in NONE_TOKENS:
        return None
    return value.upper()


def _append_condition_value(conditions: list[str], value: str, *, lineno: int) -> None:
    parsed = _parse_condition_value(value, lineno=lineno)
    if parsed is not None:
        conditions.append(parsed)


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
    len_convert = 1.0 if si_unit else 3.2808

    if wtc not in (1, 2, 3):
        raise ValueError(f"Wind turbine class must be 1, 2, or 3. Got: {wtc}")

    catg = catg.upper()
    if catg not in ("A", "B", "C"):
        raise ValueError(f"Turbulence category must be A, B, or C. Got: {catg!r}")

    if abs(slope_deg) > 8.0:
        print(
            "WARNING: IEC specifies a maximum inclination angle of 8 deg.\n"
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
            f"Hub height ({hh_raw}) must be greater than rotor radius ({dia_raw / 2.0:.2f}). Check your input file."
        )

    hh = hh_raw / len_convert
    dia = dia_raw / len_convert
    vin = vin_raw / len_convert
    vrated = vrated_raw / len_convert
    vout = vout_raw / len_convert

    if vrated <= vin:
        raise ValueError(f"Rated speed ({vrated:.2f}) must exceed cut-in ({vin:.2f}).")
    if vout <= vrated:
        raise ValueError(f"Cut-out speed ({vout:.2f}) must exceed rated ({vrated:.2f}).")
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


def _finalize_parsed_fields(fields: dict[str, str], conditions: list[str]) -> IECParameters:
    required = [
        "si_unit",
        "t1",
        "wtc",
        "catg",
        "slope_deg",
        "iec_edition",
        "hh",
        "dia",
        "vin",
        "vrated",
        "vout",
    ]
    missing = [name for name in required if name not in fields]
    if missing:
        raise ValueError(f"Missing required input field(s): {', '.join(missing)}.")

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


def _parse_legacy_input_file(raw_lines: list[str]) -> IECParameters:
    while len(raw_lines) < 17:
        raw_lines.append("")

    def first_token(line: str) -> str:
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

    conditions: list[str] = []
    for raw in raw_lines[16:]:
        stripped = raw.strip()
        if not stripped:
            break
        conditions.append(stripped.upper())

    return _build_parameters(
        si_unit=si_unit,
        t1=float(line_val(3, "transient start time")),
        wtc=int(line_val(5, "wind turbine class")),
        catg=line_val(6, "turbulence category"),
        slope_deg=float(line_val(7, "wind inflow angle")),
        iec_edition=int(line_val(8, "IEC edition for wind shear exponent")),
        hh_raw=float(line_val(10, "hub height")),
        dia_raw=float(line_val(11, "rotor diameter")),
        vin_raw=float(line_val(12, "cut-in wind speed")),
        vrated_raw=float(line_val(13, "rated wind speed")),
        vout_raw=float(line_val(14, "cut-out wind speed")),
        conditions=conditions,
    )


def _parse_keyed_input_file(raw_lines: list[str]) -> IECParameters:
    fields: dict[str, str] = {}
    conditions: list[str] = []
    in_conditions = False

    for lineno, raw_line in enumerate(raw_lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("!", "#")):
            continue

        if in_conditions:
            if stripped.startswith("-"):
                _append_condition_value(conditions, stripped[1:].strip(), lineno=lineno)
                continue
            if "=" not in stripped and ":" not in stripped:
                _append_condition_value(conditions, stripped, lineno=lineno)
                continue
            in_conditions = False

        if ":" in stripped and stripped.split(":", 1)[0].strip().lower() == "conditions":
            trailing = stripped.split(":", 1)[1].strip()
            in_conditions = True
            if trailing:
                _append_condition_value(conditions, trailing, lineno=lineno)
            continue

        if "=" in stripped:
            raw_key, raw_value = stripped.split("=", 1)
        elif ":" in stripped:
            raw_key, raw_value = stripped.split(":", 1)
        else:
            raise ValueError(f"Cannot parse keyed input line {lineno}: {raw_line!r}")

        key = FIELD_ALIASES.get(_normalize_key(raw_key))
        if key is None:
            raise ValueError(f"Unknown input key on line {lineno}: {raw_key!r}")

        value = raw_value.strip()
        if key in {"condition", "conditions"}:
            _append_condition_value(conditions, value, lineno=lineno)
        else:
            fields[key] = value

    return _finalize_parsed_fields(fields, conditions)


def _parse_openfast_input_file(raw_lines: list[str]) -> IECParameters:
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
            _append_condition_value(conditions, value, lineno=lineno)
            continue

        if not value:
            raise ValueError(f"Missing value for '{key}' on line {lineno}.")
        fields[key] = value

    return _finalize_parsed_fields(fields, conditions)


def parse_input_file(filepath: str | Path = DEFAULT_INPUT_FILENAME) -> IECParameters:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find input file '{path}'. Ensure {DEFAULT_INPUT_FILENAME} is in the current working directory."
        )

    raw_lines = path.read_text(encoding="utf-8").splitlines()

    keyed_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_ -]*\s*(=|:)\s*.*$")
    openfast_pattern = re.compile(r"^\S+\s{2,}[A-Za-z_][A-Za-z0-9_ -]*\s*(?:\s+-.*)?$")
    keyed_format = any(
        stripped and not stripped.startswith(("!", "#")) and keyed_pattern.match(stripped)
        for stripped in (line.strip() for line in raw_lines)
    )
    openfast_format = any(
        stripped and not stripped.startswith(("!", "#")) and openfast_pattern.match(stripped)
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
