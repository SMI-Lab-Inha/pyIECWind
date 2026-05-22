"""Compatibility facade re-exporting the stable public pyIECWind API.

Only supported, public names live here. Implementation helpers (the underscored
parsing/validation functions, alias tables, and token sets used internally) are
intentionally *not* re-exported, so they remain free to change without breaking
callers. Import internals from their own modules if you must.
"""

from __future__ import annotations

from .generation import (
    GenerationError,
    GenerationResult,
    gen_ecd,
    gen_edc,
    gen_eog,
    gen_ewm,
    gen_ews,
    gen_nwp,
    generate_all,
    generate_from_input_file,
)
from .models import (
    BETA,
    CASE_PREFIXES,
    CASE_ROW_COMMENTS,
    CASE_TYPE_ORDER,
    DEFAULT_INPUT_FILENAME,
    DEFAULT_TEMPLATE_FILENAME,
    DT,
    EWM_ALPHA,
    PI,
    VCG,
    VERSION,
    IECParameters,
    IECWindWarning,
)
from .parsing import parse_input_file
from .template import format_openfast_input, write_template

__all__ = [
    "BETA",
    "CASE_PREFIXES",
    "CASE_ROW_COMMENTS",
    "CASE_TYPE_ORDER",
    "DEFAULT_INPUT_FILENAME",
    "DEFAULT_TEMPLATE_FILENAME",
    "DT",
    "EWM_ALPHA",
    "GenerationError",
    "GenerationResult",
    "IECParameters",
    "IECWindWarning",
    "PI",
    "VCG",
    "VERSION",
    "format_openfast_input",
    "gen_ecd",
    "gen_edc",
    "gen_eog",
    "gen_ewm",
    "gen_ews",
    "gen_nwp",
    "generate_all",
    "generate_from_input_file",
    "parse_input_file",
    "write_template",
]
