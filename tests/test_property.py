"""Property-based tests (Hypothesis).

These exercise the parser round-trip, the condition-code grammar, unit
conversion, transient row counts, and direction-ramp monotonicity across a wide
range of randomly generated -- but always valid -- turbine definitions.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pyiecwind import IECParameters, format_openfast_input, parse_input_file
from pyiecwind.generation import gen_ecd, gen_edc, gen_eog, gen_nwp
from pyiecwind.models import DT

settings.register_profile(
    "pyiecwind",
    deadline=None,  # file I/O on CI/Windows can exceed the default deadline
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("pyiecwind")

# Conditions valid for any in-range turbine, used for the round-trip property.
# Listed in CASE_TYPE_ORDER so the formatter's regrouping reproduces this order.
_SAFE_CONDITIONS = ("ECD+R", "EOGR", "EDC+R", "NWP10.0", "EWM50", "EWM01")


def _finite(lo: float, hi: float) -> st.SearchStrategy[float]:
    return st.floats(min_value=lo, max_value=hi, allow_nan=False, allow_infinity=False)


@st.composite
def _valid_params(draw: st.DrawFn, conditions: tuple[str, ...] = _SAFE_CONDITIONS) -> IECParameters:
    dia = draw(_finite(10.0, 250.0))
    hh = draw(_finite(dia / 2.0 + 1.0, 320.0))
    vin = draw(_finite(1.0, 8.0))
    vrated = draw(_finite(vin + 1.0, 16.0))
    vout = draw(_finite(vrated + 1.0, 35.0))
    return IECParameters(
        si_unit=draw(st.booleans()),
        t1=draw(_finite(0.0, 120.0)),
        wtc=draw(st.sampled_from([1, 2, 3])),
        catg=draw(st.sampled_from(["A", "B", "C"])),
        slope_deg=draw(_finite(-8.0, 8.0)),
        iec_edition=draw(st.sampled_from([1, 3])),
        hh=hh,
        dia=dia,
        vin=vin,
        vrated=vrated,
        vout=vout,
        conditions=conditions,
    )


def _data_rows(path: Path) -> list[list[float]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("!"):
            rows.append([float(token) for token in line.split()])
    return rows


def _fixed_params(*, si_unit: bool) -> IECParameters:
    return IECParameters(
        si_unit=si_unit,
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
        conditions=(),
    )


@given(_valid_params())
def test_openfast_format_parse_roundtrip(params: IECParameters) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.ipt"
        path.write_text(format_openfast_input(params), encoding="utf-8")
        parsed = parse_input_file(path)

    assert parsed.conditions == params.conditions
    assert parsed.si_unit == params.si_unit
    assert parsed.wtc == params.wtc
    assert parsed.catg == params.catg
    assert parsed.iec_edition == params.iec_edition
    for attr in ("hh", "dia", "vin", "vrated", "vout", "t1", "slope_deg"):
        assert math.isclose(getattr(parsed, attr), getattr(params, attr), abs_tol=0.01)


@given(_valid_params(conditions=("EWM50",)))
def test_transient_row_counts_match_duration(params: IECParameters) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        for generator, code, duration in ((gen_ecd, "ECD+R", 10.0), (gen_edc, "EDC+R", 6.0)):
            rows = _data_rows(generator(code, params, output_dir=out))
            assert len(rows) == round(duration / DT) + 2


@given(speed=_finite(0.5, 60.0))
def test_nwp_speed_scales_with_unit_system(speed: float) -> None:
    code = f"NWP{speed:.3f}"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        si = _data_rows(gen_nwp(code, _fixed_params(si_unit=True), output_dir=out))[0][1]
        english = _data_rows(gen_nwp(code, _fixed_params(si_unit=False), output_dir=out))[0][1]
    # Columns are rendered to three decimals, so allow half-a-digit of rounding.
    assert math.isclose(english, si * 3.2808, abs_tol=2e-3)


@given(reference=st.sampled_from(["I", "O"]), modifier=_finite(0.1, 5.0))
def test_modifier_on_non_rated_reference_always_rejected(reference: str, modifier: float) -> None:
    params = _fixed_params(si_unit=True)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        with pytest.raises(ValueError):
            gen_eog(f"EOG{reference}{modifier:+.1f}", params, output_dir=out)
        with pytest.raises(ValueError):
            gen_edc(f"EDC+{reference}{modifier:+.1f}", params, output_dir=out)


@given(_valid_params(conditions=("EDC+R",)))
def test_direction_ramp_is_monotonic(params: IECParameters) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        rows = _data_rows(gen_edc("EDC+R", params, output_dir=Path(tmp)))
    directions = [row[2] for row in rows]
    assert directions[0] == 0.0
    assert all(b >= a - 1e-9 for a, b in zip(directions, directions[1:], strict=False))


@given(
    vin=_finite(5.0, 10.0),
    vrated=_finite(1.0, 4.0),
)
def test_construction_rejects_unordered_speeds(vin: float, vrated: float) -> None:
    with pytest.raises(ValueError):
        IECParameters(
            si_unit=True,
            t1=40.0,
            wtc=2,
            catg="B",
            slope_deg=0.0,
            iec_edition=3,
            hh=80.0,
            dia=80.0,
            vin=vin,
            vrated=vrated,
            vout=24.0,
            conditions=("EWM50",),
        )
