from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from pyiecwind.cli import build_parser, main

from helpers import WorkspaceTestCaseMixin, openfast_case_table_text


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
            "",   # SI units -> default yes
            "",   # t1
            "",   # wtc
            "",   # catg
            "",   # slope_deg
            "",   # iec_edition
            "",   # hh
            "",   # dia
            "",   # vin
            "",   # vrated
            "",   # vout
            "",   # condition type -> default EWM
            "",   # recurrence -> 50
            "n",  # add another condition?
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with redirect_stdout(io.StringIO()):
                result = main(["wizard", "-o", str(output_dir), "--save-input", "wizard_case.ipt"])

        self.assertEqual(result, 0)
        self.assertTrue((output_dir / "EWM50.wnd").exists())
        self.assertTrue((output_dir / "wizard_case.ipt").exists())
