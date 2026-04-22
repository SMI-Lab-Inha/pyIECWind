from __future__ import annotations

import argparse
from pathlib import Path

from .core import IECParameters, VERSION, format_openfast_input, generate_from_input_file, write_template


def _prompt_text(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def _prompt_float(prompt: str, default: float) -> float:
    while True:
        raw = _prompt_text(prompt, str(default))
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")


def _prompt_int(prompt: str, default: int, allowed: set[int] | None = None) -> int:
    while True:
        raw = _prompt_text(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print("Please enter an integer value.")
            continue
        if allowed is not None and value not in allowed:
            print(f"Choose one of: {', '.join(str(item) for item in sorted(allowed))}")
            continue
        return value


def _prompt_choice(prompt: str, default: str, allowed: set[str]) -> str:
    allowed_upper = {item.upper() for item in allowed}
    while True:
        value = _prompt_text(prompt, default).upper()
        if value in allowed_upper:
            return value
        print(f"Choose one of: {', '.join(sorted(allowed_upper))}")


def _prompt_yes_no(prompt: str, default: bool = True) -> bool:
    default_token = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{default_token}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def _build_condition() -> str:
    print("\nCondition types:")
    print("  ECD  Extreme Coherent Gust with Direction Change")
    print("  EWS  Extreme Wind Shear")
    print("  EOG  Extreme Operating Gust")
    print("  EDC  Extreme Direction Change")
    print("  NWP  Normal Wind Profile")
    print("  EWM  Extreme Wind Model")

    kind = _prompt_choice("Select condition type", "EWM", {"ECD", "EWS", "EOG", "EDC", "NWP", "EWM"})

    if kind == "ECD":
        direction = _prompt_choice("Direction sign (+ or -)", "+", {"+", "-"})
        modifier = _prompt_float("Speed modifier relative to Vrated", 0.0)
        return f"ECD{direction}R" if modifier == 0.0 else f"ECD{direction}R{modifier:+0.1f}"

    if kind == "EWS":
        axis = _prompt_choice("Shear axis (V or H)", "V", {"V", "H"})
        direction = _prompt_choice("Shear direction (+ or -)", "+", {"+", "-"})
        speed = _prompt_float("Hub-height wind speed in selected user units", 12.0)
        return f"EWS{axis}{direction}{speed:0.1f}"

    if kind == "EOG":
        speed_ref = _prompt_choice("Reference speed (I, O, or R)", "R", {"I", "O", "R"})
        if speed_ref != "R":
            return f"EOG{speed_ref}"
        modifier = _prompt_float("Speed modifier relative to Vrated", 0.0)
        return "EOGR" if modifier == 0.0 else f"EOGR{modifier:+0.1f}"

    if kind == "EDC":
        direction = _prompt_choice("Direction sign (+ or -)", "+", {"+", "-"})
        speed_ref = _prompt_choice("Reference speed (I, O, or R)", "R", {"I", "O", "R"})
        if speed_ref != "R":
            return f"EDC{direction}{speed_ref}"
        modifier = _prompt_float("Speed modifier relative to Vrated", 0.0)
        return f"EDC{direction}R" if modifier == 0.0 else f"EDC{direction}R{modifier:+0.1f}"

    if kind == "NWP":
        speed = _prompt_float("Steady wind speed in m/s", 10.0)
        return f"NWP{speed:0.1f}"

    recurrence = _prompt_choice("Recurrence period (50 or 01)", "50", {"50", "01"})
    return f"EWM{recurrence}"


def _parameters_to_input_text(params: IECParameters) -> str:
    return format_openfast_input(params)


def _run_wizard(args: argparse.Namespace) -> int:
    print(f"pyIECWind wizard ({VERSION})")
    print("Press Enter to accept the defaults shown in brackets.\n")

    si_unit = _prompt_yes_no("Use SI units (m, m/s)?", True)
    params = IECParameters(
        si_unit=si_unit,
        t1=_prompt_float("Transient start time T1 [s]", 40.0),
        wtc=_prompt_int("Wind turbine class", 2, {1, 2, 3}),
        catg=_prompt_choice("Turbulence category", "B", {"A", "B", "C"}),
        slope_deg=_prompt_float("Inflow inclination angle [deg]", 0.0),
        iec_edition=_prompt_int("IEC edition for alpha", 3, {1, 3}),
        hh=_prompt_float("Hub height", 80.0) / (1.0 if si_unit else 3.2808),
        dia=_prompt_float("Rotor diameter", 80.0) / (1.0 if si_unit else 3.2808),
        vin=_prompt_float("Cut-in wind speed", 4.0) / (1.0 if si_unit else 3.2808),
        vrated=_prompt_float("Rated wind speed", 10.0) / (1.0 if si_unit else 3.2808),
        vout=_prompt_float("Cut-out wind speed", 24.0) / (1.0 if si_unit else 3.2808),
        conditions=[],
    )

    while True:
        params.conditions.append(_build_condition())
        if not _prompt_yes_no("Add another condition?", False):
            break

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = None
    if args.save_input:
        input_path = output_dir / args.save_input
        input_path.write_text(_parameters_to_input_text(params), encoding="utf-8")

    from .core import generate_all

    count = generate_all(params, output_dir=output_dir)
    print(f"\nGenerated {count} wind file(s) in {output_dir}")
    if input_path is not None:
        print(f"Saved reproducible input file to {input_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyiecwind",
        description="Generate IECWind .wnd files from an input file or guided wizard.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Generate .wnd files from an .ipt file.")
    run_parser.add_argument("input_file", nargs="?", default="IEC.IPT")
    run_parser.add_argument("-o", "--output-dir", default=".")

    template_parser = subparsers.add_parser("template", help="Write a commented template input file.")
    template_parser.add_argument("dest", nargs="?", default="IEC_template.ipt")

    wizard_parser = subparsers.add_parser("wizard", help="Interactive case builder for non-expert users.")
    wizard_parser.add_argument("-o", "--output-dir", default=".")
    wizard_parser.add_argument("--save-input", default="wizard_case.ipt")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        params, count = generate_from_input_file("IEC.IPT", output_dir=".")
        print(params.summary())
        print(f"\nGenerated {count} wind file(s).")
        return 0

    if args.command == "run":
        params, count = generate_from_input_file(args.input_file, output_dir=args.output_dir)
        print(params.summary())
        print(f"\nGenerated {count} wind file(s).")
        return 0

    if args.command == "template":
        write_template(args.dest)
        return 0

    if args.command == "wizard":
        return _run_wizard(args)

    parser.print_help()
    return 1
