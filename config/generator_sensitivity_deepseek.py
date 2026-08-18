#!/usr/bin/env python3
"""Run the seed-42, 35-task, three-condition Generator sensitivity campaign."""

import os
import re
import subprocess
import sys
import time
from pathlib import Path


MODEL = "deepseek-coder-v2:16b"
MODEL_SUFFIX = "deepseek_coder_v2_16b"
CONDITIONS = ("baseline", "vector_a_undefended", "vector_a_defended")
ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = ARTIFACT_ROOT / "rerun_results"
LOG_ROOT = ARTIFACT_ROOT / "rerun_logs"
MAIN = ARTIFACT_ROOT / "src" / "main.py"


def completed_indices(condition: str) -> set[int]:
    directory = RESULT_ROOT / "seed_42" / f"{condition}_generator_{MODEL_SUFFIX}"
    completed = set()
    for path in directory.glob("run_p4_*.json"):
        match = re.search(r"_python_(\d+)_\d+\.json$", path.name)
        if match:
            completed.add(int(match.group(1)))
    return completed


def run_condition(condition: str) -> None:
    completed_set = completed_indices(condition)
    start_at = next((index for index in range(1, 36) if index not in completed_set), 36)
    directory = RESULT_ROOT / "seed_42" / f"{condition}_generator_{MODEL_SUFFIX}"
    if len(completed_set) >= 35:
        print(f"=== SKIP {condition}: already has 35 results ===", flush=True)
        return

    LOG_ROOT.mkdir(exist_ok=True)
    log_path = LOG_ROOT / f"generator_sensitivity_{condition}_deepseek_s42.log"
    command = [
        sys.executable, "-u", str(MAIN),
        "--iterations", "5",
        "--condition", condition,
        "--seed", "42",
        "--task-set", "stratified",
        "--generator-model", MODEL,
        "--start-at", str(start_at),
        "--result-root", str(RESULT_ROOT),
    ]
    print(f"=== START {condition} at {time.ctime()} start_at={start_at} ===", flush=True)
    with log_path.open("a") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=os.environ.copy())
    print(f"=== END {condition} rc={result.returncode} at {time.ctime()} ===", flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> None:
    for condition in CONDITIONS:
        run_condition(condition)
    print(f"=== GENERATOR SENSITIVITY CAMPAIGN COMPLETE at {time.ctime()} ===", flush=True)


if __name__ == "__main__":
    main()
