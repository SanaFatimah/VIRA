# Reproduced IST results

- **seed_42:** 12/17 → 1/17; cells (1, 11, 0, 5); McNemar p=0.0009765625.
- **seed_43:** 6/16 → 3/16; cells (3, 3, 0, 10); McNemar p=0.25.
- **seed_44:** 8/15 → 2/15; cells (2, 6, 0, 7); McNemar p=0.03125.
- **full_suite:** 33/55 → 5/55; cells (5, 28, 0, 22); McNemar p=7.450580597e-09.
- **gemma2_analyst:** 11/16 → 1/16; cells (1, 10, 0, 5); McNemar p=0.001953125.
- **deepseek_generator:** 12/25 → 5/25; cells (5, 7, 0, 13); McNemar p=0.015625.
- **devstral_generator:** 13/25 → 3/25; cells (3, 10, 0, 12); McNemar p=0.001953125.
- **vec_b_candidate:** 5/13 → 1/17; cells (1, 4, 0, 8); McNemar p=0.125.

## Holm-adjusted values

- Seeds: `{'seed_42': 0.0029296875, 'seed_44': 0.0625, 'seed_43': 0.25}`
- Analysts: `{'primary_qwen': 0.001953125, 'gemma2': 0.001953125}`
- Generators: `{'qwen3_coder_next': 0.0029296875, 'devstral': 0.00390625, 'deepseek_coder_v2': 0.015625}`
