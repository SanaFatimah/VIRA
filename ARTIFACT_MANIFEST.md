# Artifact manifest

## Studies and task records

| Artifact study | Conditions | Records per condition | Purpose |
|---|---|---:|---|
| `qwen_seed42` | `vector_a_guard_off/on` | 35 | Primary Qwen configuration, seed 42 |
| `qwen_seed43` | `vector_a_guard_off/on` | 35 | Seed robustness |
| `qwen_seed44` | `vector_a_guard_off/on` | 35 | Seed robustness |
| `full_suite_seed42` | `vector_a_guard_off/on` | 121 | Complete-suite comparison |
| `gemma2_analyst_seed42` | `vector_a_guard_off/on` | 35 | Analyst replacement |
| `deepseek_generator_seed42` | `vector_a_guard_off/on` | 35 | Generator replacement |
| `devstral_generator_seed42` | `vector_a_guard_off/on` | 35 | Generator replacement |
| `vec_b_candidate_seed42` | `guard_b_off/on_candidate` | 35 | Diagnostic Vec-B comparison |
| `normal_operation_seed42` | four configurations | 35 | Normal-operation outcomes |

Total sanitized task records: 872. Each condition also contains its available
phase-summary JSON. `data/results/record_manifest.json` is machine-readable.

## Included source

- Complete Generator, Attacker, Analyst, and Manipulator implementations.
- Embedded system and user prompts.
- Guard A, Guard B, no-evidence short circuit, convergence, and persistence.
- SecurityEval loaders, CodeQL runner, Docker sandbox, and Ollama configuration.
- Condition and campaign configuration material.

## Deliberately excluded

- Git metadata and commit history.
- Virtual environments, caches, compiled bytecode, model weights, and archives.
- CodeQL distribution and generated databases.
- Environment files, credentials, editor configuration, and local agent files.
- Raw console logs containing development-machine tracebacks.
- Timer reports because the manuscript makes no efficiency claim and the
  primary Qwen normal-operation timer is incomplete.
- Earlier conference-artifact files, comments, identifiers, and URLs.
