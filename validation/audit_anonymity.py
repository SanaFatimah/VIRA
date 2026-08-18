#!/usr/bin/env python3
"""Fail on identifying metadata or stale conference-artifact references."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {"", ".py", ".md", ".txt", ".json", ".csv", ".yml", ".yaml", ".sh", ".gitignore"}

# Tokens are assembled so the audit source does not trigger its own checks.
FORBIDDEN_LITERALS = [
    "ss" + "lab",
    "sa" + "na",
    "ac" + "sac",
    "ac" + "sac26",
    "anonymous" + ".4open" + ".science",
    "/home/" + "sslab",
    "C:" + "\\Users\\",
]

PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@(?!app\.(?:route|post|get|put|delete|patch)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "institutional role/name": re.compile(r"\b(professor|university|laboratory)\b", re.I),
    "submission identifier": re.compile(r"\bsubmission\s*(?:id|number|no\.?|#)\b\s*[:#-]?\s*[A-Z0-9-]+", re.I),
    "Unix development path": re.compile(r"/(?:home|Users)/[^/\s\"']+/(?:Documents|Desktop|workspace|projects?)/", re.I),
}


def text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            yield path


def main() -> None:
    findings = []
    if (ROOT / ".git").exists():
        findings.append("Git metadata directory exists")

    for path in text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        relative = str(path.relative_to(ROOT))
        lower_name = relative.lower()
        for literal in FORBIDDEN_LITERALS:
            if literal.lower() in lower_name:
                findings.append(f"filename contains forbidden token {literal!r}: {relative}")
        text = path.read_text(errors="replace")
        lower = text.lower()
        for literal in FORBIDDEN_LITERALS:
            if literal.lower() in lower:
                findings.append(f"content contains forbidden token {literal!r}: {relative}")
        for label, pattern in PATTERNS.items():
            match = pattern.search(text)
            if match:
                findings.append(f"{label} {match.group(0)!r}: {relative}")

    if findings:
        print("ANONYMITY AUDIT FAILED")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)
    print("ANONYMITY AUDIT PASSED")
    print(f"files_scanned={sum(1 for _ in text_files())}")
    print("git_metadata=absent")


if __name__ == "__main__":
    main()
