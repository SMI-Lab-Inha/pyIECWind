from __future__ import annotations

import unittest
from pathlib import Path

from pyiecwind.core import _parse_case_row, parse_input_file

from helpers import WorkspaceTestCaseMixin, openfast_case_table_text


class ParsingTests(WorkspaceTestCaseMixin, unittest.TestCase):
    def test_parse_case_row_expands_array_options(self) -> None:
        expanded = _parse_case_row("ECD             True   [+R, -R+2.0]              - test row", lineno=1)
        self.assertEqual(expanded, ["ECD+R", "ECD-R+2.0"])

    def test_parse_case_row_returns_empty_for_false(self) -> None:
        expanded = _parse_case_row("EWM             False  [50, 01]                  - disabled row", lineno=1)
        self.assertEqual(expanded, [])

    def test_parse_openfast_case_table_builds_expected_conditions(self) -> None:
        tmp = self.workspace_tempdir()
        path = tmp / "case_table.ipt"
        path.write_text(
            openfast_case_table_text(
                case_rows=[
                    "ECD             True   [+R, -R]                  - ECD row",
                    "EWS             True   [V+12.0, H-12.0]          - EWS row",
                    "EOG             True   [I, O, R+2.0]             - EOG row",
                    "EDC             True   [+I, -R]                  - EDC row",
                    "NWP             True   [10.0, 23.7]              - NWP row",
                    "EWM             True   [50, 01]                  - EWM row",
                ]
            ),
            encoding="utf-8",
        )

        params = parse_input_file(path)

        self.assertEqual(
            params.conditions,
            [
                "ECD+R",
                "ECD-R",
                "EWSV+12.0",
                "EWSH-12.0",
                "EOGI",
                "EOGO",
                "EOGR+2.0",
                "EDC+I",
                "EDC-R",
                "NWP10.0",
                "NWP23.7",
                "EWM50",
                "EWM01",
            ],
        )

    def test_parse_openfast_false_and_none_rows_are_ignored(self) -> None:
        tmp = self.workspace_tempdir()
        path = tmp / "disabled.ipt"
        path.write_text(
            openfast_case_table_text(
                case_rows=[
                    "ECD             False  [+R, -R]                  - ignored",
                    "NWP             True   [10.0]                    - included",
                    "EWM             None   [50]                      - placeholder",
                ]
            ),
            encoding="utf-8",
        )

        params = parse_input_file(path)
        self.assertEqual(params.conditions, ["NWP10.0"])

    def test_parse_keyed_format_is_still_supported(self) -> None:
        tmp = self.workspace_tempdir()
        path = tmp / "keyed.ipt"
        path.write_text(
            "\n".join(
                [
                    "si_unit = True",
                    "t1 = 40.0",
                    "wtc = 2",
                    "catg = B",
                    "slope_deg = 0.0",
                    "iec_edition = 3",
                    "hh = 80.0",
                    "dia = 80.0",
                    "vin = 4.0",
                    "vrated = 10.0",
                    "vout = 24.0",
                    "",
                    "conditions:",
                    "  - EWM50",
                    "  - NWP10.0",
                ]
            ),
            encoding="utf-8",
        )

        params = parse_input_file(path)
        self.assertEqual(params.conditions, ["EWM50", "NWP10.0"])

    def test_parse_legacy_format_is_still_supported(self) -> None:
        tmp = self.workspace_tempdir()
        path = tmp / "legacy.ipt"
        legacy_lines = [
            "header 1",
            "header 2",
            "TRUE",
            "40.0",
            "header 5",
            "2",
            "B",
            "0.0",
            "3",
            "header 10",
            "80.0",
            "80.0",
            "4.0",
            "10.0",
            "24.0",
            "header 16",
            "EWM50",
            "NWP10.0",
            "",
        ]
        path.write_text("\n".join(legacy_lines), encoding="utf-8")

        params = parse_input_file(path)
        self.assertEqual(params.conditions, ["EWM50", "NWP10.0"])
