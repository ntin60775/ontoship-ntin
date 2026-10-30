"""Guard for the canon's quality rule across its three carriers.

The three legal test goals live in the canon (docs/decisions/ontoship-core.md),
the testing skill (skills/testing/SKILL.md) and the reference page
(docs/reference/testing.md). The skill re-tells the rule on purpose — the
bundle installs into foreign projects without docs/ — so the retelling is
allowed, but the anchor wordings must stay identical in every carrier: a
rephrase in one file without the others is a silent divergence.

invariant: docs/decisions/ontoship-core.md#одно правило качества — якорные
формулировки правила трёх классов теста совпадают в каноне, скилле testing
и справочнике testing.md
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
    """Collapse wrapping, spacing and markdown emphasis: phrasing is compared."""
    return re.sub(r"\s+", " ", text.replace("*", "")).lower()


@pytest.mark.parametrize("carrier", CARRIERS, ids=lambda p: p.name)
def test_carrier_exists(carrier: Path) -> None:
    assert carrier.is_file(), f"carrier missing: {carrier.relative_to(REPO)}"


@pytest.mark.parametrize("anchor", ANCHORS, ids=lambda a: a[:24])
def test_anchor_in_every_carrier(anchor: str) -> None:
    missing = [
        f"{carrier.relative_to(REPO)}" for carrier in CARRIERS
        if anchor not in _flat(carrier.read_text(encoding="utf-8"))
    ]
    assert not missing, (
        f"anchor «{anchor}» missing from: {', '.join(missing)} — "
        "reword one carrier without the others; edit all three or none"
    )
