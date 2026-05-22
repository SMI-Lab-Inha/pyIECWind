# Architecture

pyIECWind is organised as a small set of single-responsibility modules under
`src/pyiecwind/`. Data flows in one direction: text input is parsed and
validated into a typed parameter object, generators turn that object into wind
series and write `.wnd` files, and only the CLI talks to the user.

| Module | Responsibility |
| --- | --- |
| `models` | Constants, the `IECParameters` dataclass and derived properties, the `IECWindWarning` category, and the single-sourced `VERSION`. |
| `parsing` | Read the three supported input layouts (OpenFAST-style table, keyed, legacy), normalise aliases, and validate into `IECParameters`. |
| `generation` | The six condition generators, the `WindFileWriter`, and `generate_all` / `generate_from_input_file` returning a structured `GenerationResult`. |
| `template` | Render `IECParameters` back to an OpenFAST-style input file and write commented templates. |
| `core` | Compatibility facade re-exporting the public (and historical) API surface. |
| `cli` | Argument parsing, the interactive wizard, and **all** user-facing output. |
| `__main__` | `python -m pyiecwind` entry point. |

## Design rules

- **Library code does not print.** Advisory validation issues are emitted as
  `IECWindWarning`; batch outcomes are returned as a `GenerationResult` carrying
  the written paths and structured `GenerationError` diagnostics. The CLI is the
  only place that writes to stdout/stderr and the only place that chooses an exit
  code.
- **One version, one source.** `VERSION` is read from installed package metadata
  (`pyproject.toml`), so code and packaging can never drift. A test guards this.
- **Output is locked.** Every generator's numeric output is pinned by the golden
  corpus described in {doc}`verification`; refactors must be output-preserving.

## Data flow

```
input file ──parse_input_file──▶ IECParameters ──generate_all──▶ GenerationResult
   (parsing)                       (models)         (generation)     │
                                                                     ▼
                                                        <code>.wnd files
                                                          (WindFileWriter)
```

The wizard short-circuits the parsing step by constructing `IECParameters`
directly from interactive prompts, then feeds the same `generate_all` path.
