"""Guard for the canon's quality rule across its full carriers.

The three legal test goals live in full in the canon (docs/decisions/
ontoship-core.md), the testing skill (skills/testing/SKILL.md) and the
reference page (docs/reference/testing.md). The skill re-tells the rule on
purpose — the bundle installs into foreign projects without docs/ — so the
retelling is allowed, but the anchor wordings must stay identical in every
full carrier: a rephrase in one file without the others is a silent
divergence. Short mentions elsewhere (skills/ship, AGENTS.md,
review-roles.md, .agents/redpolitika.md) are digests and are covered by
review, not by anchors.

invariant: docs/decisions/ontoship-core.md#одно правило качества — якорные
формулировки правила трёх классов теста и его планки совпадают в каноне,
скилле testing и справочнике testing.md
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CARRIERS = (
    REPO / "docs/decisions/ontoship-core.md",
    REPO / "skills/testing/SKILL.md",
    REPO / "docs/reference/testing.md",
)
ANCHORS = (
    "ровно три законные цели",
    "тест без ни одной из трёх целей — сирота",
    "реальный путь сбоя",
    "red→green",
    "спеки, литерала или разобранного примера",
)


def _flat(text: str) -> str:
    """Collapse wrapping, spacing, emphasis and arrow spacing: phrasing is compared."""
    no_emphasis = text.replace("*", "")
    tight_arrow = re.sub(r"\s*→\s*", "→", no_emphasis)
    return re.sub(r"\s+", " ", tight_arrow).lower()


def _load(carrier: Path) -> str:
    assert carrier.is_file(), f"carrier missing: {carrier.relative_to(REPO)}"
    return _flat(carrier.read_text(encoding="utf-8"))


FLAT_CARRIERS = {carrier.name: _load(carrier) for carrier in CARRIERS}


@pytest.mark.parametrize("carrier", CARRIERS, ids=lambda p: p.name)
def test_carrier_exists(carrier: Path) -> None:
    assert carrier.is_file(), f"carrier missing: {carrier.relative_to(REPO)}"


@pytest.mark.parametrize("anchor", ANCHORS, ids=lambda a: a[:24])
def test_anchor_in_every_carrier(anchor: str) -> None:
    needle = _flat(anchor)
    missing = [name for name, text in FLAT_CARRIERS.items() if needle not in text]
    if len(missing) == len(CARRIERS):
        raise AssertionError(
            f"anchor «{anchor}» missing from every carrier — if the rule was "
            "deliberately reworded, update ANCHORS in this test to match"
        )
    assert not missing, (
        f"anchor «{anchor}» missing from: {', '.join(missing)} — "
        "reword one carrier without the others; edit all carriers or none"
    )
