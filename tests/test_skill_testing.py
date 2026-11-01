"""Contract for the testing skill (workflow-skills ticket 04).

The bundle must be discoverable as ``<root>/testing/SKILL.md`` and carry the
canon's quality rule: exactly three legal test goals (spec, invariant,
target) with ``spec:`` / ``invariant:`` / ``target:`` traceability, an
independent source for every expected value, the target-test quality bar,
the seven-step agent cycle, channels named as tools rather than goals, and
metrics counting spec items, invariants and fixed defects — never lines or
test counts.

spec: docs/plans/workflow-skills.md#готово — skills/testing/SKILL.md: three
classes, independent expected value, target bar, seven-step cycle, metrics
spec: docs/decisions/ontoship-core.md#одно правило качества — three goals,
traceability markers, independent expected value, channels as tools,
coverage in spec items
invariant: docs/plans/workflow-skills.md#ограничения — the skill stays
model-invocable; only to-tickets and ship are model-inaccessible
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "testing" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
ANCHOR_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)+:\d+")
CYCLE_STEPS = ("**воспроизведи", "**исследуй", "**рассуди",
               "**набросай и запусти", "**планка качества", "**исправь",
               "**диагностируй при неудаче")
TARGET_BAR = ("реальный путь сбоя", "red→green", "стабильность и детерминизм",
              "читаемость", "вторая пара глаз", "пока класс сбоя жив")
CHANNELS = ("unit/contract", "e2e/smoke", "ожидаемый вывод",
            "записанное воспроизведение", "браузер/снимок", "производительность")
TRACE_MARKERS = ("spec: <path>#<criterion>", "invariant: i<n>",
                 "invariant: <path>#<section> — <statement>",
                 "target: <bug/incident ref>")
REQUIRED_PHRASES = (
    "ровно три законные цели",
    "spec-тест",
    "инвариантный охранник",
    "target-тест",
    "воспроизводит реальный сбой",
    "сирота",
    "в имени или docstring",
    "независимого источника",
    "спеки, литерала или разобранного примера",
    "не пересчитывается тем же способом",
    "тавтологичен",
    "негативной или мутационной пробой",
    "тест должен уметь падать",
    "каналы — инструменты, а не цели",
    "может жить в любом канале",
    "покрытие считается пунктами спеки, инвариантами и исправленными "
    "дефектами",
    "способным упасть",
    "утёкшие дефекты",
    "строки и количество тестов — не метрики",
    "тем же изменением",
    "назначь бюджет",
    "доступен модели",
    "лог прогона",
    "docs/decisions/ontoship-core.md",
    "одно правило качества",
    "docs/reference/testing.md",
) + TRACE_MARKERS + CHANNELS + TARGET_BAR + CYCLE_STEPS
FORBIDDEN_PHRASES = (
    "покрытие строк",
    "число тестов",
)


def _parse(text: str) -> tuple[dict[str, str], str]:
    """Parse the simple single-line YAML frontmatter this skill uses."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        close = lines.index("---", 1)
    except ValueError:
        raise ValueError("unterminated YAML frontmatter") from None
    fields: dict[str, str] = {}
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"frontmatter line is not a key: {line!r}")
        fields[key.strip()] = value.strip()
    return fields, "\n".join(lines[close + 1:])


def _unquote(value: str) -> str:
    """Strip matching YAML quotes; the skill keeps its description quoted."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _contract_errors(text: str) -> list[str]:
    """Return every violated skill contract; empty means the skill is sound."""
    try:
        fields, body = _parse(text)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    name = fields.get("name", "")
    raw_description = fields.get("description", "")
    description = _unquote(raw_description)
    if not name:
        errors.append("frontmatter: missing name")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"frontmatter: invalid kebab-case name {name!r}")
    if not description:
        errors.append("frontmatter: missing description")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"frontmatter: description is {len(description)} chars "
                      f"(catalog cap {DESCRIPTION_MAX})")
    if ": " in description and not (raw_description.startswith('"')
                                    and raw_description.endswith('"')):
        errors.append("frontmatter: description contains ': ' and must be quoted")
    if fields.get("disable-model-invocation", "").lower() == "true":
        errors.append("frontmatter: disable-model-invocation must not be true "
                      "(the model applies the quality rule; only to-tickets "
                      "and ship are model-inaccessible)")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            errors.append(f"body: forbidden metric phrase {phrase!r} — "
                          f"coverage counts spec items, invariants and "
                          f"fixed defects, not lines or test counts")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
    # .zcode stays banned here: this skill names no channel roots.
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/workflow-skills.md#готово — skills/testing/SKILL.md."""
    assert SKILL.is_file(), "the testing skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "testing"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_model_invocable():
    """invariant: docs/plans/workflow-skills.md#ограничения — the model loads
    the skill while writing and reviewing tests."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert fields.get("disable-model-invocation", "").lower() != "true"
    lowered = _normalized_lower(body)
    assert "доступен модели" in lowered
    assert "не вызывает пользовательских скиллов" in lowered


def test_skill_carries_the_three_classes():
    """spec: docs/plans/workflow-skills.md#готово — item 4: three test classes."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "ровно три законные цели" in lowered
    assert "spec-тест" in lowered
    assert "инвариантный охранник" in lowered
    assert "target-тест" in lowered
    assert "воспроизводит реальный сбой" in lowered
    assert "сирота" in lowered
    assert "пересказывающий реализацию" in lowered


def test_every_goal_is_traceable():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — the goal
    is traceable in the test name or comment."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    for marker in TRACE_MARKERS:
        assert marker in lowered, f"traceability marker {marker!r} missing"
    assert "в имени или docstring" in lowered


def test_expected_value_has_an_independent_source():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — the
    expected value is never recomputed the way the code computes it."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "независимого источника" in lowered
    assert "спеки, литерала или разобранного примера" in lowered
    assert "не пересчитывается тем же способом" in lowered
    assert "тавтологичен" in lowered


def test_target_bar_is_complete():
    """spec: docs/plans/workflow-skills.md#готово — the target-test bar."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    for item in TARGET_BAR:
        assert item in lowered, f"target-bar item {item!r} missing"
    assert "искусственное исключение" in lowered
    assert "приватном шве" in lowered


def test_agent_cycle_has_seven_steps_in_order():
    """spec: docs/plans/workflow-skills.md#готово — the seven-step cycle."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    positions = [lowered.find(step) for step in CYCLE_STEPS]
    assert all(position >= 0 for position in positions), \
        f"a cycle step is missing: {list(zip(CYCLE_STEPS, positions))}"
    assert positions == sorted(positions), \
        "the cycle steps must appear in reproduce → … → diagnose order"
    assert "назначь бюджет" in lowered


def test_channels_are_tools_not_goals():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — channels
    are tools (how), spec/invariant/target are goals (what)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "каналы — инструменты, а не цели" in lowered
    for channel in CHANNELS:
        assert channel in lowered, f"channel {channel!r} missing"
    assert "может жить в любом канале" in lowered
    assert "канал — **как** тест доказывает" in lowered
    assert "spec/invariant/target — **что** он доказывает" in lowered


def test_metrics_count_spec_items_invariants_and_defects():
    """spec: docs/plans/workflow-skills.md#готово — item 4: coverage counts
    spec items, invariants and fixed defects."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert ("покрытие считается пунктами спеки, инвариантами и исправленными "
            "дефектами") in lowered
    assert "способным упасть" in lowered
    assert "утёкшие дефекты" in lowered
    assert "устаревшие тесты" in lowered
    assert "флейки" in lowered
    assert "строки и количество тестов — не метрики" in lowered
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in lowered, f"forbidden metric phrase {phrase!r} leaked"


def test_deprecation_removes_tests_in_the_same_change():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — outdated
    tests leave with the change that retires the item."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "тем же изменением" in lowered


def test_skill_anchors_to_the_canon():
    """spec: docs/decisions/ontoship-core.md#одно правило качества — the skill
    cites the canon section it carries."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "docs/decisions/ontoship-core.md" in lowered
    assert "одно правило качества" in lowered
    assert "docs/reference/testing.md" in lowered


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific
    skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a forbidden metric, a lost cycle step, a
    model-invocation ban, an anchor, a tautological oracle, a lost traceability
    marker and a missing name."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    line_metric = text.replace("Строки и количество тестов — не метрики",
                               "Метрика — покрытие строк", 1)
    assert line_metric != text
    assert any("покрытие строк" in error for error in _contract_errors(line_metric))

    dropped_step = text.replace("**Исправь.", "**Правь.", 1)
    assert dropped_step != text
    assert any("a cycle step is missing" in error or "**исправь" in error
               for error in _contract_errors(dropped_step))

    banned = text.replace("name: testing\n",
                          "name: testing\ndisable-model-invocation: true\n", 1)
    assert banned != text
    assert any("disable-model-invocation" in error for error in _contract_errors(banned))

    anchored = text.replace("## Трассируемость",
                            "## Трассируемость\n\nСмотри `skills/testing/SKILL.md:7`.", 1)
    assert anchored != text
    assert any("SKILL.md:7" in error for error in _contract_errors(anchored))

    tautology = text.replace("не пересчитывается тем же способом",
                             "пересчитывай значение тем же способом, что и код", 1)
    assert tautology != text
    assert any("не пересчитывается тем же способом" in error
               for error in _contract_errors(tautology))

    untraceable = text.replace("invariant: I<n>", "инвариант — номер", 1)
    assert untraceable != text
    assert any("invariant: i<n>" in error for error in _contract_errors(untraceable))

    project_invariant = text.replace(
        "invariant: <path>#<section> — <statement>", "инвариант проекта", 1)
    assert project_invariant != text
    assert any("invariant: <path>#<section> — <statement>" in error
               for error in _contract_errors(project_invariant))

    oracular_matrix = text.replace("тест должен уметь падать",
                                   "тест может оставаться зелёным", 1)
    assert oracular_matrix != text
    assert any("тест должен уметь падать" in error
               for error in _contract_errors(oracular_matrix))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))
