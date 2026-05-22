"""Public package interface for pyIECWind."""

from .core import (
    DEFAULT_INPUT_FILENAME,
    DEFAULT_TEMPLATE_FILENAME,
    VERSION,
    GenerationError,
    GenerationResult,
    IECParameters,
    IECWindWarning,
    format_openfast_input,
    generate_all,
    generate_from_input_file,
    parse_input_file,
    write_template,
)

#: Installed distribution version (single source of truth: ``pyproject.toml``).
__version__ = VERSION

__all__ = [
    "DEFAULT_INPUT_FILENAME",
    "DEFAULT_TEMPLATE_FILENAME",
    "VERSION",
    "GenerationError",
    "GenerationResult",
    "IECParameters",
    "IECWindWarning",
    "__version__",
    "format_openfast_input",
    "generate_all",
    "generate_from_input_file",
    "parse_input_file",
    "write_template",
]
