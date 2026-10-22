"""Traceability guard for the project test suite.

Every test carries one of the canon's three legal goals. A ``spec:`` marker
must point at a durable spec, not at an ephemeral ticket. An ``invariant:`` in
a contract test must name a durable invariant: an ontology code from
``docs/ontology.md`` or a ``docs/<path>#<section>`` reference. Engine-level
invariants stay descriptive until their durable reference exists.

The criterion after ``#`` is a human locator, not an HTML anchor: numbered plan
items have no heading anchor, so the guard checks that the file exists and the
criterion is non-empty. The marker carries the statement; ``path#section`` names
the durable artifact or rule it guards, not necessarily the verbatim wording.

Markers are read at line start, optionally after a docstring opening quote. An
inline mention inside prose or a code literal is not a marker: the guard cannot
tell a claim from an example there, so those mentions stay out of scope.

spec: docs/decisions/ontoship-core.md#одно правило качества — durable traceability
invariant: docs/decisions/ontoship-core.md#одно правило качества — the contract check can fail
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"
ONTOLOGY = REPO / "docs" / "ontology.md"

MARKER_RE = re.compile(
    r'^\s*(?:"""|\'\'\')?(spec|invariant|target):\s*(.+?)\s*(?:"""|\'\'\')?\s*$',
    re.MULTILINE,
)
PATH_RE = re.compile(r"(docs/[^\s#`]+)#([^\s`]+)")
TICKET_PATH_RE = re.compile(r"(?:^|\s)(tickets/[^\s#`]+)")
I_CODE_RE = re.compile(r"\bI(\d+)\b")
ENGINE_TESTS = {"test_engine.py", "test_lint_paths.py", "test_redact.py"}


def _markers(text: str):
    """Yield ``(kind, value)`` for every line-start marker in a module."""
    for match in MARKER_RE.finditer(text):
        yield match.group(1), match.group(2).strip()


def _ontology_codes() -> set[str]:
    return set(re.findall(r"^\|\s*(I\d+)\s*\|", ONTOLOGY.read_text("utf-8"),
                          re.MULTILINE))


def _marker_errors(text: str, filename: str,
                   codes: set[str] | None = None) -> list[str]:
    """Return every traceability violation in one test module; empty is sound."""
    codes = codes if codes is not None else _ontology_codes()
    errors: list[str] = []
    for kind, value in _markers(text):
        ticket = TICKET_PATH_RE.search(value)
        if ticket:
            errors.append(f"{kind}: points at the ephemeral tracker "
                          f"{ticket.group(1)!r}")
            continue
        if kind == "spec":
            match = PATH_RE.search(value)
            if not match:
                errors.append(f"spec: no docs/<path>#<criterion> in {value!r}")
                continue
            path, criterion = match.groups()
            if not criterion.strip():
                errors.append(f"spec: empty criterion in {value!r}")
            elif not (REPO / path).is_file():
                errors.append(f"spec: missing file {path!r}")
        elif kind == "invariant" and filename not in ENGINE_TESTS:
            found = I_CODE_RE.findall(value)
            if found:
                for code in found:
                    if f"I{code}" not in codes:
                        errors.append(f"invariant: unknown ontology code I{code}")
            else:
                match = PATH_RE.search(value)
                if not match:
                    errors.append(f"invariant: no I<n> or docs/<path>#<section> "
                                  f"in {value!r}")
                    continue
                path, section = match.groups()
                if not section.strip():
                    errors.append(f"invariant: empty section in {value!r}")
                elif not (REPO / path).is_file():
                    errors.append(f"invariant: missing file {path!r}")
        elif kind == "target" and not value:
            errors.append("target: empty reference")
    return errors


def test_every_test_marker_resolves_to_a_durable_source():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — durable markers."""
    codes = _ontology_codes()
    failures: list[str] = []
    for path in sorted(TESTS.glob("test_*.py")):
        errors = _marker_errors(path.read_text("utf-8"), path.name, codes)
        failures.extend(f"{path.name}: {error}" for error in errors)
    assert not failures, "\n".join(failures)


def test_traceability_guard_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    guard rejects an ephemeral target, a missing path, an unknown invariant
    code and an unnamed contract invariant."""
    codes = _ontology_codes()
    assert _marker_errors(
        "spec: docs/decisions/ontoship-core.md#три фазы — x",
        "test_skill_x.py", codes) == []
    assert _marker_errors("invariant: I2 — x", "test_skill_x.py", codes) == []
    assert _marker_errors(
        "invariant: docs/decisions/ontoship-core.md#три фазы — x",
        "test_skill_x.py", codes) == []
    assert _marker_errors("invariant: descriptive only", "test_engine.py",
                          codes) == []

    bad = (
        ("spec: tickets/core-kb/03.md — x", "test_skill_x.py", "ephemeral"),
        ("spec: docs/decisions/ontoship-core.md — x", "test_skill_x.py",
         "no docs/<path>#<criterion>"),
        ("spec: docs/decisions/nope.md#три фазы — x", "test_skill_x.py",
         "missing file"),
        ("invariant: descriptive only", "test_skill_x.py",
         "no I<n> or docs/<path>#<section>"),
        ("invariant: I99 — x", "test_skill_x.py", "unknown ontology code I99"),
    )
    for text, filename, needle in bad:
        errors = _marker_errors(text, filename, codes)
        assert any(needle in error for error in errors), (text, errors)