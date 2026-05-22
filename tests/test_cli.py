from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from helpers import WorkspaceTestCaseMixin, openfast_case_table_text
from pyiecwind.cli import (
    _build_condition,
    _prompt_choice,
    _prompt_float,
    _prompt_int,
    _prompt_yes_no,
    build_parser,
    main,
)


class CLITests(WorkspaceTestCaseMixin, unittest.TestCase):
    def test_build_parser_exposes_expected_commands(self) -> None:
        parser = build_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        help_text = parser.format_help()
        self.assertIn("run", help_text)
        self.assertIn("template", help_text)
        self.assertIn("wizard", help_text)

    def test_main_template_writes_file(self) -> None:
        tmp = self.workspace_tempdir()
        dest = tmp / "template.ipt"

        result = main(["template", str(dest)])

        self.assertEqual(result, 0)
        self.assertTrue(dest.exists())

    def test_main_run_generates_outputs(self) -> None:
        tmp = self.workspace_tempdir()
        input_file = tmp / "input.ipt"
        output_dir = tmp / "out"
        input_file.write_text(
            openfast_case_table_text(
                case_rows=[
                    "EWM             True   [50]                    - EWM row",
                    "NWP             True   [10.0]                  - NWP row",
                ]
            ),
            encoding="utf-8",
        )

        with redirect_stdout(io.StringIO()) as buffer:
            result = main(["run", str(input_file), "-o", str(output_dir)])

        self.assertEqual(result, 0)
        self.assertIn("Generated 2 wind file(s).", buffer.getvalue())
        self.assertTrue((output_dir / "EWM50.wnd").exists())

    def test_main_wizard_generates_output_and_saved_input(self) -> None:
        tmp = self.workspace_tempdir()
        output_dir = tmp / "wizard"
        user_inputs = [
            "",  # SI units -> default yes
            "",  # t1
            "",  # wtc
            "",  # catg
            "",  # slope_deg
            "",  # iec_edition
            "",  # hh
            "",  # dia
            "",  # vin
            "",  # vrated
            "",  # vout
            "",  # condition type -> default EWM
            "",  # recurrence -> 50
            "n",  # add another condition?
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with redirect_stdout(io.StringIO()):
                result = main(["wizard", "-o", str(output_dir), "--save-input", "wizard_case.ipt"])

        self.assertEqual(result, 0)
        self.assertTrue((output_dir / "EWM50.wnd").exists())
        self.assertTrue((output_dir / "wizard_case.ipt").exists())


class WizardPromptTests(unittest.TestCase):
    def _build(self, inputs: list[str]) -> str:
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(io.StringIO()):
                return _build_condition()

    def test_build_condition_covers_every_case_kind(self) -> None:
        expectations = [
            (["ECD", "+", "0"], "ECD+R"),
            (["ECD", "+", "1.5"], "ECD+R+1.5"),
            (["EWS", "V", "+", "12"], "EWSV+12.0"),
            (["EOG", "I"], "EOGI"),
            (["EOG", "R", "2"], "EOGR+2.0"),
            (["EDC", "+", "R", "0"], "EDC+R"),
            (["EDC", "-", "I"], "EDC-I"),
            (["NWP", "10"], "NWP10.0"),
            (["EWM", "50"], "EWM50"),
        ]
        for inputs, expected in expectations:
            with self.subTest(expected=expected):
                self.assertEqual(self._build(inputs), expected)

    def test_build_condition_reprompts_on_invalid_numeric_input(self) -> None:
        self.assertEqual(self._build(["NWP", "fast", "10"]), "NWP10.0")

    def test_prompt_int_rejects_non_integer_and_out_of_range(self) -> None:
        with patch("builtins.input", side_effect=["abc", "5", "2"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(_prompt_int("class", 2, {1, 2, 3}), 2)

    def test_prompt_choice_reprompts_until_allowed(self) -> None:
        with patch("builtins.input", side_effect=["Z", "B"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(_prompt_choice("cat", "A", {"A", "B"}), "B")

    def test_prompt_float_default_used_on_blank(self) -> None:
        with patch("builtins.input", side_effect=[""]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(_prompt_float("x", 3.5), 3.5)

    def test_prompt_yes_no_variants(self) -> None:
        with patch("builtins.input", side_effect=["maybe", "y"]):
            with redirect_stdout(io.StringIO()):
                self.assertTrue(_prompt_yes_no("ok?", default=False))
        with patch("builtins.input", side_effect=[""]):
            with redirect_stdout(io.StringIO()):
                self.assertFalse(_prompt_yes_no("ok?", default=False))
