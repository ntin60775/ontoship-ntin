"""Contract for the review-roles reference and the harness review rows (review-config ticket 04).

``docs/reference/review-roles.md`` must carry the base-set role
contracts — ``reviewer-spec``, ``reviewer-tests``, ``reviewer-code``,
``reviewer-kb`` — each with a scope and a checklist, plus the pack rules:
packs carry prompts and checklists only, role names follow
``reviewer-<kontur>-<aspect>``, init detects pack roles, gates stay with the
core. ``docs/reference/harnesses.md`` must describe how each harness
organizes the review panel: the working zcode way (role definitions from the
config, the full-restart cost of a model change, the ``subagent_model``
fallback path, the ``[current]`` marker for the session-model check) and DSH
and Qoder each named a gap inside their own subsection of the review
section, never implemented silently. The reference is linked from the folder
index. The ``reviewer-tests`` checklist additionally carries the two
evidence items: every acceptance criterion must show what and where to look
(command output, log line, file, live probe) plus a spec-sourced expectation
— «тест прошёл» with no place to look is a finding — and the ticket must
dissect every expectation/fact discrepancy or carry the line «не было»,
linking the «Артефакт доказательства» section of docs/reference/testing.md
(evidence-verification ticket 02).

spec: docs/plans/review-config.md#готово — справочник ролей и регламент паков
spec: docs/plans/review-config.md#готово — матрица harnesses.md дополнена:
ревью DSH и Qoder описаны и названы пробелом
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
PACK_RULES = (
    "пак",
    "только промпты и чек-листы",
    "reviewer-<kontur>-<aspect>",
    "без кода",
    "гейт",
    "init",
)
ZCODE_WAY = (
    "определени",
    "gen_agents.py",
    "полный перезапуск",
    "subagent_model",
    "[current]",
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

    lowered = _normalized_lower(text)
    for phrase in INDEPENDENCE_PHRASES:
        if phrase not in lowered:
            errors.append(f"missing required phrase {phrase!r}")
    for rule in PACK_RULES:
        if rule not in lowered:
            errors.append(f"pack rule {rule!r} is missing")
    errors.extend(_reviewer_tests_evidence_errors(text))
    return errors


def _harness_errors(harnesses: str, index: str) -> list[str]:
    """Every violated harness-matrix contract; empty means the rows are sound."""
    errors: list[str] = []
    section = _review_section(harnesses)
    if section is None:
        return ["harnesses.md has no review section"]
    whole = _normalized_lower(" ".join(section))

    for token in ZCODE_WAY:
        if token not in whole:
            errors.append(f"zcode review way is missing {token!r}")
    blocks = _h3_blocks(section)
    for harness in ("dsh", "qoder"):
        named_gap = any(harness in heading and "пробел" in block
                        for heading, block in blocks.items())
        if not named_gap:
            errors.append(f"{harness} review way is not named a gap")
    if "фолбэк" not in whole:
        errors.append("the role-model fallback (decision 14) is not mentioned")

    if "review-roles.md" not in index:
        errors.append("docs/reference/README.md does not link review-roles.md")
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
    """spec: docs/plans/review-config.md#готово — вход: область и чек-лист;
    выход: вердикт и находки с приоритетами и зацепками; независимость —
    артефакты, не ход исполнения."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for phrase in ("область", "чек-лист", *INDEPENDENCE_PHRASES):
        assert phrase in lowered, f"{phrase!r} is missing"


def test_reference_carries_the_pack_rules():
    """spec: docs/plans/review-config.md#решения план-гейта — 12: пак несёт
    только промпты и чек-листы, имена reviewer-<kontur>-<aspect>, init
    обнаруживает роли пака; гейты остаются у ядра."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for rule in PACK_RULES:
        assert rule in lowered, f"pack rule {rule!r} is missing"


def test_reviewer_tests_checks_artifact_expectation_and_discrepancies():
    """spec: docs/plans/evidence-verification.md#готово — чек-лист reviewer-tests
    несёт оба пункта: «что и где смотреть + ожидание из спеки» («тест прошёл»
    без места осмотра — находка) и «разбор каждого расхождения или строка
    «не было»» со ссылкой на раздел testing.md."""
    text = REFERENCE.read_text("utf-8")
    assert _reviewer_tests_evidence_errors(text) == []


def test_harnesses_describe_the_review_way_and_name_the_gaps():
    """spec: docs/plans/review-config.md#готово — матрица описывает способ
    ревью: zcode рабочий (определения, полный перезапуск, subagent_model),
    DSH и Qoder — названные пробелы в своих подразделах раздела ревью."""
    errors = _harness_errors(HARNESSES.read_text("utf-8"),
                             INDEX.read_text("utf-8"))
    assert errors == []


def test_reference_is_linked_from_the_folder_index():
    """spec: docs/plans/review-config.md#готово — справочник связан из индекса
    папки."""
    index = INDEX.read_text("utf-8")
    assert "review-roles.md" in index


def test_reference_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract rejects a lost checklist, a renamed role, a lost pack rule, a
    lost DSH/Qoder gap row (word, block and section level), a lost zcode way
    and a broken index link."""
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

    # A gap must be named inside its own subsection: every «пробел» leaving
    # the DSH block, or the block leaving the review section, must fail.
    unimplemented = harnesses.replace("пробел", "реализовано")
    assert unimplemented != harnesses
    errors = _harness_errors(unimplemented, index)
    assert any("is not named a gap" in error for error in errors)

    # Promoting the DSH gap row out of the review section (### → ##) must
    # leave the section without its gap rows — both harnesses go missing.
    # The fuller «### DSH» of the «Доказательства» section is a different row;
    # the gap heading alone carries « — пробел».
    deheaded = harnesses.replace("### DSH — пробел", "## DSH — пробел", 1)
    assert deheaded != harnesses
    errors = _harness_errors(deheaded, index)
    assert any("dsh" in error for error in errors)
    assert any("qoder" in error for error in errors)

    no_fallback = harnesses.replace("subagent_model", "agent tool", 1)
    assert no_fallback != harnesses
    assert any("subagent_model" in error
               for error in _harness_errors(no_fallback, index))

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
