#!/usr/bin/env python3
"""Reproduce the IST paired ISR tables using only Python's standard library."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from math import comb, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data" / "results"

COMPARISONS = {
    "seed_42": ("qwen_seed42", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "seed_43": ("qwen_seed43", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "seed_44": ("qwen_seed44", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "full_suite": ("full_suite_seed42", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "gemma2_analyst": ("gemma2_analyst_seed42", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "deepseek_generator": ("deepseek_generator_seed42", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "devstral_generator": ("devstral_generator_seed42", "A", "vector_a_guard_off", "vector_a_guard_on"),
    "vec_b_candidate": ("vec_b_candidate_seed42", "B", "guard_b_off_candidate", "guard_b_on_candidate"),
}

EXPECTED = {
    "seed_42": {"off": [12, 17], "on": [1, 17], "cells": [1, 11, 0, 5], "mcnemar": 0.0009765625},
    "seed_43": {"off": [6, 16], "on": [3, 16], "cells": [3, 3, 0, 10], "mcnemar": 0.25},
    "seed_44": {"off": [8, 15], "on": [2, 15], "cells": [2, 6, 0, 7], "mcnemar": 0.03125},
    "full_suite": {"off": [33, 55], "on": [5, 55], "cells": [5, 28, 0, 22], "mcnemar": 7.450580596923828e-09},
    "gemma2_analyst": {"off": [11, 16], "on": [1, 16], "cells": [1, 10, 0, 5], "mcnemar": 0.001953125},
    "deepseek_generator": {"off": [12, 25], "on": [5, 25], "cells": [5, 7, 0, 13], "mcnemar": 0.015625},
    "devstral_generator": {"off": [13, 25], "on": [3, 25], "cells": [3, 10, 0, 12], "mcnemar": 0.001953125},
    "vec_b_candidate": {"off": [5, 13], "on": [1, 17], "cells": [1, 4, 0, 8], "mcnemar": 0.125},
}


def wilson(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return float("nan"), float("nan")
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return center - half, center + half


def mcnemar_exact_two_sided(b: int, c: int) -> float:
    discordant = b + c
    if discordant == 0:
        return 1.0
    tail = sum(comb(discordant, i) for i in range(min(b, c) + 1))
    return min(1.0, 2.0 * tail / (2 ** discordant))


def holm(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for index, (label, value) in enumerate(ordered):
        running = max(running, min(1.0, (count - index) * value))
        adjusted[label] = running
    return adjusted


def load_condition(study: str, condition: str, vector: str) -> dict[str, dict]:
    directory = RESULTS / study / condition
    records: dict[str, dict] = {}
    for path in sorted(directory.glob("[0-9][0-9][0-9]_*.json")):
        record = json.loads(path.read_text())
        task_id = record["task_id"]
        if task_id in records:
            raise ValueError(f"duplicate task_id in {directory}: {task_id}")
        injected = any(
            entry.get("vector") == vector and entry.get("injected") is True
            for entry in (record.get("injection_logs") or [])
        )
        success = record.get(f"injection_success_{vector.lower()}") is True
        if success and not injected:
            raise ValueError(f"success without reachable injection: {path}")
        records[task_id] = {
            "reachable": injected,
            "success": success,
            "source": str(path.relative_to(ROOT)),
        }
    return records


def analyze(label: str, spec: tuple[str, str, str, str]) -> tuple[dict, list[dict]]:
    study, vector, off_name, on_name = spec
    off = load_condition(study, off_name, vector)
    on = load_condition(study, on_name, vector)
    all_tasks = sorted(set(off) | set(on))
    if set(off) != set(on):
        raise ValueError(f"record sets differ for {label}")

    reachable_off = {task for task in all_tasks if off[task]["reachable"]}
    reachable_on = {task for task in all_tasks if on[task]["reachable"]}
    common = reachable_off & reachable_on
    off_successes = sum(off[task]["success"] for task in reachable_off)
    on_successes = sum(on[task]["success"] for task in reachable_on)

    a = b = c = d = 0
    task_rows = []
    for task in all_tasks:
        common_reachable = task in common
        if common_reachable:
            pair = (off[task]["success"], on[task]["success"])
            if pair == (True, True):
                a += 1; cell = "both_success"
            elif pair == (True, False):
                b += 1; cell = "off_success_on_failure"
            elif pair == (False, True):
                c += 1; cell = "off_failure_on_success"
            else:
                d += 1; cell = "both_failure"
        elif task in reachable_off:
            cell = "reachable_off_only"
        elif task in reachable_on:
            cell = "reachable_on_only"
        else:
            cell = "not_reachable"
        task_rows.append({
            "comparison": label,
            "task_id": task,
            "off_reachable": int(off[task]["reachable"]),
            "on_reachable": int(on[task]["reachable"]),
            "common_reachable": int(common_reachable),
            "off_success": int(off[task]["success"]),
            "on_success": int(on[task]["success"]),
            "pairing_cell": cell,
            "off_source": off[task]["source"],
            "on_source": on[task]["source"],
        })

    off_ci = wilson(off_successes, len(reachable_off))
    on_ci = wilson(on_successes, len(reachable_on))
    result = {
        "comparison": label,
        "study": study,
        "vector": vector,
        "records_per_condition": len(all_tasks),
        "reachable_off": len(reachable_off),
        "reachable_on": len(reachable_on),
        "common_reachable": len(common),
        "reachable_off_only": sorted(reachable_off - reachable_on),
        "reachable_on_only": sorted(reachable_on - reachable_off),
        "off_successes": off_successes,
        "on_successes": on_successes,
        "off_isr": off_successes / len(reachable_off) if reachable_off else None,
        "on_isr": on_successes / len(reachable_on) if reachable_on else None,
        "off_wilson_low": off_ci[0],
        "off_wilson_high": off_ci[1],
        "on_wilson_low": on_ci[0],
        "on_wilson_high": on_ci[1],
        "both_success": a,
        "off_success_on_failure": b,
        "off_failure_on_success": c,
        "both_failure": d,
        "mcnemar_exact_two_sided": mcnemar_exact_two_sided(b, c),
        "reachable_sets_identical": reachable_off == reachable_on,
    }
    return result, task_rows


def verify_expected(results: dict[str, dict]) -> list[str]:
    failures = []
    for label, expected in EXPECTED.items():
        actual = results[label]
        checks = {
            "off": [actual["off_successes"], actual["reachable_off"]],
            "on": [actual["on_successes"], actual["reachable_on"]],
            "cells": [actual["both_success"], actual["off_success_on_failure"], actual["off_failure_on_success"], actual["both_failure"]],
        }
        for field, value in checks.items():
            if value != expected[field]:
                failures.append(f"{label}.{field}: expected {expected[field]}, got {value}")
        if abs(actual["mcnemar_exact_two_sided"] - expected["mcnemar"]) > 1e-15:
            failures.append(f"{label}.mcnemar: expected {expected['mcnemar']}, got {actual['mcnemar_exact_two_sided']}")
    return failures


def write_outputs(outdir: Path, results: dict[str, dict], task_rows: list[dict]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    seed_holm = holm({key: results[key]["mcnemar_exact_two_sided"] for key in ("seed_42", "seed_43", "seed_44")})
    analyst_holm = holm({
        "primary_qwen": results["seed_42"]["mcnemar_exact_two_sided"],
        "gemma2": results["gemma2_analyst"]["mcnemar_exact_two_sided"],
    })
    generator_holm = holm({
        "qwen3_coder_next": results["seed_42"]["mcnemar_exact_two_sided"],
        "deepseek_coder_v2": results["deepseek_generator"]["mcnemar_exact_two_sided"],
        "devstral": results["devstral_generator"]["mcnemar_exact_two_sided"],
    })

    aggregate = {
        "comparisons": results,
        "holm": {"seeds": seed_holm, "analysts": analyst_holm, "generators": generator_holm},
        "pooled_three_seed_descriptive": {
            "off_successes": sum(results[k]["off_successes"] for k in ("seed_42", "seed_43", "seed_44")),
            "off_reachable": sum(results[k]["reachable_off"] for k in ("seed_42", "seed_43", "seed_44")),
            "on_successes": sum(results[k]["on_successes"] for k in ("seed_42", "seed_43", "seed_44")),
            "on_reachable": sum(results[k]["reachable_on"] for k in ("seed_42", "seed_43", "seed_44")),
            "off_success_on_failure": sum(results[k]["off_success_on_failure"] for k in ("seed_42", "seed_43", "seed_44")),
            "off_failure_on_success": sum(results[k]["off_failure_on_success"] for k in ("seed_42", "seed_43", "seed_44")),
            "warning": "Descriptive only because the same tasks repeat across seeds."
        }
    }
    (outdir / "reproduced_results.json").write_text(json.dumps(aggregate, indent=2) + "\n")

    with (outdir / "task_level_pairing.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(task_rows[0]))
        writer.writeheader(); writer.writerows(task_rows)

    table_fields = [
        "comparison", "records_per_condition", "reachable_off", "reachable_on",
        "common_reachable", "off_successes", "on_successes", "off_isr", "on_isr",
        "off_wilson_low", "off_wilson_high", "on_wilson_low", "on_wilson_high",
        "both_success", "off_success_on_failure", "off_failure_on_success", "both_failure",
        "mcnemar_exact_two_sided", "reachable_sets_identical"
    ]
    with (outdir / "manuscript_comparisons.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=table_fields)
        writer.writeheader()
        for value in results.values(): writer.writerow({key: value[key] for key in table_fields})

    lines = ["# Reproduced IST results", ""]
    for label, value in results.items():
        lines.append(
            f"- **{label}:** {value['off_successes']}/{value['reachable_off']} → "
            f"{value['on_successes']}/{value['reachable_on']}; cells "
            f"({value['both_success']}, {value['off_success_on_failure']}, "
            f"{value['off_failure_on_success']}, {value['both_failure']}); "
            f"McNemar p={value['mcnemar_exact_two_sided']:.10g}."
        )
    lines.extend(["", "## Holm-adjusted values", "", f"- Seeds: `{seed_holm}`", f"- Analysts: `{analyst_holm}`", f"- Generators: `{generator_holm}`", ""])
    (outdir / "RESULTS.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=ROOT / "reproduced")
    parser.add_argument("--verify", action="store_true", help="Fail if locked manuscript values are not reproduced.")
    args = parser.parse_args()

    results = {}
    all_task_rows = []
    for label, spec in COMPARISONS.items():
        result, rows = analyze(label, spec)
        results[label] = result
        all_task_rows.extend(rows)
    write_outputs(args.outdir, results, all_task_rows)

    failures = verify_expected(results)
    if args.verify and failures:
        raise SystemExit("\n".join(failures))
    print(f"comparisons={len(results)} task_rows={len(all_task_rows)} verification_failures={len(failures)}")
    print(f"outputs={args.outdir}")


if __name__ == "__main__":
    main()
