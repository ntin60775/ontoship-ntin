"""Anchor guard for the sa08 ticket text after the unfreeze rewrite.

core-team-boundaries ticket 07: ticket 08 of standards-autoship is rewritten
as a fast smoke pack test of the core (install a pack, init with the pack,
ship runs the pack gates, report). The guard reads the ticket TEXT only:
mandatory sections, the four smoke steps, named artifacts, the «what
reddens» line, the unfreeze record, the fate of the spec's «Готово» 12/14
and the out-of-unit execution line. Execution of sa08 and the red probe of
its criteria are a separate run outside the unit — this guard never runs
them; the can-fail probe mutates the text in memory and asserts the named
error, so a dropped check in this file reddens the probe too. Closed
checkboxes ([x]) are the executed-ticket idiom and stay green.

spec: docs/plans/core-team-boundaries.md#готово — «Готово» 7: текст sa08
несёт обязательные разделы, четыре шага дымового pack-теста, названные
артефакты, строку «что краснит», запись разморозки, судьбу «Готово» 12/14
спеки standards-autoship и строку исполнения вне юнита
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TICKET = REPO / "tickets" / "standards-autoship" / "08-live-proof.md"

# Mandatory sections of the standards-autoship ticket form (bold labels at
# line start, the unit's ticket idiom).
SECTION_LABELS = (
    "**Спека:**",
    "**Блокируется:**",
    "**Что построить:**",
    "**Демо-путь:**",
    "**Критерии приёмки**",
)

# The smoke flow of decision 7, verbatim chain; whitespace-normalized search
# survives the 80-column prose wrap.
SMOKE_FLOW = "установка пака → init с паком → ship исполняет гейты пака → отчёт"

# The four numbered steps of «Что построить», each anchored on its own.
STEP_ANCHORS = (
    "1. Установка пака",
    "2. Init с паком",
    "3. Ship исполняет гейты пака",
    "4. Отчёт",
)

# Named artifacts of the four steps: the installer pack channel, the gate
# runner with the manifest exit contract, the role registry.
ARTIFACT_PHRASES = (
    "install.sh --pack",
    "install.sh --check",
    "run_gates.py",
    "expect_exit",
    ".agents/config.toml",
)

# The unfreeze record: the decision that lifted the freeze, and the lifted
# freeze itself named with its date.
UNFREEZE_PHRASES = (
    "**Разморожен:**",
    "решение 7 спеки",
    "core-team-boundaries",
    "2026-11-16",
    "Заморозка ask 2026-11-13",
    "снята",
)

# The fate of the orphaned spec items (triage G9): displaced by the team
# probe 07, or a named gap.
FATE_PHRASES = (
    "«Готово» 12",
    "«Готово» 14",
    "вытеснено пробой 07 team",
    "team-profiles",
    "названный пробел",
)

# Execution and the red probe of the criteria are the input of the sa08 run,
# outside the unit (spec «Рамки»).
OUT_OF_UNIT_PHRASES = (
    "Исполнение и красная проба критериев — отдельный прогон вне юнита",
    "вход прогона sa08",
)

# Retired wordings of the frozen full-flow ticket: the freeze label and the
# old title must not survive the rewrite.
RETIRED_PHRASES = (
    "**Заморожен:**",
    "Живая проба полного потока и закрывающий набор",
)

RED_LINE_RE = re.compile(r"^\*\*Что краснит:\*\*[ \t]+\S", re.MULTILINE)
# Open and closed checkboxes alike: the sa08 run marks its criteria [x].
# Uppercase [X] is not the ticket idiom: the criterion count reddens it.
CRITERION_RE = re.compile(r"^- \[[ x]\]", re.MULTILINE)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _text_errors(text: str) -> list[str]:
    """Name every missing anchor of the rewritten sa08 text."""
    errors: list[str] = []
    norm = _norm(text)

    first_line = text.splitlines()[0] if text.splitlines() else ""
    if not (first_line.startswith("# 08:") and "pack-тест" in first_line):
        errors.append("the title must name the smoke pack test")

    for label in SECTION_LABELS:
        if not re.search(r"^" + re.escape(label), text, re.MULTILINE):
            errors.append(f"missing section label {label!r}")

    if SMOKE_FLOW not in norm:
        errors.append(f"missing smoke flow {SMOKE_FLOW!r}")

    for step in STEP_ANCHORS:
        if not re.search(r"^" + re.escape(step), text, re.MULTILINE):
            errors.append(f"missing smoke step {step!r}")

    for phrase in ARTIFACT_PHRASES:
        if phrase not in norm:
            errors.append(f"missing named artifact {phrase!r}")

    if not RED_LINE_RE.search(text):
        errors.append("missing the «Что краснит» line with content")

    for phrase in UNFREEZE_PHRASES:
        if phrase not in norm:
            errors.append(f"missing unfreeze record phrase {phrase!r}")

    for phrase in FATE_PHRASES:
        if phrase not in norm:
            errors.append(f"missing fate phrase {phrase!r}")

    for phrase in OUT_OF_UNIT_PHRASES:
        if phrase not in norm:
            errors.append(f"missing out-of-unit phrase {phrase!r}")

    for phrase in RETIRED_PHRASES:
        if phrase in norm:
            errors.append(f"retired wording survived: {phrase!r}")

    tail = text.split("**Критерии приёмки**", 1)
    if len(tail) != 2:
        errors.append("missing the criteria section body")
    else:
        items = CRITERION_RE.split(tail[1])[1:]
        if len(items) < 4:
            errors.append("the four smoke steps need four criteria")
        for index, item in enumerate(items, 1):
            if "артефакт" not in item or "ожидание" not in item:
                errors.append(
                    f"criterion {index} must name an artifact and an expectation")

    return errors


def _remove_phrase(text: str, phrase: str) -> str:
    # Whitespace between words matches the 80-column prose wrap too.
    pattern = r"\s+".join(re.escape(word) for word in phrase.split())
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def test_sa08_text_carries_the_smoke_contract():
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 7: текст
    тикета 08 несёт обязательные разделы, четыре шага дымового pack-теста,
    названные артефакты, строку «что краснит», запись разморозки, судьбу
    «Готово» 12/14 и строку исполнения вне юнита; снятые формулировки
    замороженного тикета не переживают переписывание."""
    assert _text_errors(TICKET.read_text("utf-8")) == []


def test_sa08_text_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the sa08 text check can fail: remove-мутация каждого якоря (разделы,
    шаги, артефакты, «что краснит», разморозка, судьба 12/14, вне юнита)
    краснит именованной ошибкой; удаление одного критерия, возврат
    заморозки и старого заголовка краснят; канарейка закрытых чекбоксов
    [x] — guard обоих состояний: до исполнения закрывает открытые,
    после исполнения (все [x]) открывает один критерий и остаётся
    зелёной; заглавный [X] — не идиома тикета, краснит счёт критериев
    (мутационная проба)."""
    text = TICKET.read_text("utf-8")
    assert _text_errors(text) == []

    groups = (
        (SECTION_LABELS, "missing section label"),
        ((SMOKE_FLOW,), "missing smoke flow"),
        (STEP_ANCHORS, "missing smoke step"),
        (ARTIFACT_PHRASES, "missing named artifact"),
        (UNFREEZE_PHRASES, "missing unfreeze record phrase"),
        (FATE_PHRASES, "missing fate phrase"),
        (OUT_OF_UNIT_PHRASES, "missing out-of-unit phrase"),
        (("артефакт", "ожидание"), "must name an artifact and an expectation"),
    )
    for phrases, expected in groups:
        for phrase in phrases:
            mutated = _remove_phrase(text, phrase)
            assert mutated != text, f"the needle {phrase!r} matched nothing"
            assert any(expected in error for error in _text_errors(mutated)), \
                f"removing {phrase!r} must redden with {expected!r}"

    no_red_line = RED_LINE_RE.sub("", text)
    assert no_red_line != text
    assert any("«Что краснит»" in error for error in _text_errors(no_red_line))

    bullets = list(CRITERION_RE.finditer(text))
    assert len(bullets) >= 4
    no_first = text[:bullets[0].start()] + text[bullets[1].start():]
    assert any("four smoke steps" in error for error in _text_errors(no_first)), \
        "removing one criterion must redden the criterion count"

    refrozen = text.replace("**Разморожен:**", "**Заморожен:**", 1)
    assert refrozen != text
    assert any("retired wording survived" in error
               for error in _text_errors(refrozen)), \
        "restoring the freeze label must redden the retired-wording check"

    old_title = text.replace(text.splitlines()[0],
                             "# 08: Живая проба полного потока и закрывающий набор",
                             1)
    assert old_title != text
    assert any("retired wording survived" in error
               for error in _text_errors(old_title)), \
        "restoring the old title must redden the retired-wording check"

    # Canary of the executed ticket: [x] criteria stay green. Before
    # execution, close the open criteria; after execution (all [x]),
    # reopening one criterion stays green too — a guard of both states,
    # not a mutation probe (the remove-mutations above are the probes).
    closed = text.replace("- [ ]", "- [x]")
    if closed != text:
        assert _text_errors(closed) == [], \
            "the executed ticket marks its criteria [x] and must stay green"
    else:
        opened = text.replace("- [x]", "- [ ]", 1)
        assert opened != text, "the executed ticket must carry [x] criteria"
        assert _text_errors(opened) == [], \
            "reopening one criterion of the executed ticket must stay green"
        upper = text.replace("- [x]", "- [X]")
        assert upper != text
        assert any("four smoke steps" in error
                   for error in _text_errors(upper)), \
            "uppercase [X] is not the ticket idiom and must redden the count"
