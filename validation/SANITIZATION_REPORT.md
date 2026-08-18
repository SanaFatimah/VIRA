# Sanitization report

This directory is a new, independent artifact assembled from the research
records. The source repository was not modified, and no version-control
history was copied.

## Excluded

- Git history, remotes, commit metadata, branches, and issue/PR metadata.
- Prior conference-artifact directories, URLs, identifiers, and comments.
- Environment files, credentials, editor state, agent configuration, caches,
  virtual environments, downloaded model weights, local CodeQL installations,
  generated databases, and unrelated development logs.
- Developer-only timer reports and raw console logs containing workstation
  paths. Their research-relevant task results are represented by the sanitized
  JSON records.

## Sanitized

- Task records were deterministically renamed using task order and benchmark
  task identifier.
- Run identifiers and wall-clock timestamps were removed recursively from the
  copied JSON records and phase summaries.
- Developer usernames and absolute workstation paths were removed from code,
  configuration, records, and documentation.
- A project-specific CodeQL database label was replaced with a generic label.
- CodeQL discovery now uses `CODEQL_BIN` or the executable on `PATH`.
- Task-list and output paths are artifact-relative. Reruns write to
  `rerun_results/` and `rerun_logs/`, never to the preserved records.
- One email-shaped string inside generated benchmark code was converted to an
  explicitly invalid, non-address form. It was unrelated to outcome fields.

## Deliberately retained

- Upstream SecurityEval task identifiers and task source are retained so that
  task identity and pairing remain auditable.
- Generic paths such as `/home` appearing inside benchmark test inputs are
  retained; they are program inputs, not developer paths.
- Model tags, parameter sizes, quantization, and hardware/runtime descriptions
  are retained because they are required for reproducibility.

Run `python3 validation/audit_anonymity.py` from the artifact root to repeat the
machine audit. A final human inspection is still required before public upload.
