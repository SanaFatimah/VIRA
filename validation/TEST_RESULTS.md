# Reproduction and integrity test results

Tests were run on 2026-08-18 from a clean output directory.

## Statistical reproduction

Command:

```bash
python3 analysis/reproduce_results.py --verify --outdir /tmp/vira-ist-reproduction-test
```

Result:

```text
comparisons=8 task_rows=366 verification_failures=0
```

The 296-row structural audit covers the three primary seeds, the 121-task full
suite, the replacement Analyst, and the explicitly diagnostic Vec-B candidate
pairing. The two replacement Generator comparisons are calculated separately
from 70 additional task rows. The command reports 366 rows because its output
CSV combines both scopes; this must not be described as a 366-row structural
audit or as a 296-row audit that includes the Generator comparisons. Exact
two-sided McNemar tests, Holm adjustments, Wilson intervals, and table values
are recomputed from the sanitized task records.

## Record integrity

- JSON files parsed: 900; parse failures: 0.
- Sanitized task-condition records: 872.
- Stratified task list: 35 unique tasks.
- Complete task list: 121 unique tasks.
- Removed `run_id` keys found: 0.
- Removed `timestamp` keys found: 0.
- Included Python files compile successfully.

## Anonymity scan

Command:

```bash
python3 validation/audit_anonymity.py
```

Result:

```text
ANONYMITY AUDIT PASSED
files_scanned=932
git_metadata=absent
```

The scanner checks both names and contents for the project-specific denylist,
email addresses, workstation paths, prior-artifact references, submission
identifiers, and identifying institutional terms.

## Scope limitation

These tests establish record integrity and numerical reproduction. They do not
re-execute all language-model calls, Docker workloads, or CodeQL analyses.
