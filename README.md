# VIRA IST Anonymous Replication Artifact

This package is a journal-specific, anonymous replication artifact for the
VIRA manuscript. It is independent of earlier conference artifacts and contains
no repository history, author metadata, institutional metadata, or upload URL.

## Fast reproduction of the reported statistics

Only Python 3.10+ and the standard library are required to reproduce the
headline tables from the saved task records:

```bash
python3 analysis/reproduce_results.py --verify
```

The command writes fresh outputs under `reproduced/` and exits nonzero if any
locked manuscript count, paired cell, or exact McNemar value differs. Expected
outputs are tracked in `analysis/`:

- `analysis/RESULTS.md`
- `analysis/manuscript_comparisons.csv`
- `analysis/reproduced_results.json`
- `analysis/task_level_pairing.csv`

The script calculates, rather than hard-codes as output, reachability,
condition-specific ISR, Wilson 95% intervals, task-paired cells, exact
two-sided McNemar values, and Holm-adjusted p-values. Locked values are used
only by `--verify` as regression assertions.

## Headline values reproduced

| Study | Guard off | Guard on | Exact two-sided McNemar p | Holm p, where applicable |
|---|---:|---:|---:|---:|
| Seed 42 | 12/17 | 1/17 | 0.0009765625 | 0.0029296875 |
| Seed 43 | 6/16 | 3/16 | 0.25 | 0.25 |
| Seed 44 | 8/15 | 2/15 | 0.03125 | 0.0625 |
| Full 121-task suite | 33/55 | 5/55 | 7.4505805969e-09 | — |
| Gemma2 Analyst | 11/16 | 1/16 | 0.001953125 | 0.001953125 |
| DeepSeek Generator | 12/25 | 5/25 | 0.015625 | 0.015625 |
| Devstral Generator | 13/25 | 3/25 | 0.001953125 | 0.00390625 |
| Vec-B candidate (diagnostic) | 5/13 | 1/17 | 0.125 on 13 common-reachable tasks | — |

The pooled three-seed Vec-A rates, 26/48 and 6/48, are descriptive because
the same tasks repeat across seeds.

## Package layout

```text
analysis/       extraction, statistics, expected tables, task-paired CSV
config/         conditions, model/runtime metadata, Manipulator templates
data/           exact 35- and 121-task lists plus sanitized task records
docker/         sandbox image/configuration material
docs/           prompt and data documentation
src/            VIRA agents, guards, Manipulators, pipeline, and tools
validation/     record-validation and anonymity-audit material
```

See `ARTIFACT_MANIFEST.md` for the precise study-to-directory mapping.

## Task sets

- `data/task_lists/securityeval_stratified.json`: exact stratified 35-task set.
- `data/task_lists/securityeval_full.json`: complete 121-task evaluation set.

Task IDs containing strings such as `author`, `mitre`, `sonar`, or `codeql`
are upstream benchmark identifiers, not manuscript-author metadata.

## Saved records

Every condition directory contains one deterministically named JSON record per
task and a sanitized `phase_summary.json`. Original run IDs and wall-clock
timestamps were removed because they are unnecessary for the reported
statistics. Absolute development-machine paths were replaced or removed.

Reachability is reconstructed from an injection-log entry with matching vector
and `injected=true`. Success is read from `injection_success_a` or
`injection_success_b`. See `validation/PAIRING_AND_MANUAL_VALIDATION.md`.

## Inspecting prompts and defenses

- Generator system/user prompting: `src/agents/generator.py`
- Attacker system/user prompting: `src/agents/attacker.py`
- Analyst system/user prompting and no-evidence short circuit:
  `src/agents/analyst.py`
- Guard A implementation: `_enforce_evidence_rules` in the Analyst file.
- Guard B implementation: patch-feedback validation in the Generator file.
- Vec-A/Vec-B templates and success detectors: `src/agents/manipulator.py`
  and `config/manipulator_templates.json`.
- Experimental presets: `config/conditions.json` and `src/main.py`.

## Full experimental rerun

Full reruns require Ollama model weights, Docker, NVIDIA drivers, and CodeQL,
which are not redistributed. Install Python dependencies in an isolated
environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
docker build -f docker/Dockerfile.python-sandbox -t vira-python-sandbox .
export CODEQL_BIN=/path/to/codeql
```

Example seed-42 Vec-A pair:

```bash
.venv/bin/python src/main.py --iterations 5 --condition vector_a_undefended --seed 42 --task-set stratified --result-root rerun_results
.venv/bin/python src/main.py --iterations 5 --condition vector_a_defended --seed 42 --task-set stratified --result-root rerun_results
```

Full-suite pair:

```bash
.venv/bin/python src/main.py --iterations 5 --condition vector_a_undefended --seed 42 --task-set full --result-root rerun_results_full
.venv/bin/python src/main.py --iterations 5 --condition vector_a_defended --seed 42 --task-set full --result-root rerun_results_full
```

Replacement configurations use the same commands with either
`--analyst-model gemma2:27b` or the relevant `--generator-model` tag from
`config/models_and_environment.json`.

## Environment and interpretation

The campaigns used an NVIDIA GeForce RTX 4090, Ollama, Docker 24.0.5,
sequential execution, an 8,192-token runtime context, and at most five repair
iterations. Complete Ollama IDs and model-blob digests, the complete container
ID and repository digest, CodeQL pack provenance, seed derivation,
agent-specific token ceilings, decoding-parameter provenance, and the
historical unpinned sandbox installation command are in
`config/models_and_environment.json`. Identifiers in that file are never
abbreviated. Parameters not explicitly passed by VIRA are distinguished
between model-definition values and values that relied on Ollama 0.18.3
defaults. The latter are not assigned guessed numeric values when the effective
values were not persisted.

Model replacements are comparisons among tested configurations, not isolated
causal effects of model family. The Vec-B candidate conditions also differ in
Vector-A activation and therefore remain diagnostic rather than an isolated
Guard-B estimate.

## Anonymity audit

Run:

```bash
python3 validation/audit_anonymity.py
```

The audit checks file contents and names for email addresses, known development
user/workspace tokens, local-machine path prefixes, conference-artifact terms,
submission identifiers, and old anonymous-artifact URLs. Generic `/home`
strings inside SecurityEval benchmark programs are preserved as task content
and are not development-machine paths.

## Known limitations

- Three representative records were manually checked for extraction
  consistency; this is not independent semantic ground-truth annotation.
- Model weights, CodeQL binaries/databases, Docker images, and GPU drivers are
  not redistributed.
- The original primary marginal campaign lacks the task-level join required
  for McNemar reconstruction and is therefore not included as paired evidence.
- Efficiency claims are not included because the primary timing records are
  incomplete.
