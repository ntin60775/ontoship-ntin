"""Contract for the review-roles reference and the harness review rows
(review-config ticket 04).

``docs/reference/review-roles.md`` must carry the base-set role
contracts — ``reviewer-spec``, ``reviewer-tests``, ``reviewer-code``,
``reviewer-kb`` — each with a scope and a checklist, plus the pack rules:
packs carry standards, role checklists and gate configs as data, role names
follow ``reviewer-<kontur>-<aspect>``, init detects pack roles, gates stay
with the core and the core executes the gate configs.
``docs/reference/harnesses.md`` must describe how each harness organizes
the review panel: the zcode way named retired (the rail left the project),
the working DSH way (``subagent`` with ``provider``, ``model`` and
``reasoning_effort``, a live ``list_subagent_models``, an unavailable route
stopping the pass) and Qoder named a gap inside its own subsection of the
review section, never implemented silently. The reference is linked from
the folder index. The ``reviewer-tests`` checklist additionally carries the
two evidence items: every acceptance criterion must show what and where to
look
(command output, log line, file, live probe) plus a spec-sourced expectation
— «тест прошёл» with no place to look is a finding — and the ticket must
dissect every expectation/fact discrepancy or carry the line «не было»,
linking the «Артефакт доказательства» section of docs/reference/testing.md
(evidence-verification ticket 02).

spec: docs/plans/review-config.md#готово — справочник ролей и регламент паков
spec: docs/plans/standards-autoship.md#решения план-гейта — 3: регламент
паков — стандарты, чек-листы и конфиги гейтов как данные, гейты у ядра
spec: docs/plans/dsh-adaptation.md#готово — DSH первый класс в матрице:
рабочий способ панели и онто-дока, Qoder — названный пробел
spec: docs/plans/review-config.md#решения план-гейта — 9, 11, 12
spec: docs/plans/evidence-verification.md#готово — reviewer-tests проверяет
артефакт: оба пункта чек-листа, «тест прошёл» без места осмотра — находка
invariant: docs/decisions/ontoship-core.md#одно правило качества — the
contract check can fail
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFERENCE = REPO / "docs" / "reference" / "review-roles.md"
HARNESSES = REPO / "docs" / "reference" / "harnesses.md"
INDEX = REPO / "docs" / "reference" / "README.md"
ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb")
# The role-count snapshot guard of the reference layer — the same class as
# COUNTED_ROLE in tests/test_skill_init.py; a numeral before «рол…» (optionally
# «ревью-рол…») must not return into the reference or its index. Blind spots
# match that guard: a count after the noun and ordinals before the noun.
COUNTED_ROLE = re.compile(
    r"(?<![а-яёa-z\d])"
    r"(?:\d+"
    r"|один|одна|одно|одни|одной|одному"
    r"|дв[ае]|двух|двум|двумя"
    r"|три|тр[ие]|трём|трем|тр[её]х|тремя"
    r"|четыре|четыр[её]х|четырём|четырем|четырьмя"
    r"|пять|пяти|пятью"
    r"|шесть|шести|шестью"
    r"|семь|семи|семью"
    r"|восемь|восьми|восемью"
    r"|девять|девяти|девятью"
    r"|десять|десяти|десятью)"
    r"\s+(?:ревью-)?рол",
    re.IGNORECASE,
)
INDEPENDENCE_PHRASES = ("вердикт", "приоритет", "зацепк", "артефакты",
                        "не ход исполнения")
# standards-autoship 07 («Готово» 13, решение 3): the pack carries standards,
# role checklists and gate configs as data; the retired «только промпты и
# чек-листы» rule must not return.
PACK_RULES = (
    "пак",
    "стандарты, чек-листы ролей и конфиги механических гейтов как данные",
    "reviewer-<kontur>-<aspect>",
    "без кода",
    "гейт",
    "init",
    "конфиги гейтов исполняет ядро в окружении проекта",
)
RETIRED_PACK_RULE = "только промпты и чек-листы"
# standards-autoship 05 («Готово» 3, 9; решения 8, 15): the KB panel carrier
# names the core+pack assembly, the route stop and the standards priority of
# the reviewer-code input.
ROUTE_STOP = "недоступная пара — остановка прохода и вопрос оператору"
PANEL_ASSEMBLY = (
    "панель собирается из ролей ядра и ролей паков",
    ROUTE_STOP,
    "канон > стандарты проекта > пак команды > пак стека > базовый документ",
)
# review-output 01 («Готово» 1): the role's input is its whole scope, its
# output is dry structured findings without echoing the input; an empty scope
# is a named skip and the role does not start. The same five anchors live in
# the panel preamble of both carriers; the four role sections carry the scope
# anchor only.
PANEL_OUTPUT_ANCHORS = (
    "область роли целиком",
    "сухие структурированные находки",
    "без дословного эха",
    "зацепка ≤10 слов",
    "пустая область",
    # the finding line shape and the output template: priority, place, dash,
    # lead, verdict line.
    "одна строка: `p2 <файл:строка> — зацепка",
    "<принять | принять с находками | вернуть>",
)
PANEL_OUTPUT_CARRIERS = (
    REFERENCE,
    REPO / "skills" / "ship" / "references" / "review-panel.md",
)
# The harness row promises the dry metrics in the panel contract, so the
# contract states them: an echoed quote is a verbatim input substring of five
# words or more, the output length is counted in words.
PANEL_METRIC_ANCHORS = (
    "цитата входа — дословная подстрока входа ≥5 слов",
    "длина вывода считается в словах",
)
# review-output 01: the dated fallback decisions are read with the addendum
# «снято решением 2026-11-25»; the live text of both plans carries the route
# stop, and no fallback wording survives there or in the live carriers.
ROUTE_STOP_NORM = "подмены маршрута нет, стоп и вопрос оператору"
FALLBACK_PHRASES = (
    "заменяется моделью сессии",
    "идёт на модели сессии",
    "на фолбэке",
    "фолбэк называется в отчёте",
)
PLAN_CARRIERS = (
    REPO / "docs" / "plans" / "review-config.md",
    REPO / "docs" / "plans" / "standards-autoship.md",
)
LIVE_PANEL_CARRIERS = (
    REPO / "skills" / "ship" / "SKILL.md",
    REPO / "skills" / "ship" / "references" / "review-panel.md",
    HARNESSES,
)
# The model-distinctness rule is retired: a role route may match the session
# model. Any return of the old wording reddens.
RETIRED_MODEL_RULE = (
    "независимость по умолчанию",
    "отличной от сессионной",
    "модель сессии",
    "модели сессии",
    "не-сессионную модель",
)
# The ZCode purge (operator decision): the review section keeps a zcode
# subsection, and it is named retired — with no surviving procedure tokens
# (generator, workflow transport, host tool, session-model marker).
ZCODE_RETIRE_NEEDLES = ("снят", "выведен")
ZCODE_RETIRE_FORBIDDEN = ("gen_agents", "subagent_model`", "[current]",
                          "listmodels", "перезапуск")
# DSH first class (dsh-adaptation ticket 05): the review row names the native
# panel way instead of a gap; Qoder keeps its named gap.
DSH_WAY = (
    "subagent",
    "provider",
    "reasoning_effort",
    "list_subagent_models",
)
RETIRED_DSH_PHRASES = (
    "dsh — пробел окружения",
    "dsh и qoder — вне плана",
    "dsh вне плана",
)
GENERATOR_DSH_RULE = "генератора определений в проекте нет"
GAP_CARRIERS = (
    HARNESSES,
    REPO / "skills" / "ship" / "references" / "review-panel.md",
    REPO / "skills" / "onto-doc" / "references" / "ontodoc-run.md",
)
REVIEWER_TESTS_EVIDENCE = (
    "что и где смотреть",
    "вывод команды, строка лога, файл, живая проба",
    "ожидание из спеки",
    "тест прошёл",
    "без места осмотра — находка",
    "разбор каждого расхождения",
    "не было",
    "docs/reference/testing.md",
)


def _frontmatter(text: str) -> dict[str, str]:
    """Flat single-line keys of the frontmatter; nested lists are skipped."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            break
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def _h3_sections(text: str) -> dict[str, str]:
    """Map each ``### heading`` to its body, up to the next heading of any level."""
    sections: dict[str, str] = {}
    current: str | None = None
    chunks: list[str] = []
    for line in text.splitlines():
        if line.startswith("### "):
            if current is not None:
                sections[current] = "\n".join(chunks)
            current = line[4:].strip()
            chunks = []
        elif line.startswith("#"):
            # h1/h2/h4 end the section and never start one
            if current is not None:
                sections[current] = "\n".join(chunks)
                current = None
        elif current is not None:
            chunks.append(line)
    if current is not None:
        sections[current] = "\n".join(chunks)
    return sections


def _h2_section(text: str, heading: str) -> str:
    """Body of one ``## heading`` section, up to the next ``## ``."""
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def _panel_intro(text: str) -> str:
    """Panel preamble of a carrier: everything before the first ``## `` plus
    the body of ``## Панель`` when the carrier has that section."""
    first = re.search(r"(?m)^## ", text)
    head = text[: first.start()] if first else text
    return _normalized_lower(head + "\n" + _h2_section(text, "Панель"))


def _review_section(harnesses: str) -> list[str] | None:
    """Raw lines of the review section: the first ``## `` heading naming
    ревью, up to the next ``## `` heading. Raw lines, no whitespace
    collapsing — the per-harness checks below need real line structure."""
    lines = harnesses.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.startswith("## ") and "ревью" in line.lower()), None)
    if start is None:
        return None
    section: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def _h3_blocks(section: list[str]) -> dict[str, str]:
    """Map each lowered ``###`` heading inside the section to its normalized
    heading-plus-body — the whole block, so a gap named anywhere in it counts."""
    blocks: dict[str, str] = {}
    heading: str | None = None
    chunks: list[str] = []
    for line in section:
        if line.startswith("### "):
            if heading is not None:
                blocks[heading] = _normalized_lower(" ".join(chunks))
            heading = line[4:].strip().lower()
            chunks = [line[4:]]
        elif heading is not None:
            chunks.append(line)
    if heading is not None:
        blocks[heading] = _normalized_lower(" ".join(chunks))
    return blocks


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _reviewer_tests_evidence_errors(text: str) -> list[str]:
    """Violated evidence items of the reviewer-tests checklist; empty is sound.

    The roles loop in ``_reference_errors`` owns the missing-section and
    unnamed-checklist errors, so this helper stays silent on both instead of
    duplicating them. The phrases are checked inside the checklist part of
    the section only: prose above it must not keep the contract green when
    the checklist loses an item.
    """
    sections = _h3_sections(text)
    matching = [heading for heading in sections
                if "reviewer-tests" in heading.lower()]
    if not matching:
        return []
    body = _normalized_lower(sections[matching[0]])
    marker = body.find("чек-лист")
    if marker < 0:
        return []
    tail = body[marker:]
    return [f"reviewer-tests checklist lost {phrase!r}"
            for phrase in REVIEWER_TESTS_EVIDENCE if phrase not in tail]


def _reference_errors(text: str) -> list[str]:
    """Every violated review-roles contract; empty means the reference is sound."""
    errors: list[str] = []
    fields = _frontmatter(text)
    if not fields:
        return ["frontmatter is missing"]
    if fields.get("node_type") != "reference":
        errors.append(f"frontmatter: node_type must be reference, got "
                      f"{fields.get('node_type')!r}")
    if fields.get("status") != "active":
        errors.append(f"frontmatter: status must be active, got "
                      f"{fields.get('status')!r}")
    if not fields.get("title"):
        errors.append("frontmatter: title is missing")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields.get("updated", "")):
        errors.append("frontmatter: updated must be a YYYY-MM-DD date")

    sections = _h3_sections(text)
    for role in ROLES:
        matching = [heading for heading in sections if role in heading.lower()]
        if not matching:
            errors.append(f"role {role!r} has no section")
            continue
        body = sections[matching[0]]
        lowered = _normalized_lower(body)
        marker = lowered.find("чек-лист")
        if marker < 0:
            errors.append(f"role {role!r}: checklist is not named")
            items = 0
        else:
            items = len(re.findall(r"(?m)^- ", body[marker:]))
        if items < 3:
            errors.append(f"role {role!r}: checklist has {items} items, need 3+")
        if "область" not in lowered:
            errors.append(f"role {role!r}: scope (область) is not named")
        elif "область роли целиком" not in lowered:
            errors.append(f"role {role!r}: the scope is not the whole role "
                          "area (область роли целиком)")

    lowered = _normalized_lower(text)
    for phrase in INDEPENDENCE_PHRASES:
        if phrase not in lowered:
            errors.append(f"missing required phrase {phrase!r}")
    for rule in PACK_RULES:
        if rule not in lowered:
            errors.append(f"pack rule {rule!r} is missing")
    if RETIRED_PACK_RULE in lowered:
        errors.append(f"retired pack rule {RETIRED_PACK_RULE!r} is back")
    for phrase in PANEL_ASSEMBLY:
        if phrase not in lowered:
            errors.append(f"panel assembly {phrase!r} is missing")
    for phrase in PANEL_OUTPUT_ANCHORS:
        if phrase not in lowered:
            errors.append(f"panel output contract {phrase!r} is missing")
    for phrase in RETIRED_MODEL_RULE:
        if phrase in lowered:
            errors.append(f"retired model rule {phrase!r} is back")
    errors.extend(_reviewer_tests_evidence_errors(text))
    return errors


def _harness_errors(harnesses: str, index: str) -> list[str]:
    """Every violated harness-matrix contract; empty means the rows are sound."""
    errors: list[str] = []
    section = _review_section(harnesses)
    if section is None:
        return ["harnesses.md has no review section"]
    whole = _normalized_lower(" ".join(section))

    blocks = _h3_blocks(section)
    zcode_retired = any("zcode" in heading
                        and all(needle in block for needle in ZCODE_RETIRE_NEEDLES)
                        for heading, block in blocks.items())
    if not zcode_retired:
        errors.append("the zcode review way is not named retired")
    for token in ZCODE_RETIRE_FORBIDDEN:
        if token in whole:
            errors.append(f"the retired zcode way names {token!r}")
    dsh_blocks = [block for heading, block in blocks.items() if "dsh" in heading]
    if not dsh_blocks:
        errors.append("dsh review way has no section")
    else:
        dsh_block = dsh_blocks[0]
        for token in DSH_WAY:
            if token not in dsh_block:
                errors.append(f"dsh review way is missing {token!r}")
        for phrase in ("пробел", "вне плана"):
            if phrase in dsh_block:
                errors.append(f"dsh review way is still named {phrase!r}")
        if ROUTE_STOP not in dsh_block:
            errors.append("dsh review way lost the route-stop rule")
        # review-output 01: the DSH row names the holistic scope and the dry
        # output without echo and points at the panel contract instead of
        # duplicating it; the capacity refusal waits for a slot.
        for phrase in PANEL_OUTPUT_ANCHORS[:3]:
            if phrase not in dsh_block:
                errors.append(f"dsh review way lost {phrase!r}")
        if "references/review-panel.md" not in dsh_block:
            errors.append("dsh review way does not point at the panel contract")
        for phrase in ("`activation_limit_reached`", "ожидание слота",
                       "лимит из живого профиля"):
            if phrase not in dsh_block:
                errors.append(f"dsh review way lost {phrase!r}")
    qoder_gap = any("qoder" in heading and "пробел" in block
                    for heading, block in blocks.items())
    if not qoder_gap:
        errors.append("qoder review way is not named a gap")
    if "безусловно" in whole:
        errors.append("the unconditional generator line is back")
    if GENERATOR_DSH_RULE not in whole:
        errors.append("the DSH generator rule is missing")

    if "review-roles.md" not in index:
        errors.append("docs/reference/README.md does not link review-roles.md")
    return errors


def _carrier_errors(text: str) -> list[str]:
    """Retired DSH-gap phrases and the lost Qoder gap in one procedure carrier."""
    lowered = _normalized_lower(text)
    errors = [f"retired DSH gap phrase {phrase!r} is back"
              for phrase in RETIRED_DSH_PHRASES if phrase in lowered]
    if "qoder" not in lowered:
        errors.append("the Qoder gap is not named")
    return errors


def _plan_live_errors(text: str, name: str) -> list[str]:
    """Violated fallback-cleanup contract of one plan spec; empty is sound.

    The live sections (Цель, Готово, Ограничения) carry the route-stop norm
    and no fallback wording; the dated decisions 4, 14 and 15 stay untouched
    and are read with the addendum «снято решением 2026-11-25», which sits in
    the appendix area after the decisions table and before «Готово».
    """
    live = "\n".join(_h2_section(text, heading)
                     for heading in ("Цель", "Готово", "Ограничения"))
    lowered = _normalized_lower(live)
    errors: list[str] = []
    if ROUTE_STOP_NORM not in lowered:
        errors.append(f"{name}: the live text lost the route stop")
    for phrase in FALLBACK_PHRASES:
        if phrase in lowered:
            errors.append(f"{name}: the live text carries {phrase!r}")
    marker = "снято решением 2026-11-25"
    lowered_text = text.lower()
    if marker not in lowered_text:
        errors.append(f"{name}: the fallback addendum is missing")
    elif "## решения план-гейта" not in lowered_text:
        errors.append(f"{name}: the decisions-table heading is missing")
    else:
        table = lowered_text.find("## решения план-гейта")
        ready = lowered_text.find("## готово")
        at = lowered_text.find(marker)
        if not table < at < ready:
            errors.append(f"{name}: the addendum left the appendix area")
    return errors


def test_reference_exists_with_sound_frontmatter():
    """spec: docs/plans/review-config.md#готово — docs/reference/review-roles.md."""
    assert REFERENCE.is_file(), "the review-roles reference is missing"
    assert _reference_errors(REFERENCE.read_text("utf-8")) == []


def test_reference_carries_the_base_set_role_contracts():
    """spec: docs/plans/review-config.md#решения план-гейта — 11: роли
    базового набора, каждая — узкий чек-лист."""
    text = REFERENCE.read_text("utf-8")
    sections = _h3_sections(text)
    for role in ROLES:
        assert any(role in heading.lower() for heading in sections), \
            f"role {role} has no section"
    assert _reference_errors(text) == []


def test_reference_layer_carries_no_role_count():
    """invariant: docs/plans/review-loose-ends.md#цель — счётчики-срезы не
    живут в справочниках: the reference and its index name no count before
    «рол…», and a returned count reddens (panel probe dwfrun-71b03204)."""
    for path in (REFERENCE, INDEX):
        text = path.read_text("utf-8")
        match = COUNTED_ROLE.search(text)
        assert match is None, f"{path.name}: a counted role snapshot {match.group(0)!r}"

    reference = REFERENCE.read_text("utf-8")
    returned = reference.replace("Каждая роль базового набора",
                                 "Базовый набор ядра — четыре роли; каждая", 1)
    assert returned != reference
    assert COUNTED_ROLE.search(returned) is not None, \
        "a returned role count must redden the reference"


def test_reference_states_input_output_and_independence():
    """spec: docs/plans/review-output.md#готово — вход: область роли целиком;
    выход: сухие структурированные находки; независимость — артефакты, не
    ход исполнения."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for phrase in ("область роли целиком", "чек-лист", *INDEPENDENCE_PHRASES):
        assert phrase in lowered, f"{phrase!r} is missing"


def test_panel_output_contract_lives_in_the_preamble_of_both_carriers():
    """spec: docs/plans/review-output.md#готово — общий контракт вывода (все
    пять игл) — в интро обоих носителей панели; старые строки «Область»
    четырёх ролей переведены на «область роли целиком»."""
    for carrier in PANEL_OUTPUT_CARRIERS:
        text = carrier.read_text("utf-8")
        intro = _panel_intro(text)
        assert intro, f"{carrier.name}: the panel preamble is not found"
        for anchor in (*PANEL_OUTPUT_ANCHORS, *PANEL_METRIC_ANCHORS):
            assert anchor in intro, \
                f"{carrier.name}: the panel preamble lost {anchor!r}"
        sections = _h3_sections(text)
        for role in ROLES:
            heading = next(h for h in sections if role in h.lower())
            role_body = _normalized_lower(sections[heading])
            assert "область роли целиком" in role_body, \
                f"{carrier.name}: role {role} keeps a menu scope"

    # can-fail: a lost preamble clause and a role that keeps the old menu
    # scope both redden; the other carrier stays sound.
    text = REFERENCE.read_text("utf-8")
    for anchor in PANEL_OUTPUT_ANCHORS:
        pattern = re.escape(anchor).replace(r"\ ", r"\s+")
        mutated = re.sub(pattern, "иное правило", text, count=0,
                         flags=re.IGNORECASE)
        assert mutated != text, anchor
        assert anchor not in _panel_intro(mutated), anchor
    sections = _h3_sections(text)
    kb_heading = next(h for h in sections if "reviewer-kb" in h.lower())
    menu = text.replace("область роли целиком — изменённые документы KB",
                        "изменённые документы KB", 1)
    assert menu != text
    assert "область роли целиком" not in _normalized_lower(
        _h3_sections(menu)[kb_heading])
    assert _reference_errors(menu) != []
    assert _reference_errors(text) == []


def test_fallback_cleanup_is_recorded_and_live_plans_are_clean():
    """spec: docs/plans/review-output.md#готово — чистка фолбэка: датированные
    решения 4, 14 и 15 не переписываются, после таблицы решений — приписка
    «снято решением 2026-11-25»; живой текст обоих планов несёт норму
    «подмены маршрута нет, стоп и вопрос оператору» и не несёт фолбэк-фраз."""
    for path in PLAN_CARRIERS:
        assert _plan_live_errors(path.read_text("utf-8"), path.name) == []

    # can-fail: a planted fallback phrase, a lost addendum and an addendum
    # that left the appendix area all redden.
    path = PLAN_CARRIERS[0]
    text = path.read_text("utf-8")
    planted = text.replace(
        "## Готово\n",
        "## Готово\n\nНедоступная модель заменяется моделью сессии.\n", 1)
    assert planted != text
    assert any("carries" in error
               for error in _plan_live_errors(planted, path.name))

    marker = "Снято решением 2026-11-25"
    no_addendum = text.replace(marker, "Разбор снят", 1)
    assert no_addendum != text
    assert any("addendum is missing" in error
               for error in _plan_live_errors(no_addendum, path.name))

    # Moving the addendum before the decisions table reddens.
    body_without = text.replace(marker, "", 1)
    moved = body_without.replace("## Решения план-гейта",
                                 f"{marker}\n\n## Решения план-гейта", 1)
    assert moved != body_without
    assert any("appendix area" in error
               for error in _plan_live_errors(moved, path.name))


def test_live_panel_carriers_carry_no_fallback():
    """spec: docs/plans/review-output.md#готово — живые носители (ship,
    review-panel, harnesses) фолбэк-фраз не несут; сторож зелёный на базе."""
    for path in LIVE_PANEL_CARRIERS:
        lowered = _normalized_lower(path.read_text("utf-8"))
        for phrase in FALLBACK_PHRASES:
            assert phrase not in lowered, f"{path.name}: {phrase!r} is back"


def test_reference_carries_the_pack_rules():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — 3: пак
    несёт стандарты, чек-листы ролей и конфиги механических гейтов как
    данные, имена reviewer-<kontur>-<aspect>, init обнаруживает роли пака;
    гейты остаются у ядра, конфиги исполняет ядро; снятое правило «только
    промпты и чек-листы» не возвращается."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for rule in PACK_RULES:
        assert rule in lowered, f"pack rule {rule!r} is missing"
    assert RETIRED_PACK_RULE not in lowered


def test_reference_names_the_core_pack_assembly_and_route_stop():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 3, 9: KB-носитель
    панели называет сборку из ролей ядра и ролей паков, остановку на
    недоступной паре и приоритет источников стандартов reviewer-code;
    DSH-способ матрицы несёт ту же остановку."""
    text = REFERENCE.read_text("utf-8")
    lowered = _normalized_lower(text)
    for phrase in PANEL_ASSEMBLY:
        assert phrase in lowered, f"the panel carrier lost {phrase!r}"
    harnesses = HARNESSES.read_text("utf-8")
    assert ROUTE_STOP in _normalized_lower(harnesses)

    # can-fail: each assembly clause and the route stop reddens on loss.
    # The priority phrase lives in two places (the panel preamble and the
    # reviewer-code scope): every occurrence must go for the probe.
    for phrase in PANEL_ASSEMBLY:
        pattern = re.escape(phrase).replace("\\ ", r"\s+")
        mutated = re.sub(pattern, "", text, flags=re.IGNORECASE)
        assert mutated != text, f"the mutation must change the text: {phrase!r}"
        assert any("panel assembly" in error
                   for error in _reference_errors(mutated)), phrase
    no_stop = re.sub(re.escape(ROUTE_STOP),
                     "недоступная пара — выбор другой модели", harnesses,
                     count=1, flags=re.IGNORECASE)
    assert no_stop != harnesses
    assert any("route-stop rule" in error
               for error in _harness_errors(no_stop, INDEX.read_text("utf-8")))


def test_reviewer_tests_checks_artifact_expectation_and_discrepancies():
    """spec: docs/plans/evidence-verification.md#готово — чек-лист reviewer-tests
    несёт оба пункта: «что и где смотреть + ожидание из спеки» («тест прошёл»
    без места осмотра — находка) и «разбор каждого расхождения или строка
    «не было»» со ссылкой на раздел testing.md."""
    text = REFERENCE.read_text("utf-8")
    assert _reviewer_tests_evidence_errors(text) == []


def test_harnesses_describe_the_review_way_and_keep_the_qoder_gap():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 1: матрица
    описывает способ ревью: zcode — снят (рельсы выведены решением
    оператора), DSH — рабочий способ через `subagent` и живой каталог,
    Qoder — названный пробел в своём подразделе."""
    errors = _harness_errors(HARNESSES.read_text("utf-8"),
                             INDEX.read_text("utf-8"))
    assert errors == []


def test_retired_dsh_gap_phrases_left_the_carriers():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 1: фраз «DSH —
    пробел окружения» и «DSH и Qoder — вне плана» нет в матрице, справочнике
    панели и прогоне онто-дока; Qoder назван во всех трёх."""
    for path in GAP_CARRIERS:
        errors = _carrier_errors(path.read_text("utf-8"))
        assert errors == [], f"{path}: {errors}"


def test_dsh_first_class_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the DSH-first-class contract rejects a lost DSH way token, a resurrected
    DSH gap row, a lost Qoder gap, the unconditional generator line and a
    retired phrase in any carrier."""
    harnesses = HARNESSES.read_text("utf-8")
    index = INDEX.read_text("utf-8")
    assert _harness_errors(harnesses, index) == []

    no_route = harnesses.replace("list_subagent_models", "каталог моделей", 1)
    assert no_route != harnesses
    assert any("list_subagent_models" in error
               for error in _harness_errors(no_route, index))

    regressed = harnesses.replace("### DSH — рабочий способ",
                                  "### DSH — пробел окружения", 1)
    assert regressed != harnesses
    assert any("still named 'пробел'" in error
               for error in _harness_errors(regressed, index))

    unconditional = harnesses.replace(
        "### zcode — снят\n",
        "### zcode — снят\n\nГенератор зовётся безусловно.\n\n", 1)
    assert unconditional != harnesses
    assert any("unconditional generator" in error
               for error in _harness_errors(unconditional, index))

    lost_rule = harnesses.replace("генератора определений в проекте нет",
                                  "определения не нужны", 1)
    assert lost_rule != harnesses
    assert any("DSH generator rule" in error
               for error in _harness_errors(lost_rule, index))

    no_qoder = harnesses.replace("пробел", "реализовано")
    assert no_qoder != harnesses
    assert any("qoder review way is not named a gap" in error
               for error in _harness_errors(no_qoder, index))

    carrier = GAP_CARRIERS[1].read_text("utf-8")
    assert _carrier_errors(carrier) == []
    assert any("dsh и qoder — вне плана" in error
               for error in _carrier_errors(
                   carrier + "\n### DSH и Qoder — вне плана\n"))
    renamed = carrier.replace("Qoder", "другой харнесс")
    assert any("Qoder gap is not named" in error
               for error in _carrier_errors(renamed))


def test_reference_is_linked_from_the_folder_index():
    """spec: docs/plans/review-config.md#готово — справочник связан из индекса
    папки."""
    index = INDEX.read_text("utf-8")
    assert "review-roles.md" in index


def test_reference_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract rejects a lost checklist, a renamed role, a lost pack rule, a
    lost DSH way token, a lost Qoder gap, the unconditional generator line,
    a lost zcode way and a broken index link."""
    text = REFERENCE.read_text("utf-8")
    assert _reference_errors(text) == []

    no_checklist = text.replace("Чек-лист", "Список проверок")
    assert no_checklist != text
    assert any("checklist is not named" in error
               for error in _reference_errors(no_checklist))

    renamed = text.replace("### reviewer-kb", "### reviewer-docs", 1)
    assert renamed != text
    assert any("reviewer-kb" in error for error in _reference_errors(renamed))

    no_pack_names = text.replace("reviewer-<kontur>-<aspect>",
                                 "reviewer-<pack>-<role>", 1)
    assert no_pack_names != text
    assert any("reviewer-<kontur>-<aspect>" in error
               for error in _reference_errors(no_pack_names))

    # Gate configs as data (decision 3): losing the «как данные» clause or
    # resurrecting the retired prompts-only rule both redden.
    no_data = text.replace("как данные", "как промпты", 1)
    assert no_data != text
    assert any("конфиги механических гейтов как данные" in error
               for error in _reference_errors(no_data))
    old_rule = text + "\n\nПак несёт только промпты и чек-листы.\n"
    assert any("retired pack rule" in error
               for error in _reference_errors(old_rule))

    # A role's checklist must be its own: dropping every bullet of the last
    # role (whose section once swallowed the trailing sections) has to fail.
    sections = _h3_sections(text)
    kb_heading = next(h for h in sections if h.lower().startswith("reviewer-kb"))
    kb_body = re.sub(r"(?m)^- .*$", "", sections[kb_heading], count=4)
    stripped = text.replace(sections[kb_heading], kb_body, 1)
    assert stripped != text
    assert any("checklist has" in error for error in _reference_errors(stripped))

    harnesses = HARNESSES.read_text("utf-8")
    index = INDEX.read_text("utf-8")
    assert _harness_errors(harnesses, index) == []

    # The Qoder gap must be named inside its own subsection: every «пробел»
    # leaving the block, or the block leaving the review section, must fail.
    unimplemented = harnesses.replace("пробел", "реализовано")
    assert unimplemented != harnesses
    errors = _harness_errors(unimplemented, index)
    assert any("is not named a gap" in error for error in errors)

    # Promoting the DSH row out of the review section (### → ##) must leave
    # the section without both rows — the DSH way and the Qoder gap.
    # The fuller «### DSH» of the «Доказательства» section is a different row;
    # the gap heading alone carries « — пробел».
    deheaded = harnesses.replace("### DSH — рабочий способ",
                                "## DSH — рабочий способ", 1)
    assert deheaded != harnesses
    errors = _harness_errors(deheaded, index)
    assert any("dsh" in error for error in errors)
    assert any("qoder" in error for error in errors)

    # The zcode subsection must stay a retirement note: an unretired heading
    # or a resurrected transport token both redden.
    unretired = harnesses.replace("### zcode — снят", "### zcode — рабочий способ", 1)
    assert unretired != harnesses
    assert any("not named retired" in error
               for error in _harness_errors(unretired, index))

    resurrected = harnesses.replace(
        "### zcode — снят\n",
        "### zcode — снят\n\nПанель вела роли через `subagent_model`.\n\n", 1)
    assert resurrected != harnesses
    assert any("retired zcode way" in error
               for error in _harness_errors(resurrected, index))

    # Every occurrence must go — the frontmatter link alone would keep the
    # `not in` check green — so the index truly stops naming the reference.
    orphan = index.replace("review-roles.md", "roles.md")
    assert orphan != index
    assert any("does not link review-roles.md" in error
               for error in _harness_errors(harnesses, orphan))


def test_evidence_items_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: потеря любой части двух пунктов чек-листа
    reviewer-tests красит его — маркер пункта, список носителей, «тест
    прошёл», следствие-находку, разбор расхождений, «не было» и ссылку на
    раздел testing.md."""
    text = REFERENCE.read_text("utf-8")
    assert _reference_errors(text) == []

    no_what_where = text.replace("что и где смотреть", "место осмотра", 1)
    assert no_what_where != text
    assert any("что и где смотреть" in error
               for error in _reference_errors(no_what_where))

    # The carriers list is wrapped across lines in the checklist; mutating
    # its last word kills the phrase after whitespace normalisation.
    no_carriers = text.replace("живая проба", "ручная проверка", 1)
    assert no_carriers != text
    assert any("вывод команды, строка лога, файл, живая проба" in error
               for error in _reference_errors(no_carriers))

    no_expectation = text.replace("ожидание из спеки",
                                  "ожидание из требований", 1)
    assert no_expectation != text
    assert any("ожидание из спеки" in error
               for error in _reference_errors(no_expectation))

    green_only = text.replace("тест прошёл", "зелёный тест", 1)
    assert green_only != text
    assert any("тест прошёл" in error
               for error in _reference_errors(green_only))

    no_finding = text.replace("без места осмотра", "без указания места", 1)
    assert no_finding != text
    assert any("без места осмотра — находка" in error
               for error in _reference_errors(no_finding))

    no_dissection = text.replace("разбор каждого расхождения",
                                 "разбор несовпадений", 1)
    assert no_dissection != text
    assert any("разбор каждого расхождения" in error
               for error in _reference_errors(no_dissection))

    no_clean_line = text.replace("не было", "отсутствовали", 1)
    assert no_clean_line != text
    assert any("'не было'" in error
               for error in _reference_errors(no_clean_line))

    no_link = text.replace("docs/reference/testing.md", "testing.md", 1)
    assert no_link != text
    assert any("docs/reference/testing.md" in error
               for error in _reference_errors(no_link))
