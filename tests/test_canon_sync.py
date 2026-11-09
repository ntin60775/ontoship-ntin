"""Guard for method sections across KB docs and bundle carriers.

Named carrier sets share the anchor mechanics:

- ``quality`` — the quality rule in full: the canon, the testing skill, the
  KB page (docs/reference/testing.md) and the bundle carrier
  (skills/testing/references/quality-rule.md);
- ``panel-rules`` — the panel rules (a base-set role without a config section
  is not launched, the fallback for an unavailable model): the ship skill and
  its bundle carrier (skills/ship/references/review-panel.md);
- ``panel-run`` — the launch ways of the panel: the KB page
  (docs/reference/harnesses.md) and the bundle carrier;
- ``panel-intro`` — the panel's contract preamble and finding scale:
  the KB page (docs/reference/review-roles.md) and the bundle carrier;
- ``ontodoc-run`` — the onto-doc run ways: the KB page
  (docs/reference/harnesses.md) and the bundle carrier
  (skills/onto-doc/references/ontodoc-run.md);
- ``method-phases`` — the canon's three-phase section: the canon and the
  bundle carrier (skills/ship/references/method-phases.md);
- ``guard`` — the boundary rule (a bundle file is the primary source, the
  project overrides it): the canon and the four referencing skills.

Carriers retell the rules on purpose — bundles install into foreign projects
without docs/ — but the anchor wordings must stay identical in every carrier
of a set: a rephrase in one file without the others is a silent divergence.
Every KB page of a method section names its bundle carrier file with the
phrase «Носитель методной секции в бандле» (bundle-references, «Готово» 3).
Short mentions elsewhere (AGENTS.md, .agents/redpolitika.md) are digests and
are covered by review, not by anchors.

The can-fail probe guards the shared helpers (the comparator and the naming
predicate) on seeded files; the parametrized tests guard the real carriers.

invariant: docs/decisions/ontoship-core.md#одно правило качества — якорные
формулировки правила трёх классов теста и его планки совпадают в каноне,
скилле testing, справочнике testing.md и бандле quality-rule.md
spec: docs/plans/bundle-references.md#готово — якорные наборы методных
секций: правила панели, запуск панели, контракты панели, прогон онто-дока,
guard-фраза; KB-страница каждой секции называет файл бандла носителем
spec: docs/plans/canon-section-in-bundles.md#готово — набор method-phases:
канон ↔ секция бандла ship, четыре якоря тикета
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
    "тест-сироту не хранят",
    "вместе с прочитанным артефактом",
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

PANEL_RUN_CARRIERS = (
    REPO / "docs/reference/harnesses.md",
    REPO / "skills/ship/references/review-panel.md",
)
PANEL_RUN_ANCHORS = (
    "Модель субагента задаётся типом агента",
    "Фолбэк недоступной модели роли",
    "модель сессии с пометкой в отчёте",
)

PANEL_INTRO_CARRIERS = (
    REPO / "docs/reference/review-roles.md",
    REPO / "skills/ship/references/review-panel.md",
)
PANEL_INTRO_ANCHORS = (
    "Роли и их модели назначает",
    "Шкала приоритетов находок",
    "приоритет, место и зацепка",
)

ONTODOC_CARRIERS = (
    REPO / "docs/reference/harnesses.md",
    REPO / "skills/onto-doc/references/ontodoc-run.md",
)
ONTODOC_ANCHORS = (
    "прогон — сохранённый workflow",
    "Модель и уровень едут в `subagent_model`",
    "ListModels",
)

METHOD_CARRIERS = (
    REPO / "docs/decisions/ontoship-core.md",
    REPO / "skills/ship/references/method-phases.md",
)
METHOD_ANCHORS = (
    "Факты — работа агента; решения — работа оператора",
    "Никаких якорей `file:line` — они гниют",
    "Гейты ручные: план-гейт, вопрос нарезки и команда ship",
    "`to-tickets` **вызывает агент**",
    "вручную, то есть без автоматических цепочек",
    "один прогон ревью (панель специалистов параллельно, один отчёт)",
)

GUARD_CARRIERS = (
    REPO / "docs/decisions/ontoship-core.md",
    REPO / "skills/ship/SKILL.md",
    REPO / "skills/onto-doc/SKILL.md",
    REPO / "skills/testing/SKILL.md",
    REPO / "skills/to-tickets/SKILL.md",
)
GUARD_ANCHORS = (
    "файл бандла — первоисточник",
    "проект переопределяет его документом",
)

SETS = (
    ("quality", QUALITY_CARRIERS, QUALITY_ANCHORS),
    ("panel-rules", PANEL_CARRIERS, PANEL_ANCHORS),
    ("panel-run", PANEL_RUN_CARRIERS, PANEL_RUN_ANCHORS),
    ("panel-intro", PANEL_INTRO_CARRIERS, PANEL_INTRO_ANCHORS),
    ("ontodoc-run", ONTODOC_CARRIERS, ONTODOC_ANCHORS),
    ("method-phases", METHOD_CARRIERS, METHOD_ANCHORS),
    ("guard", GUARD_CARRIERS, GUARD_ANCHORS),
)

# The KB page of each method section names its bundle carrier file with the
# phrase (spec: docs/plans/bundle-references.md#готово — «Готово» 3).
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
NAMING_PHRASE = "Носитель методной секции в бандле"


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


ALL_CARRIERS = tuple(sorted({carrier for _name, carriers, _anchors in SETS
                             for carrier in carriers}, key=_carrier_name))

ANCHOR_CASES = tuple((name, anchor, carriers)
                     for name, carriers, anchors in SETS
                     for anchor in anchors)
ANCHOR_IDS = [f"{name}:{anchor[:20]}" for name, anchor, _ in ANCHOR_CASES]


def _missing_carriers(anchor: str, carriers: tuple[Path, ...]) -> list[str]:
    """Names of the carriers the anchor wording is absent from."""
    needle = _flat(anchor)
    return [_carrier_name(carrier) for carrier in carriers
            if needle not in _flat(carrier.read_text(encoding="utf-8"))]


def _page_names_carrier(page: Path, carrier: str) -> bool:
    """The KB page names the bundle carrier file with the naming phrase."""
    text = _flat(page.read_text(encoding="utf-8"))
    return NAMING_PHRASE.lower() in text and carrier in text


@pytest.mark.parametrize("carrier", ALL_CARRIERS,
                         ids=_carrier_name)
def test_carrier_exists(carrier: Path) -> None:
    assert carrier.is_file(), f"carrier missing: {_carrier_name(carrier)}"


@pytest.mark.parametrize("set_name,anchor,carriers", ANCHOR_CASES, ids=ANCHOR_IDS)
def test_anchor_in_every_carrier(set_name: str, anchor: str,
                                 carriers: tuple[Path, ...]) -> None:
    missing = _missing_carriers(anchor, carriers)
    if len(missing) == len(carriers):
        raise AssertionError(
            f"anchor «{anchor}» of the {set_name} set is missing from every "
            "carrier — if the rule was deliberately reworded, update the "
            "anchor tuples (QUALITY_ANCHORS / PANEL_ANCHORS / PANEL_RUN_"
            "ANCHORS / PANEL_INTRO_ANCHORS / ONTODOC_ANCHORS / METHOD_"
            "ANCHORS / GUARD_ANCHORS) "
            "in this test"
        )
    assert not missing, (
        f"anchor «{anchor}» of the {set_name} set missing from: "
        f"{', '.join(missing)} — reword one carrier without the others; "
        "edit all carriers or none"
    )


@pytest.mark.parametrize("page,carrier", KB_NAMED_CARRIERS,
                         ids=[f"{page.name}->{carrier.rsplit('/', 1)[-1]}"
                              for page, carrier in KB_NAMED_CARRIERS])
def test_kb_page_names_its_bundle_carrier(page: Path, carrier: str) -> None:
    """spec: docs/plans/bundle-references.md#готово — the KB page of a method
    section names its bundle carrier file with the naming phrase."""
    assert _page_names_carrier(page, carrier), (
        f"{_carrier_name(page)} must name the bundle carrier {carrier} "
        f"with the phrase «{NAMING_PHRASE}»"
    )


def test_parity_mutations_can_fail(tmp_path: Path) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the shared helpers redden: the comparator names one carrier without the
    others (the KB page without the bundle, the bundle without the KB page,
    both directions of the panel pair), and the naming predicate drops a page
    that loses the mention or the phrase. Probes run on seeded carrier files,
    so a real divergence reddens only the parity tests, not this probe."""
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

    # The ship skill reworded without its bundle carrier (panel-rules pair).
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

    # The bundle carrier reworded without the ship skill (panel-rules pair):
    # the фолбэк anchor arrives wrapped, the flat comparator still holds it
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

    # The method-phases pair: an anchor dropped from the bundle section
    # alone reddens while the canon still holds it.
    canon = seed("canon-phases.md",
                 "Гейты ручные: план-гейт, вопрос нарезки и команда ship.")
    section = seed("method-phases.md",
                   "Гейты ручные: план-гейт, вопрос нарезки и команда ship.")
    mutated_text = section.read_text("utf-8").replace(
        "команда ship", "команда merge")
    assert mutated_text != section.read_text("utf-8"), \
        "the mutation must remove the anchor"
    section.write_text(mutated_text, "utf-8")
    missing = _missing_carriers(
        "Гейты ручные: план-гейт, вопрос нарезки и команда ship",
        (canon, section))
    assert missing == [section.as_posix()], missing

    # The naming predicate: a page that drops the carrier mention or the
    # phrase stops naming its bundle carrier — the same predicate the
    # parametrized test asserts.
    page = seed("page.md",
                f"{NAMING_PHRASE}: skills/testing/references/quality-rule.md.")
    assert _page_names_carrier(page, "skills/testing/references/quality-rule.md")
    page.write_text(page.read_text("utf-8").replace(
        "skills/testing/references/quality-rule.md", ""), "utf-8")
    assert not _page_names_carrier(
        page, "skills/testing/references/quality-rule.md")
    page = seed("page2.md", "skills/testing/references/quality-rule.md.")
    assert not _page_names_carrier(
        page, "skills/testing/references/quality-rule.md")
