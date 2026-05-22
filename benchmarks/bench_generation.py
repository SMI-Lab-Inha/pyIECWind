"""Tiny benchmark for wind-file generation.

Times generating the full golden scenario matrix (all case families across both
unit systems, both editions, and the turbine-class/category range). Dependency
free -- just the standard library and pyiecwind.

Usage::

    python benchmarks/bench_generation.py [repeats]      # human-readable
    python benchmarks/bench_generation.py [repeats] --json  # machine-readable

The ``--json`` output is suitable for recording a baseline and comparing against
later runs. See the threshold policy in ``docs/contributing.rst`` -- CI runs this
as a smoke test (must complete without error); wall-clock comparison is done
offline against a recorded baseline rather than gated in CI, because shared
runners are too noisy for a stable threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "tests"))

from golden_cases import SCENARIOS  # noqa: E402  (path set up above)
from pyiecwind import generate_all  # noqa: E402


def run_once() -> int:
    """Generate every scenario into a throwaway directory; return the file count."""

    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        for scenario in SCENARIOS:
            total += generate_all(scenario.parameters(), output_dir=out / scenario.name).count
    return total


def measure(repeats: int) -> dict[str, float | int]:
    """Run the workload ``repeats`` times (after a warm-up) and summarise timings."""

    files = run_once()  # warm up imports and the filesystem
    samples = [(_timed_run()) for _ in range(repeats)]
    best = min(samples)
    return {
        "scenarios": len(SCENARIOS),
        "files_per_run": files,
        "repeats": repeats,
        "best_ms": round(best * 1e3, 3),
        "mean_ms": round(sum(samples) / len(samples) * 1e3, 3),
        "per_file_us": round(best / files * 1e6, 1),
    }


def _timed_run() -> float:
    start = time.perf_counter()
    run_once()
    return time.perf_counter() - start


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark wind-file generation.")
    parser.add_argument("repeats", nargs="?", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    result = measure(args.repeats)
    if args.json:
        print(json.dumps(result))
    else:
        print(f"scenarios={result['scenarios']}  files/run={result['files_per_run']}  repeats={result['repeats']}")
        print(f"best={result['best_ms']} ms   mean={result['mean_ms']} ms   per-file={result['per_file_us']} us")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
