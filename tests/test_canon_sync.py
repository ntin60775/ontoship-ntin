"""Guard for method sections across KB docs and bundle carriers.

Two carrier sets share the anchor mechanics. The quality rule lives in full
in the canon (docs/decisions/ontoship-core.md), the testing skill
(skills/testing/SKILL.md), the KB page (docs/reference/testing.md) and its
bundle carrier (skills/testing/references/quality-rule.md). The panel rules
live in the ship skill (skills/ship/SKILL.md) and its bundle carrier
(skills/ship/references/review-panel.md). Carriers retell the rules on
purpose — bundles install into foreign projects without docs/ — but the
anchor wordings must stay identical in every carrier of a set: a rephrase
in one file without the others is a silent divergence. Every KB page of a
method section names its bundle carrier file (bundle-references, «Готово» 3).
Short mentions elsewhere (AGENTS.md, .agents/redpolitika.md, to-tickets)
are digests and are covered by review, not by anchors.

invariant: docs/decisions/ontoship-core.md#одно правило качества — якорные
формулировки правила трёх классов теста и его планки совпадают в каноне,
скилле testing, справочнике testing.md и бандле quality-rule.md; якорные
формулировки правил панели совпадают в скилле ship и его бандле
review-panel.md
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

QUALITY_CARRIERS = (
    REPO / "docs/decisions/ontoship-core.md",
    REPO / "skills/testing/SKILL.md",
    REPO / "docs/reference/testing.md",
    REPO / "skills/testing/references/quality-rule.md",
)
QUALITY_ANCHORS = (
    "ровно три законные цели",
    "тест без ни одной из трёх целей — сирота",
    "реальный путь сбоя",
    "red→green",
    "спеки, литерала или разобранного примера",
)

PANEL_CARRIERS = (
    REPO / "skills/ship/SKILL.md",
    REPO / "skills/ship/references/review-panel.md",
)
PANEL_ANCHORS = (
    "без секции в конфиге не запускается",
    "молчаливая подмена не делается",
    "модель сессии с пометкой в отчёте",
    "«ревью провёл исполнитель» законным исходом не является",
)

SETS = (
    ("quality", QUALITY_CARRIERS, QUALITY_ANCHORS),
    ("panel", PANEL_CARRIERS, PANEL_ANCHORS),
)

# The KB page of each method section names its bundle carrier file
# (spec: docs/plans/bundle-references.md#готово — «Готово» 3).
KB_NAMED_CARRIERS = (
    (REPO / "docs/reference/testing.md",
     "skills/testing/references/quality-rule.md"),
    (REPO / "docs/reference/harnesses.md",
     "skills/ship/references/review-panel.md"),
    (REPO / "docs/reference/harnesses.md",
     "skills/onto-doc/references/ontodoc-run.md"),
    (REPO / "docs/reference/review-roles.md",
     "skills/ship/references/review-panel.md"),
)

ALL_CARRIERS = tuple(carrier for _name, carriers, _anchors in SETS
                     for carrier in carriers)

ANCHOR_CASES = tuple((anchor, carriers)
                     for _name, carriers, anchors in SETS
                     for anchor in anchors)
ANCHOR_IDS = [anchor[:24] for anchor, _carriers in ANCHOR_CASES]


def _flat(text: str) -> str:
    """Collapse wrapping, spacing, emphasis and arrow spacing: phrasing is compared."""
    no_emphasis = text.replace("*", "")
    tight_arrow = re.sub(r"\s*→\s*", "→", no_emphasis)
    return re.sub(r"\s+", " ", tight_arrow).lower()


def _carrier_name(carrier: Path) -> str:
    try:
        return carrier.relative_to(REPO).as_posix()
    except ValueError:
        return carrier.as_posix()


def _missing_carriers(anchor: str, carriers: tuple[Path, ...]) -> list[str]:
    """Names of the carriers the anchor wording is absent from."""
    needle = _flat(anchor)
    return [_carrier_name(carrier) for carrier in carriers
            if needle not in _flat(carrier.read_text(encoding="utf-8"))]


@pytest.mark.parametrize("carrier", ALL_CARRIERS,
                         ids=_carrier_name)
def test_carrier_exists(carrier: Path) -> None:
    assert carrier.is_file(), f"carrier missing: {_carrier_name(carrier)}"


@pytest.mark.parametrize("anchor,carriers", ANCHOR_CASES, ids=ANCHOR_IDS)
def test_anchor_in_every_carrier(anchor: str,
                                 carriers: tuple[Path, ...]) -> None:
    missing = _missing_carriers(anchor, carriers)
    if len(missing) == len(carriers):
        raise AssertionError(
            f"anchor «{anchor}» missing from every carrier — if the rule was "
            "deliberately reworded, update ANCHORS in this test to match"
        )
    assert not missing, (
        f"anchor «{anchor}» missing from: {', '.join(missing)} — "
        "reword one carrier without the others; edit all carriers or none"
    )


@pytest.mark.parametrize("page,carrier", KB_NAMED_CARRIERS,
                         ids=[f"{page.name}->{carrier.rsplit('/', 1)[-1]}"
                              for page, carrier in KB_NAMED_CARRIERS])
def test_kb_page_names_its_bundle_carrier(page: Path, carrier: str) -> None:
    """spec: docs/plans/bundle-references.md#готово — the KB page of a method
    section names its bundle carrier file."""
    assert carrier in page.read_text(encoding="utf-8"), (
        f"{_carrier_name(page)} must name the bundle carrier {carrier}"
    )


def test_parity_mutations_can_fail(tmp_path: Path) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the comparator reddens one carrier without the others: the KB page
    without the bundle, the bundle without the KB page, and both directions
    of the panel pair; a dropped carrier mention reddens the naming check.
    Probes run on seeded carrier files, so a real divergence reddens only
    the parity tests, not this probe."""
    def seed(name: str, text: str) -> Path:
        path = tmp_path / name
        path.write_text(text, "utf-8")
        return path

    plank = "Планка target-теста:\n**Red→green.**\nТест падает на дереве с багом."

    # The KB page reworded without the bundle carrier (quality set). Both
    # spellings of the anchor — «**Red→green.**» in the планка and the
    # lowercase one in the метрики — must leave the text.
    kb = seed("kb.md", plank + "\n\nМетрики считают red→green тесты.")
    mutated_text = kb.read_text("utf-8").replace("Red→green", "цветовая проба") \
                                        .replace("red→green", "цветовая проба")
    assert mutated_text != kb.read_text("utf-8"), \
        "the mutation must remove the anchor"
    kb.write_text(mutated_text, "utf-8")
    bundle = seed("bundle.md", plank)
    missing = _missing_carriers("red→green", (kb, bundle))
    assert missing == [kb.as_posix()], missing

    # The bundle carrier reworded without the KB page (fresh pair: the KB
    # page above already lost the anchor to its own probe).
    kb = seed("kb2.md", plank)
    bundle = seed("bundle2.md", plank)
    mutated_text = bundle.read_text("utf-8").replace("Red→green",
                                                     "цветовая проба")
    assert mutated_text != bundle.read_text("utf-8"), \
        "the mutation must remove the anchor"
    bundle.write_text(mutated_text, "utf-8")
    missing = _missing_carriers("red→green", (kb, bundle))
    assert missing == [bundle.as_posix()], missing

    # The ship skill reworded without its bundle carrier (panel pair).
    panel_rule = ("Роль без секции в конфиге не запускается —\nмолчаливая "
                  "подмена не делается.")
    ship = seed("ship.md", panel_rule)
    panel = seed("panel.md", panel_rule)
    mutated_text = ship.read_text("utf-8").replace(
        "молчаливая подмена не делается", "молчаливая подмена исключена")
    assert mutated_text != ship.read_text("utf-8"), \
        "the mutation must remove the anchor"
    ship.write_text(mutated_text, "utf-8")
    missing = _missing_carriers("молчаливая подмена не делается",
                                (ship, panel))
    assert missing == [ship.as_posix()], missing

    # The bundle carrier reworded without the ship skill (panel pair): the
    # фолбэк anchor arrives wrapped, the flat comparator still holds it
    # until the exact wrapped fragment is reworded.
    ship = seed("ship2.md",
                "Недоступная модель роли — фолбэк на модель\nсессии "
                "с пометкой в отчёте, провал — стоп.")
    panel = seed("panel2.md",
                 "Фолбэк недоступной модели роли — модель\nсессии с пометкой "
                 "в отчёте; провал — стоп прохода.")
    mutated_text = panel.read_text("utf-8").replace(
        "модель\nсессии с пометкой в отчёте",
        "модель\nпрогона с пометкой в отчёте")
    assert mutated_text != panel.read_text("utf-8"), \
        "the mutation must remove the anchor"
    panel.write_text(mutated_text, "utf-8")
    missing = _missing_carriers("модель сессии с пометкой в отчёте",
                                (ship, panel))
    assert missing == [panel.as_posix()], missing

    # A KB page that drops the carrier mention reddens the naming check.
    page = seed("page.md",
                "Носитель методной секции в бандле: "
                "skills/testing/references/quality-rule.md.")
    page.write_text(page.read_text("utf-8").replace(
        "skills/testing/references/quality-rule.md", ""), "utf-8")
    assert "skills/testing/references/quality-rule.md" \
        not in page.read_text("utf-8")
