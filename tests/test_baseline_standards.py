"""Contract for the baseline-standards step (standards-autoship ticket 03).

The pack skill carries a separate pass after init: the agent assembles
``docs/reference/baseline-standards.md`` from model knowledge (general
engineering practices plus the project stack practices), the operator approves
it once via the host ask tool, the approval is fixed in the document (date,
operator decision); the init four-file contract stays untouched. The document
exists in this repository (dogfood), is linked from the folder index, carries
the approval mark in its own section and the verbatim norm priority with the
conflict-to-operator rule. The panel input names the standards sources in
priority order, the baseline document last.

Jurisdiction split with the ticket-01 contract (tests/test_skill_pack.py):
the norm priority literal in the pack skill body and the harness-root ban on
bundle files are guarded there; this file guards the step section, the
conflict rule, the document and the index link. KB documents may name harness
roots legitimately (harnesses.md), so no root ban applies to the document.

spec: docs/plans/standards-autoship.md#готово — «Готово» 4: скилл pack
      отдельным шагом после init собирает baseline-standards.md из знаний
      модели, оператор утверждает ask-ом один раз, утверждение фиксируется
      в документе; источник стандартов называется во входе панели; init
      сохраняет контракт четырёх файлов
spec: docs/plans/standards-autoship.md#решения план-гейта — решения 8, 9:
      приоритет норм канон > проект > команда > стек > базовый документ,
      неразрешимый конфликт — вопрос оператору; базовые стандарты без пака
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "pack" / "SKILL.md"
DOC = REPO / "docs" / "reference" / "baseline-standards.md"
INDEX = REPO / "docs" / "reference" / "README.md"
INIT = REPO / "skills" / "init" / "SKILL.md"

STEP_HEADING = "базовые стандарты"
STEP_PHRASES = (
    "отдельный проход после init",
    "не часть init",
    "контракт четырёх файлов",
    "docs/reference/baseline-standards.md",
    "из знаний модели",
    "оператор утверждает документ ask-инструментом хоста один раз",
    "утверждение фиксируется в документе",
    "решение оператора (кто утвердил)",
    "дата — во frontmatter",
    "только решением оператора",
    "docs/reference/readme.md",
    "нижний приоритет",
    "источник стандартов называется во входе панели",
    "базовый документ — последним",
)
PRIORITY = "канон > стандарты проекта > пак команды > пак стека > базовый документ"
CONFLICT = "неразрешимый конфликт норм — вопрос оператору"
APPROVAL_HEADING = "отметка утверждения"
APPROVAL_PHRASES = (
    "оператор утвердил документ",
    "ask-ом, вариант «утвердить»",
)
DOC_PHRASES = APPROVAL_PHRASES + (
    "из знаний модели",
    "общие практики инженерии",
    "практики стека проекта",
    PRIORITY,
    CONFLICT,
)


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _drop_phrase(text: str, phrase: str) -> str:
    """Remove every occurrence of a phrase regardless of case and internal
    line wrapping (runs of whitespace inside the phrase match any run)."""
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def _section(body: str, heading: str) -> str:
    lowered = body.lower()
    start = lowered.find(f"## {heading}")
    if start < 0:
        return ""
    return body[start:].split("\n## ", 1)[0]


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("document must start with YAML frontmatter")
    try:
        close = lines.index("---", 1)
    except ValueError:
        raise ValueError("unclosed frontmatter") from None
    fields: dict[str, str] = {}
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def _step_errors(skill_text: str) -> list[str]:
    """The baseline-standards step of the pack skill; empty means it holds.

    The priority literal in the skill body and the harness-root ban are
    guarded by tests/test_skill_pack.py (ticket 01); the conflict rule is
    this file's jurisdiction.
    """
    lowered = _normalized(skill_text)
    errors: list[str] = []
    section = _normalized(_section(skill_text, STEP_HEADING))
    if not section:
        errors.append(f"step: missing section «{STEP_HEADING}»")
    else:
        for phrase in STEP_PHRASES:
            if phrase not in section:
                errors.append(f"step: section lost {phrase!r}")
    if CONFLICT not in lowered:
        errors.append(f"step: skill body lost {CONFLICT!r}")
    return errors


def _doc_errors(doc_text: str) -> list[str]:
    """The baseline-standards document; empty means it holds.

    Approval phrases are checked inside the approval section only: a date
    in the frontmatter or an «ask» elsewhere must not satisfy the mark.
    """
    errors: list[str] = []
    try:
        fields = _frontmatter(doc_text)
    except ValueError as exc:
        return [f"doc: {exc}"]
    if fields.get("node_type") != "reference":
        errors.append("doc: node_type must be reference")
    lowered = _normalized(doc_text)
    approval = _normalized(_section(doc_text, APPROVAL_HEADING))
    if not approval:
        errors.append(f"doc: missing section «{APPROVAL_HEADING}»")
    else:
        for phrase in APPROVAL_PHRASES:
            if phrase not in approval:
                errors.append(f"doc: approval section lost {phrase!r}")
    for phrase in DOC_PHRASES:
        if phrase in APPROVAL_PHRASES:
            continue
        if phrase not in lowered:
            errors.append(f"doc: missing phrase {phrase!r}")
    return errors


def test_step_is_described_in_the_pack_skill() -> None:
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 4: шаг
    базовых стандартов — отдельный проход после init, ask-утверждение
    один раз, фиксация в документе; контракт init не тронут."""
    assert _step_errors(SKILL.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("phrase", STEP_PHRASES)
def test_every_step_phrase_has_a_failing_probe(phrase: str) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any step phrase, however short, reddens the step contract."""
    text = SKILL.read_text(encoding="utf-8")
    mutated = _drop_phrase(text, phrase)
    assert mutated != text, f"the mutation must remove {phrase!r}"
    errors = _step_errors(mutated)
    assert any(f"step: section lost {phrase!r}" in error
               for error in errors), errors


def test_step_contract_can_fail() -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the step check rejects a renamed section and a lost conflict rule."""
    text = SKILL.read_text(encoding="utf-8")
    assert _step_errors(text) == []

    renamed = text.replace("## Базовые стандарты", "## Стандарты проекта", 1)
    assert renamed != text
    assert any("missing section" in error for error in _step_errors(renamed))

    no_conflict = _drop_phrase(text, CONFLICT)
    assert no_conflict != text
    assert any(f"skill body lost {CONFLICT!r}" in error
               for error in _step_errors(no_conflict))


def test_document_exists_and_is_approved() -> None:
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 4: документ
    существует в этом репозитории (dogfood), несёт отметку утверждения
    оператором (решение оператора; дата — во frontmatter), источник — знания модели, оба класса
    практик, приоритет норм дословно, конфликт уходит оператору."""
    assert DOC.is_file(), "the baseline-standards document is missing"
    assert _doc_errors(DOC.read_text(encoding="utf-8")) == []


def test_document_contract_can_fail() -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the document check rejects a lost approval mark, a lost content class,
    a lost priority order, a lost conflict rule and a wrong node_type
    (мутационные пробы по каждой фразе DOC_PHRASES)."""
    text = DOC.read_text(encoding="utf-8")
    assert _doc_errors(text) == []

    for phrase in DOC_PHRASES:
        mutated = _drop_phrase(text, phrase)
        assert mutated != text, f"the mutation must remove {phrase!r}"
        errors = _doc_errors(mutated)
        if phrase in APPROVAL_PHRASES:
            assert any(f"approval section lost {phrase!r}" in error
                       for error in errors), phrase
        else:
            assert any(f"missing phrase {phrase!r}" in error
                       for error in errors), phrase

    wrong_type = text.replace("node_type: reference", "node_type: guide", 1)
    assert wrong_type != text
    assert any("node_type must be reference" in error
               for error in _doc_errors(wrong_type))

    no_frontmatter = text.split("---\n", 2)[2]
    assert any("frontmatter" in error for error in _doc_errors(no_frontmatter))

    first_fence = text.index("---\n")
    second_fence = text.index("---\n", first_fence + 4)
    unclosed = text[:second_fence] + text[second_fence + 4:]
    assert any("unclosed frontmatter" in error
               for error in _doc_errors(unclosed))


def test_document_is_linked_from_the_folder_index() -> None:
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 4: документ
    связан из индекса папки docs/reference/README.md."""
    index = INDEX.read_text(encoding="utf-8")
    assert "baseline-standards.md" in index, \
        "the folder index must link the baseline-standards document"


def test_init_four_file_contract_is_untouched() -> None:
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 9:
    контракт init (четыре файла) не меняется; базовые стандарты — шаг pack,
    не пятый файл init. Полный текст контракта живёт в скилле init; pack
    names it without retelling the file list."""
    text = INIT.read_text(encoding="utf-8")
    lowered = _normalized(text)
    assert "пишет эти четыре файла и ничего больше" in lowered
    assert "baseline-standards" not in lowered, \
        "init must not own the baseline-standards document"