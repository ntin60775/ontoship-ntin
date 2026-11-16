"""The method-contract reference file at the core root.

The connector norm (canon, «Границы»): the reference is the core file
``method-contract.json``, the declaration is the team bundle manifest;
the chain skill of the team bundle reads the file and compares. The
file carries only the contract — the core version is a git tag, there
is no machine version file (core-team-boundaries, trivial decisions).

spec: docs/plans/core-team-boundaries.md#готово — «Готово» 2, критерий 1:
method-contract.json в корне ядра, methodContract: 3 (решение 2; решение 6:
контракт 2→3, вход цепочки меняется); файл несёт только контракт
invariant: docs/decisions/ontoship-core.md#границы — эталон контракта —
файл ядра; проверка эталона умеет падать
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFERENCE = REPO / "method-contract.json"

# Spec decision 6: methodContract 2→3 — the chain entry changes (the
# reference file replaces the skill literal), the old team with the new
# core must signal mismatch. Independent expectation: the spec, not code.
EXPECTED_CONTRACT = 3


def _reference_errors(path: Path) -> list[str]:
    """Every violated reference-file rule; empty means the file is sound."""
    if not path.is_file():
        return ["method-contract.json is missing from the core root"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"method-contract.json is not valid JSON: {error}"]
    if not isinstance(value, dict):
        return ["method-contract.json must be a JSON object"]
    if set(value) != {"methodContract"}:
        return ["method-contract.json carries only the contract key, "
                f"got {sorted(value)}"]
    contract = value["methodContract"]
    if isinstance(contract, bool) or not isinstance(contract, int) or contract < 1:
        return ["methodContract must be an integer >= 1"]
    if contract != EXPECTED_CONTRACT:
        return [f"methodContract is {contract}, the spec expects {EXPECTED_CONTRACT}"]
    return []


def test_reference_file_carries_contract_3() -> None:
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 2,
    критерий 1: эталон в корне ядра несёт methodContract: 3 и только его."""
    assert _reference_errors(REFERENCE) == []


def test_reference_check_can_fail(tmp_path: Path) -> None:
    """invariant: docs/decisions/ontoship-core.md#границы — the reference
    check reddens on a missing file, broken JSON, a foreign key, a wrong
    version and a non-integer; probes run on seeded files."""
    assert _reference_errors(REFERENCE) == []

    missing = tmp_path / "absent.json"
    assert any("missing" in error for error in _reference_errors(missing))

    cases = (
        ("{broken", "not valid JSON"),
        ("[]", "JSON object"),
        ('{"methodContract": 3, "version": "0.7.0"}', "only the contract key"),
        ('{"methodContract": 2}', "spec expects 3"),
        ('{"methodContract": "3"}', "integer >= 1"),
        ('{"methodContract": true}', "integer >= 1"),
        ('{"methodContract": 0}', "integer >= 1"),
        ('{}', "only the contract key"),
    )
    for text, needle in cases:
        seeded = tmp_path / "reference.json"
        seeded.write_text(text, encoding="utf-8")
        errors = _reference_errors(seeded)
        assert any(needle in error for error in errors), (text, errors)
