#!/usr/bin/env python3
"""Run the ProVerif models for the TDT-Pipe authentication pipeline."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


MODELS = [
    "tdt_pipe_reachability_sanity.pv",
    "tdt_pipe_pipeline.pv",
    "tdt_pipe_pipeline_atomic_replay.pv",
]


def run_model(proverif: str, model: Path, output_dir: Path) -> int:
    result = subprocess.run(
        [proverif, str(model)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    stem = model.stem
    output_path = output_dir / f"{stem}_proverif_output.txt"
    output_path.write_text(result.stdout, encoding="utf-8")

    summary_lines = []
    for line in result.stdout.splitlines():
        if "RESULT" in line:
            summary_lines.append(line)

    summary_path = output_dir / f"{stem}_proverif_summary.txt"
    if summary_lines:
        summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    else:
        summary_path.write_text("No RESULT lines found in ProVerif output.\n", encoding="utf-8")

    return result.returncode


def main() -> None:
    root = Path(__file__).resolve().parent
    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    proverif = shutil.which("proverif")
    if proverif is None:
        message = (
            "ProVerif executable not found in PATH.\n"
            "Install ProVerif and rerun this script.\n"
        )
        (output_dir / "proverif_not_available.txt").write_text(message, encoding="utf-8")
        raise SystemExit(message)

    failures = []
    for name in MODELS:
        model = root / name
        code = run_model(proverif, model, output_dir)
        if code != 0:
            failures.append((name, code))

    if failures:
        details = ", ".join(f"{name} exited with {code}" for name, code in failures)
        raise SystemExit(details)


if __name__ == "__main__":
    main()
