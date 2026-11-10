"""Contract for the onto-doc skill (onto-doc ticket 02).

The bundle must be discoverable as ``<root>/onto-doc/SKILL.md`` and carry the
whole-KB build translated from the original ``/onto-doc`` command (clone
``contrib/clones/ontoship``, ``commands/onto-doc.md``): six steps in the
original order plus the closing principle, word-for-word in translation, with
adaptations only from decision 2 of the spec. The description carries the
launch triggers and the boundary with ``kb-curate``: one article is the light
path. The launch procedure verifies the curator role's model and level against
the host model catalog before dispatch — drift stops, a missing catalog is a
named gap and a stop, never a guess (decision 4); the saved workflow run is
read back per area; lint, index and map stay in the session.

spec: docs/plans/onto-doc.md#готово — скилл onto-doc: текст оригинала
      в переводе, адаптации только из списка решения 2, триггеры и граница
      с kb-curate
spec: docs/plans/onto-doc.md#готово — процедура запуска: сверка model+level
      со стопом на расхождении, без каталога — названный пробел и стоп,
      чтение отчёта и lint+index+map в сессии (решение 4)
spec: docs/plans/onto-doc.md#ограничения — перевод не пересказ: шаги,
      порядок и машинные литералы оригинала сохраняются
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "onto-doc" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
TRIGGERS = ("онто-док", "погони онто-док", "бутстрап kb", "пересбор kb")
STEP_TITLES = (
    "обследуй репозиторий",
    "разбей на док-области",
    "запусти кураторов (fan-out)",
    "точка входа и индексы",
    "проверь и выведи производное",
    "отчёт",
)
REQUIRED_PHRASES = (
    # step 1 — survey, engine literal adapted per decision 2
    "python3 skills/kb-search/gitmark.py stat",
    # step 2 — decomposition targets
    "docs/services/<svc>/readme.md",
    "node_type: service",
    "docs/reference/",
    "docs/ops/",
    "docs/decisions/",
    # step 3 — Task → workflow transport (decision 2), curators follow kb-curate
    "транспортом харнесса",
    "kb-curate",
    "status: active",
    "documents:[src/…]",
    "implemented_by",
    "`readme.md`-индекс папки",
    "запускай независимые области параллельно",
    # step 4 — check and report, writing belongs to init (decision 2)
    "проверь, что",
    "главный индекс",
    "итог проверки — в отчёт",
    "домен скилла",
    # step 5 — derived output, engine literals
    "python3 skills/kb-search/gitmark.py lint",
    "gitmark.py index",
    "gitmark.py map -o docs-map.html",
    # step 6 — report
    "покрытие kb до→после",
    "решения человека",
    # principle, word-for-word
    "md+git — источник истины",
    "производное (индекс, граф)",
    "перегенерируется",
    "не дублируй",
    "не спорили за файлы",
    # launch procedure — decision 4 and the run contract
    "[agents.curator]",
    ".agents/config.toml",
    "сверь модель и уровень",
    "каталогом моделей",
    "расхождение — стоп",
    "названный пробел и стоп",
    "не угадывание",
    "fan-out `subagent`",
    "`workflow` не используется",
    "пишет только внутри",
    "строку на область — куратор, файлы, отказ",
    # read-back of the run card against the worktree fact (live proof
    # dwfrun-5efcd1d0: an unverified card reported empty files)
    "сверь карточку с фактом",
    "git diff --cached --name-only",
    "пустой `files` при непустом diff — расхождение",
    "лишний `files` — тоже",
    # bundle references carry the harness procedures (bundle-references
    # ticket 01): the run procedure from the owner bundle, the divergence
    # rule from the testing bundle, each with the guard phrase
    "references/ontodoc-run.md",
    "../testing/references/quality-rule.md",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/ontodoc-run.md`",
    "проект переопределяет его документом `docs/reference/quality-rule.md`",
    "написал свой, бери его",
)
FORBIDDEN_PHRASES = (
    "$arguments",
    "${claude_plugin_root}",
    "(task)",
    "surveyor",
    "файл проекта — первоисточник",
    "единственный источник",
    # Claude never enters the contour: the entry file is AGENTS.md alone
    # (operator decision, continue.md).
    "claude.md",
)
# .zcode is back on the ban list: the marketplace-plugin channel and the
# ZCode rails left the project (operator decision, continue.md).
FORBIDDEN_ROOTS = (".dsh", ".zcode", ".qoder")

# DSH run procedure (dsh-adaptation ticket 03, amended by the ZCode purge):
# the branch in SKILL.md and the section in the run reference; the ZCode
# section is gone — its return reddens the contract.
RUN_REFERENCE = REPO / "skills" / "onto-doc" / "references" / "ontodoc-run.md"
DSH_RUN_HEADING = "## dsh — прогон онто-дока"
DSH_SKILL_PHRASES = (
    "fan-out `subagent`",
    "spawn, не `subagent_fork`",
    "в одном сообщении",
    "`provider`, `model` и `reasoning_effort` из `[agents.curator]`",
    "`workflow` не используется",
    "только json-строку с полями `path`, `curator`, `files` и `refusal`",
    "не по схеме",
    "путь относительный, без `..` и без начального `/`",
    "области не повторяются",
    "пустой план — стоп",
    "прогон пишет только внутри `root`",
    "лишний `files`",
)
DSH_RUN_PHRASES = (
    "`<provider>/<model>`, ключ `level` — `reasoning_effort`",
    "с явными `provider`, `model` и `reasoning_effort`",
    "`subagent` (spawn, не `subagent_fork`)",
    "в одном сообщении",
    "`workflow` не используется",
    "`list_subagent_models`",
    "`path` — относительный путь от корня kb",
    "`cwd` субагента — чекаут сессии",
    "запись мимо `root` сверяй по `git status`",
    "без `..`",
    "без начального `/`",
    "не повторяются",
    "пустой план — стоп",
    "только внутри `root`",
    "kb-curate",
    "только json-строка",
    "с полями `path` (путь области)",
    "`files` (созданные или обновлённые файлы от корня",
    "`refusal`",
    "не по схеме",
    "git diff --cached --name-only",
    "лишний `files`",
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


def _step_titles(body: str) -> list[str]:
    """Titles of the numbered bold steps inside the «Шаги» section, in order."""
    lines = body.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Шаги")
    except StopIteration:
        return []
    end = next(
        (i for i, line in enumerate(lines[start + 1:], start + 1)
         if line.startswith("## ")),
        len(lines),
    )
    titles = []
    for line in lines[start + 1:end]:
        match = re.match(r"^\d+\. \*\*(.+?)\*\*", line)
        if match:
            titles.append(_normalized_lower(match.group(1)).strip())
    return titles


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
    lowered_description = _normalized_lower(description)
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
    for trigger in TRIGGERS:
        if trigger not in lowered_description:
            errors.append(f"description: missing trigger {trigger!r}")
    if "лёгкий путь kb-curate" not in lowered_description:
        errors.append("description: missing kb-curate boundary «лёгкий путь»")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            errors.append(f"forbidden phrase {phrase!r}")
    if _step_titles(body) != list(STEP_TITLES):
        errors.append(f"steps: expected six original steps in order, got "
                      f"{_step_titles(body)!r}")
    for root in FORBIDDEN_ROOTS:
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    # The single installer root of the engine is named.
    if ".agents/skills/kb-search/gitmark.py" not in text:
        errors.append("body: missing engine path for the channel root")
    return errors


def _dsh_run_section(text: str) -> str:
    """Slice the DSH run section; empty when its heading is absent.

    The slice ends at the next `##` heading, so a phrase that survives only in
    the ZCode or Qoder section does not satisfy the DSH contract. The text is
    whitespace-normalized, like the rest of the contract checks.
    """
    lowered = _normalized_lower(text)
    start = lowered.find(DSH_RUN_HEADING)
    if start == -1:
        return ""
    end = lowered.find(" ## ", start + 1)
    return lowered[start:end if end != -1 else len(lowered)]


def _dsh_run_errors(text: str) -> list[str]:
    """Return every violated DSH run contract; empty means the file is sound.

    spec: docs/plans/dsh-adaptation.md#готово — DSH-прогон онто-дока: fan-out
    `subagent` (spawn, не `subagent_fork`) с маршрутом и уровнем куратора из
    `[agents.curator]`, все кураторы в одном сообщении, JSON-строка на
    область с четырьмя полями, проверки плана и корня, сверка с diff;
    ZCode-раздел сохранён, старая строка «DSH и Qoder — вне плана» заменена
    Qoder-пробелом.
    """
    lowered = _normalized_lower(text)
    errors: list[str] = []
    section = _dsh_run_section(text)
    if not section:
        errors.append(f"dsh-run: missing section {DSH_RUN_HEADING!r}")
    else:
        for phrase in DSH_RUN_PHRASES:
            if phrase not in section:
                errors.append(f"dsh-run: DSH section lost {phrase!r}")
    if "dsh и qoder — вне плана" in lowered:
        errors.append("dsh-run: the retired «DSH и Qoder — вне плана» line is back")
    if "qoder" not in lowered:
        errors.append("dsh-run: the Qoder gap is not named")
    if "zcode" in lowered:
        errors.append("dsh-run: a ZCode procedure section is back")
    return errors


def _dsh_skill_errors(text: str) -> list[str]:
    """Return every violated DSH branch of the skill body; empty is sound.

    spec: docs/plans/dsh-adaptation.md#готово — DSH-ветка в SKILL.md: запуск
    идёт через `subagent`, не через `workflow`; план и корень проверяет
    родитель, ответ куратора — JSON-строка, ответ не по схеме — именованный
    отказ.
    """
    errors: list[str] = []
    lowered = _normalized_lower(_parse(text)[1])
    for phrase in DSH_SKILL_PHRASES:
        if phrase not in lowered:
            errors.append(f"dsh-skill: DSH branch lost {phrase!r}")
    if "dsh и qoder — вне плана" in lowered:
        errors.append("dsh-skill: the retired «DSH и Qoder — вне плана» line is back")
    return errors


def test_dsh_run_procedure_is_named():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 5: DSH-процедура
    прогона в references/ontodoc-run.md; ZCode-раздел сохранён, старая строка
    «DSH и Qoder — вне плана» заменена Qoder-пробелом (спека, техническое
    следствие 5)."""
    assert RUN_REFERENCE.is_file(), "the onto-doc run reference is missing"
    assert _dsh_run_errors(RUN_REFERENCE.read_text("utf-8")) == []


def test_dsh_skill_branch_is_named():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 5: DSH-ветка в
    SKILL.md — fan-out `subagent`, маршрут и уровень из `[agents.curator]`,
    JSON-строка на область, проверки плана и корня."""
    assert _dsh_skill_errors(SKILL.read_text("utf-8")) == []


def test_dsh_run_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the DSH run contract rejects a lost section, a lost spawn, a lost route
    binding, a lost one-message dispatch, a lost plan guard (relative path,
    no `..`, no leading `/`), a lost JSON schema field, a lost off-schema
    refusal, a lost staged-diff check, a lost extra-files half, a
    resurrected «DSH и Qoder — вне плана» line and a lost ZCode section."""
    text = RUN_REFERENCE.read_text("utf-8")
    assert _dsh_run_errors(text) == []

    no_heading = text.replace(DSH_RUN_HEADING, "## dsh — вне плана", 1)
    assert no_heading != text
    assert any("missing section" in error for error in _dsh_run_errors(no_heading))

    no_spawn = _drop_phrase(text, "`subagent` (spawn, не `subagent_fork`)")
    assert no_spawn != text
    assert any("spawn, не `subagent_fork`" in error
               for error in _dsh_run_errors(no_spawn))

    no_route = _drop_phrase(
        text, "`<provider>/<model>`, ключ `level` — `reasoning_effort`")
    assert no_route != text
    assert any("`<provider>/<model>`, ключ `level`" in error
               for error in _dsh_run_errors(no_route))

    no_args = _drop_phrase(
        text, "с явными `provider`, `model` и `reasoning_effort`")
    assert no_args != text
    assert any("с явными `provider`, `model` и `reasoning_effort`" in error
               for error in _dsh_run_errors(no_args))

    no_single = _drop_phrase(text, "в одном сообщении")
    assert no_single != text
    assert any("в одном сообщении" in error for error in _dsh_run_errors(no_single))

    no_plan = _drop_phrase(text, "без `..`")
    assert no_plan != text
    assert any("без `..`" in error for error in _dsh_run_errors(no_plan))

    no_slash = _drop_phrase(text, "без начального `/`")
    assert no_slash != text
    assert any("без начального `/`" in error for error in _dsh_run_errors(no_slash))

    no_cwd = _drop_phrase(text, "`cwd` субагента — чекаут сессии")
    assert no_cwd != text
    assert any("`cwd` субагента — чекаут сессии" in error
               for error in _dsh_run_errors(no_cwd))

    no_json = _drop_phrase(text, "только JSON-строка")
    assert no_json != text
    assert any("только json-строка" in error for error in _dsh_run_errors(no_json))

    no_path = _drop_phrase(text, "с полями `path` (путь области)")
    assert no_path != text
    assert any("с полями `path` (путь области)" in error
               for error in _dsh_run_errors(no_path))

    no_files = _drop_phrase(
        text, "`files` (созданные или обновлённые файлы от корня")
    assert no_files != text
    assert any("`files` (созданные или обновлённые файлы" in error
               for error in _dsh_run_errors(no_files))

    no_field = text.replace("`refusal` (причина отказа", "`reason` (причина отказа", 1)
    assert no_field != text
    assert any("`refusal`" in error for error in _dsh_run_errors(no_field))

    no_schema = _drop_phrase(text, "не по схеме")
    assert no_schema != text
    assert any("не по схеме" in error for error in _dsh_run_errors(no_schema))

    no_diff = _drop_phrase(text, "git diff --cached --name-only")
    assert no_diff != text
    assert any("git diff --cached --name-only" in error
               for error in _dsh_run_errors(no_diff))

    no_extra = _drop_phrase(text, "лишний `files`")
    assert no_extra != text
    assert any("лишний `files`" in error for error in _dsh_run_errors(no_extra))

    no_qoder = text.replace("Qoder", "другой харнесс")
    assert no_qoder != text
    assert any("Qoder" in error for error in _dsh_run_errors(no_qoder))

    resurrected = text.replace("## Qoder — вне плана",
                               "## DSH и Qoder — вне плана", 1)
    assert resurrected != text
    assert any("DSH и Qoder" in error for error in _dsh_run_errors(resurrected))

    zcode_back = text + "\n## zcode — прогон онто-дока\n\nПрогон через сохранённый workflow.\n"
    assert any("ZCode procedure section is back" in error
               for error in _dsh_run_errors(zcode_back))


def test_dsh_skill_branch_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the DSH branch rejects a lost spawn, a lost single message, a lost route
    source (`[agents.curator]` bound to `reasoning_effort`), a lost workflow
    reason, a lost JSON row, a lost off-schema refusal, a lost plan guard, a
    lost root bound, a lost extra-files half and a resurrected
    «DSH и Qoder — вне плана» line."""
    text = SKILL.read_text("utf-8")
    assert _dsh_skill_errors(text) == []

    no_fanout = _drop_phrase(text, "fan-out `subagent`")
    assert no_fanout != text
    assert any("fan-out `subagent`" in error
               for error in _dsh_skill_errors(no_fanout))

    no_spawn = _drop_phrase(text, "spawn, не `subagent_fork`")
    assert no_spawn != text
    assert any("spawn, не `subagent_fork`" in error
               for error in _dsh_skill_errors(no_spawn))

    no_single = _drop_phrase(text, "в одном сообщении")
    assert no_single != text
    assert any("в одном сообщении" in error for error in _dsh_skill_errors(no_single))

    no_route = _drop_phrase(text, "`reasoning_effort` из `[agents.curator]`")
    assert no_route != text
    assert any("`reasoning_effort` из `[agents.curator]`" in error
               for error in _dsh_skill_errors(no_route))

    no_reason = _drop_phrase(text, "`workflow` не используется")
    assert no_reason != text
    assert any("`workflow` не используется" in error
               for error in _dsh_skill_errors(no_reason))

    no_json = _drop_phrase(text, "только json-строку с полями")
    assert no_json != text
    assert any("только json-строку с полями" in error
               for error in _dsh_skill_errors(no_json))

    no_schema = _drop_phrase(text, "не по схеме")
    assert no_schema != text
    assert any("не по схеме" in error for error in _dsh_skill_errors(no_schema))

    no_plan = _drop_phrase(text, "путь относительный, без `..`")
    assert no_plan != text
    assert any("путь относительный, без `..`" in error
               for error in _dsh_skill_errors(no_plan))

    no_slash = _drop_phrase(text, "без начального `/`")
    assert no_slash != text
    assert any("без начального `/`" in error
               for error in _dsh_skill_errors(no_slash))

    no_root = _drop_phrase(text, "прогон пишет только внутри `root`")
    assert no_root != text
    assert any("прогон пишет только внутри `root`" in error
               for error in _dsh_skill_errors(no_root))

    no_extra = _drop_phrase(text, "лишний `files`")
    assert no_extra != text
    assert any("лишний `files`" in error for error in _dsh_skill_errors(no_extra))

    resurrected = text.replace("## Запуск прогона",
                               "## Запуск прогона: DSH и Qoder — вне плана", 1)
    assert resurrected != text
    assert any("DSH и Qoder" in error for error in _dsh_skill_errors(resurrected))


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/onto-doc.md#готово — skills/onto-doc/SKILL.md."""
    assert SKILL.is_file(), "the onto-doc skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "onto-doc"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_description_carries_triggers_and_the_kb_curate_boundary():
    """spec: docs/plans/onto-doc.md#готово — описание несёт триггеры («онто-док»,
    «погони онто-док», «бутстрап KB», «пересбор KB») и границу с kb-curate:
    одна статья — лёгкий путь."""
    fields, _ = _parse(SKILL.read_text("utf-8"))
    description = _normalized_lower(_unquote(fields["description"]))
    for trigger in TRIGGERS:
        assert trigger in description, f"trigger {trigger!r} is missing"
    assert "лёгкий путь kb-curate" in description

    text = SKILL.read_text("utf-8")
    for trigger in TRIGGERS:
        stripped = _drop_phrase(text, trigger)
        assert any(f"trigger '{trigger}'" in error
                   for error in _contract_errors(stripped))


def test_six_steps_of_the_original_in_the_original_order():
    """spec: docs/plans/onto-doc.md#ограничения — шаги 1–6 оригинала
    сохраняются в порядке оригинала; потеря шага и перестановка краснят."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    assert _step_titles(body) == list(STEP_TITLES)

    text = SKILL.read_text("utf-8")
    no_last_step = "\n".join(
        line for line in text.splitlines() if not line.startswith("6. **Отчёт**"))
    assert no_last_step != text
    assert any("expected six original steps" in error
               for error in _contract_errors(no_last_step))

    swapped = text.replace("2. **Разбей на док-области**",
                           "2. **Запусти кураторов (fan-out)**", 1)
    swapped = swapped.replace("3. **Запусти кураторов (fan-out)**",
                              "3. **Разбей на док-области**", 1)
    assert swapped != text
    assert any("expected six original steps" in error
               for error in _contract_errors(swapped))


def _drop_phrase(text: str, phrase: str) -> str:
    """Remove every occurrence of a phrase regardless of case and internal
    line wrapping (runs of whitespace inside the phrase match any run)."""
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def test_adaptations_are_limited_to_decision_two():
    """spec: docs/plans/onto-doc.md#решения-план-гейта — адаптации только из
    списка решения 2: движок по пути репозитория, Task → транспорт харнесса,
    запись точки входа — домен init; потеря пункта и возврат убранного
    `$ARGUMENTS` краснят."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_transport = text.replace("транспортом харнесса", "субагентом", 1)
    assert no_transport != text
    assert any("транспортом харнесса" in error
               for error in _contract_errors(no_transport))

    no_init_domain = text.replace("домен скилла", "задача исполнителя", 1)
    assert no_init_domain != text
    assert any("домен скилла" in error
               for error in _contract_errors(no_init_domain))

    arguments_back = text + "\nОбласть работы: `$ARGUMENTS`.\n"
    assert any("$arguments" in error
               for error in _contract_errors(arguments_back))

    plugin_root_back = text.replace(
        "python3 skills/kb-search/gitmark.py stat",
        "python3 ${CLAUDE_PLUGIN_ROOT}/skills/kb-search/gitmark.py stat", 1)
    assert any("${claude_plugin_root}" in error
               for error in _contract_errors(plugin_root_back))

    claude_md_back = text.replace(
        "проверь, что `AGENTS.md` существует как",
        "проверь, что `CLAUDE.md` / `AGENTS.md` существует как", 1)
    assert claude_md_back != text
    assert any("claude.md" in error
               for error in _contract_errors(claude_md_back))

    task_back = text + "\nСпавни куратора командой (Task).\n"
    assert any("(task)" in error for error in _contract_errors(task_back))

    surveyor_back = text + "\nЗаведи отдельную роль surveyor для обследования.\n"
    assert any("surveyor" in error for error in _contract_errors(surveyor_back))

    write_entry = text.replace(
        "запись точки входа —\n   домен скилла `init`",
        "запиши точку входа", 1)
    assert write_entry != text
    assert any("домен скилла" in error
               for error in _contract_errors(write_entry))


def test_launch_procedure_verifies_model_and_level():
    """spec: docs/plans/onto-doc.md#готово — сверка model+level с каталогом
    моделей: расхождение — стоп, каталога нет — названный пробел и стоп;
    запуск — fan-out `subagent` с маршрутом куратора, путь — справочник
    прогона в бандле onto-doc; чтение отчёта и lint+index+map в сессии
    (решения 4 и 8; транспорт ZCode снят с чисткой рельсов)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "сверь модель и уровень" in lowered
    assert "расхождение — стоп" in lowered
    assert "названный пробел и стоп" in lowered
    assert "не угадывание" in lowered
    assert "fan-out `subagent`" in lowered
    assert "`workflow` не используется" in lowered
    assert "строку на область — куратор, файлы, отказ" in lowered
    assert "python3 skills/kb-search/gitmark.py lint" in lowered
    assert "gitmark.py index" in lowered
    assert "gitmark.py map -o docs-map.html" in lowered


def test_launch_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    launch contract rejects a lost verification, a lost stop, a lost named-gap
    rule and a lost root write bound."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_verify = text.replace("Сверь модель и уровень", "Сверь модель", 1)
    assert no_verify != text
    assert any("сверь модель и уровень" in error
               for error in _contract_errors(no_verify))

    no_stop = text.replace("Расхождение — стоп.", "Расхождение — предупреждение.", 1)
    assert no_stop != text
    assert any("расхождение — стоп" in error
               for error in _contract_errors(no_stop))

    no_gap = text.replace("названный пробел и стоп", "пробел назви и продолжай", 1)
    assert no_gap != text
    assert any("названный пробел и стоп" in error
               for error in _contract_errors(no_gap))

    no_bound = text.replace("пишет только внутри", "пишет внутри", 1)
    assert no_bound != text
    assert any("пишет только внутри" in error
               for error in _contract_errors(no_bound))

    body = _parse(text)[1]
    flat = re.sub(r"\s+", " ", body)

    inverted_flat = flat.replace("Файл бандла — первоисточник",
                                 "Файл проекта — первоисточник", 1)
    assert inverted_flat != flat
    inverted = text.replace(body, inverted_flat, 1)
    assert any("файл проекта — первоисточник" in error
               for error in _contract_errors(inverted))

    only_flat = flat.replace("Файл бандла — первоисточник",
                             "Файл бандла — единственный источник", 1)
    assert only_flat != flat
    only_source = text.replace(body, only_flat, 1)
    assert any("единственный источник" in error
               for error in _contract_errors(only_source))

    no_rule = text.replace("../testing/references/quality-rule.md",
                           "../testing/references/absent-rule.md")
    assert no_rule != text
    assert any("../testing/references/quality-rule.md" in error
               for error in _contract_errors(no_rule))


def test_principle_is_word_for_word():
    """spec: docs/plans/onto-doc.md#ограничения — принцип оригинала сохраняется
    дословно: производное перегенерируется, дубликатов нет, кураторы в своих
    областях."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "md+git — источник истины" in lowered
    assert "производное (индекс, граф)" in lowered
    assert "перегенерируется" in lowered
    assert "не дублируй" in lowered
    assert "не спорили за файлы" in lowered

    text = SKILL.read_text("utf-8")
    no_regen = text.replace("перегенерируется", "хранится в git", 1)
    assert no_regen != text
    assert any("перегенерируется" in error
               for error in _contract_errors(no_regen))


@pytest.mark.parametrize(
    "needle",
    [
        "python3 skills/kb-search/gitmark.py stat",
        "транспортом харнесса",
        "documents:[src/…]",
        "implemented_by",
        "запускай независимые области параллельно",
        "проверь, что",
        "главный индекс",
        "итог проверки — в отчёт",
        "покрытие kb до→после",
        "расхождение — стоп",
        "названный пробел и стоп",
        "fan-out `subagent`",
        "`workflow` не используется",
        "строку на область — куратор, файлы, отказ",
        "сверь карточку с фактом",
        "git diff --cached --name-only",
        "пустой `files` при непустом diff — расхождение",
        "references/ontodoc-run.md",
        "../testing/references/quality-rule.md",
        "файл бандла — первоисточник",
        "написал свой, бери его",
        "проект переопределяет его документом `docs/reference/ontodoc-run.md`",
        "проект переопределяет его документом `docs/reference/quality-rule.md`",
    ],
)
def test_every_short_marker_has_a_failing_probe(needle: str) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any required phrase, however short, reddens the contract."""
    text = SKILL.read_text("utf-8")
    mutated = _drop_phrase(text, needle)
    assert mutated != text, f"the mutation must remove {needle!r}"
    errors = _contract_errors(mutated)
    assert any(f"missing required phrase '{needle}'" in error for error in errors), errors


def test_no_forbidden_harness_root():
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific
    skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    for root in FORBIDDEN_ROOTS:
        assert root not in text
        leaked = text + f"\nInstall into {root}/skills instead.\n"
        assert any(root in error for error in _contract_errors(leaked))
