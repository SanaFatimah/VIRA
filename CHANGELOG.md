# Artifact changelog

- Hardened the clean-state consistency check after a read-only audit of 1,063
  manuscript-used task-condition records. Clean now requires both an empty
  finding set and zero CVSS on every execution path, and parser failures cannot
  be classified as clean by the standalone experiment runner. Zero historical
  records and zero reported manuscript results were affected.
