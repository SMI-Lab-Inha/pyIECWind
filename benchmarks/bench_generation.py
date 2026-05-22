"""Tiny benchmark for wind-file generation.

Times generating the full golden scenario matrix (all case families across both
unit systems, both editions, and the turbine-class/category range). Dependency
free -- just the standard library and pyiecwind.

Usage::

    python benchmarks/bench_generation.py [repeats]
"""

from __future__ import annotations

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


def main(argv: list[str]) -> int:
    repeats = int(argv[1]) if len(argv) > 1 else 5

    files = run_once()  # warm up imports and the filesystem
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        run_once()
        samples.append(time.perf_counter() - start)

    best = min(samples)
    mean = sum(samples) / len(samples)
    print(f"scenarios={len(SCENARIOS)}  files/run={files}  repeats={repeats}")
    print(f"best={best * 1e3:.1f} ms   mean={mean * 1e3:.1f} ms   per-file={best / files * 1e6:.0f} us")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
