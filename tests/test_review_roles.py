"""Contract for the review-roles reference and the harness review rows (review-config ticket 04).

``docs/reference/review-roles.md`` must carry the four base-set role
contracts — ``reviewer-spec``, ``reviewer-tests``, ``reviewer-code``,
``reviewer-kb`` — each with a scope and a checklist, plus the pack rules:
packs carry prompts and checklists only, role names follow
``reviewer-<kontur>-<aspect>``, init detects pack roles, gates stay with the
core. ``docs/reference/harnesses.md`` must describe how each harness
organizes the review panel: the working zcode way (role definitions from the
config, the full-restart cost of a model change, the ``subagent_model``
fallback path, the ``[current]`` marker for the session-model check) and DSH
and Qoder each named a gap, never implemented silently. The reference is
linked from the folder index.

spec: docs/plans/review-config.md#готово — справочник ролей и регламент паков
spec: docs/plans/review-config.md#готово — матрица harnesses.md дополнена:
ревью DSH и Qoder описаны и названы пробелом
spec: docs/plans/review-config.md#решения план-гейта — 9, 11, 12
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
    """Map each ``### heading`` to its body (up to the next heading)."""
    sections: dict[str, str] = {}
    current = None
    chunks: list[str] = []
    for line in text.splitlines():
        if line.startswith("### "):
            if current is not None:
                sections[current] = "\n".join(chunks)
            current = line[4:].strip()
            chunks = []
        elif current is not None:
            chunks.append(line)
    if current is not None:
        sections[current] = "\n".join(chunks)
    return sections


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


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
        if "чек-лист" not in lowered:
            errors.append(f"role {role!r}: checklist is not named")
        items = len(re.findall(r"(?m)^- ", body))
        if items < 3:
            errors.append(f"role {role!r}: checklist has {items} items, need 3+")
        if "область" not in lowered:
            errors.append(f"role {role!r}: scope (область) is not named")

    lowered = _normalized_lower(text)
    for phrase in ("вердикт", "приоритет", "зацепк", "артефакты",
                   "не ход исполнения"):
        if phrase not in lowered:
            errors.append(f"missing required phrase {phrase!r}")
    for rule in PACK_RULES:
        if rule not in lowered:
            errors.append(f"pack rule {rule!r} is missing")
    return errors


def _harness_errors(harnesses: str, index: str) -> list[str]:
    """Every violated harness-matrix contract; empty means the rows are sound."""
    errors: list[str] = []
    lowered = _normalized_lower(harnesses)
    review_start = lowered.find("## ревью")
    if review_start < 0:
        return ["harnesses.md has no review section"]
    next_h2 = lowered.find("\n## ", review_start)
    review = lowered[review_start:next_h2 if next_h2 > 0 else len(lowered)]

    for token in ZCODE_WAY:
        if token not in review:
            errors.append(f"zcode review way is missing {token!r}")
    for harness in ("dsh", "qoder"):
        named_gap = False
        for line in review.splitlines():
            if harness in line and "пробел" in line:
                named_gap = True
        if not named_gap:
            errors.append(f"{harness} review way is not named a gap")
    if "фолбэк" not in review:
        errors.append("the role-model fallback (decision 14) is not mentioned")

    if "review-roles.md" not in index:
        errors.append("docs/reference/README.md does not link review-roles.md")
    return errors


def test_reference_exists_with_sound_frontmatter():
    """spec: docs/plans/review-config.md#готово — docs/reference/review-roles.md."""
    assert REFERENCE.is_file(), "the review-roles reference is missing"
    assert _reference_errors(REFERENCE.read_text("utf-8")) == []


def test_reference_carries_the_four_base_set_role_contracts():
    """spec: docs/plans/review-config.md#решения план-гейта — 11: четыре роли,
    каждая — узкий чек-лист."""
    text = REFERENCE.read_text("utf-8")
    sections = _h3_sections(text)
    for role in ROLES:
        assert any(role in heading.lower() for heading in sections), \
            f"role {role} has no section"
    assert _reference_errors(text) == []


def test_reference_states_input_output_and_independence():
    """spec: docs/plans/review-config.md#готово — вход: область и чек-лист;
    выход: вердикт и находки с приоритетами и зацепками; независимость —
    артефакты, не ход исполнения."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for phrase in ("область", "чек-лист", "вердикт", "приоритет", "зацепк",
                   "артефакты", "не ход исполнения"):
        assert phrase in lowered, f"{phrase!r} is missing"


def test_reference_carries_the_pack_rules():
    """spec: docs/plans/review-config.md#решения план-гейта — 12: пак несёт
    только промпты и чек-листы, имена reviewer-<kontur>-<aspect>, init
    обнаруживает роли пака; гейты остаются у ядра."""
    lowered = _normalized_lower(REFERENCE.read_text("utf-8"))
    for rule in PACK_RULES:
        assert rule in lowered, f"pack rule {rule!r} is missing"


def test_harnesses_describe_the_review_way_and_name_the_gaps():
    """spec: docs/plans/review-config.md#готово — матрица описывает способ
    ревью: zcode рабочий (определения, полный перезапуск, subagent_model),
    DSH и Qoder — названные пробелы."""
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
    contract rejects a lost checklist, a renamed role, a lost pack rule, an
    unimplemented DSH/Qoder row, a lost zcode way and a broken index link."""
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

    harnesses = HARNESSES.read_text("utf-8")
    index = INDEX.read_text("utf-8")
    assert _harness_errors(harnesses, index) == []

    # Every «пробел» must go: the DSH block keeps the word in its body line
    # («dsh headless …»), so a single replacement would leave the gap named.
    implemented = harnesses.replace("пробел", "реализовано")
    assert implemented != harnesses
    errors = _harness_errors(implemented, index)
    assert any("is not named a gap" in error for error in errors)

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
