"""Contract for the init skill and the managed block it writes.

The skill is prose: its "code" is the text an agent follows. These checks pin the
shipped artifact — the DSH frontmatter, the three files init owns (AGENTS.md,
.gitignore and the role registry .agents/config.toml), the marker cases, the
verbatim block and the bootstrap contract — and prove the check can fail
(mutation probe).

spec: docs/plans/harness-agnostic.md#готово — skills/init/SKILL.md, the managed block,
      .gitignore (four lines), harness-neutral prose
spec: docs/plans/review-config.md#готово — init спрашивает модели ролей ядра
      ask-ом, пишет .agents/config.toml и запускает генератор из бандла
spec: docs/plans/onto-doc.md#готово — init спрашивает куратора шестым вопросом:
      рекомендация — дефолт решения 3 по правилу отклонения решения 9, уровень —
      максимум из доступных, без уровней ключ опускается
invariant: docs/plans/workflow-skills.md#ограничения — no registry, provenance, Reel or
      acceptance chord
invariant: docs/plans/harness-agnostic.md#готово — no harness root named
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "init" / "SKILL.md"
BEGIN = "<!-- BEGIN ontoship -->"
END = "<!-- END ontoship -->"
GITIGNORE_LINES = (".gitmark/", "*-map.html", ".scratch/", ".agents/skills/")
CORE_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb", "critic",
              "curator")
GENERATOR_PATH = ".agents/skills/init/gen_agents.py"
CURATOR_DEFAULT = "account:zai-individual-coding-plan/GLM-5.3-Flash"
BOOTSTRAP_NEEDLES = (
    "Три файла, ничего больше",
    ".agents/config.toml",
    "назови пробел и остановись",
    "активные модели",
    "модель сессии",
    "отказ с объяснением",
    "пропуск",
    "не дописывай",
    "не трогай",
    GENERATOR_PATH,
    "Сверь шесть ролей ядра",
    "`critic`, `curator` — с секциями конфига",
    "Шестой вопрос — модель роли `curator`",
    CURATOR_DEFAULT,
    "пока она в списке активных",
    "назови отклонение от дефолта",
    "максимум из доступных уровней выбранной модели",
    "тот же список активных моделей шага 1",
    "У модели без уровней ключ `level` опусти",
) + CORE_ROLES
FORBIDDEN = ("registry", "provenance", "reel", "acceptance chord", "inventory",
             "serve", ".dsh", ".zcode", ".qoder", "commands.md")
# review-loose-ends: the registry wording must stay neutral to role growth, so
# the two old wordings are forbidden anywhere in the skill, in any case.
FORBIDDEN_WORDINGS = ("реестр ролей ревью", "бутстрап ролей ревью")

# The block from the spec, pinned independently of the skill text: the expected value
# is this literal, not a re-extraction of the implementation.
BLOCK = """\
<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `.agents/skills/kb-search/gitmark.py` для прямого запуска.
- Новые или обновлённые документы: загрузи скилл `kb-curate` — сначала поиск, никогда
  не дублируй.
- Сопровождение после правки документов:

  ```sh
  python3 .agents/skills/kb-search/gitmark.py index
  python3 .agents/skills/kb-search/gitmark.py lint --strict
  python3 .agents/skills/kb-search/gitmark.py map -o docs-map.html
  ```

- KB — это markdown + git: `.gitmark/`, `*-map.html` и `.scratch/` производные или
  эфемерные — никогда не коммитятся.
<!-- END ontoship -->
"""

BLOCK_FENCE = re.compile(
    r"^````[^\n]*\n(<!-- BEGIN ontoship -->\n.*?^<!-- END ontoship -->\n)^````$",
    re.MULTILINE | re.DOTALL,
)


def _parse_skill(text: str) -> tuple[dict[str, str], str]:
    """Parse the single-line YAML frontmatter the skill uses."""
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
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _block(text: str) -> str:
    """The four-backtick fenced block carrying the two markers, or a failure."""
    matches = BLOCK_FENCE.findall(text)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one fenced ontoship block, got {len(matches)}")
    return matches[0]


def _standalone_lines(text: str) -> list[str]:
    """Lines that are exactly a .gitignore rule, not prose mentioning one."""
    return [line for line in text.splitlines() if line in GITIGNORE_LINES]


def _mentions(text: str, term: str) -> bool:
    """Word-boundary match for words; plain substring for paths such as `.zcode`."""
    lowered = text.lower()
    if term[0].isalnum() and term[-1].isalnum():
        return re.search(rf"\b{re.escape(term)}\b", lowered) is not None
    return term in lowered


def _contract_errors(text: str) -> list[str]:
    """Every violated init contract; empty means the skill is sound."""
    try:
        fields, body = _parse_skill(text)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    if fields.get("name") != "init":
        errors.append("frontmatter: name must be init")
    raw_description = fields.get("description", "")
    description = _unquote(raw_description)
    if not description:
        errors.append("frontmatter: missing description")
    elif len(description) > 500:
        errors.append(f"frontmatter: description is {len(description)} chars "
                      "(catalog cap 500)")
    if ": " in description and not (raw_description.startswith('"')
                                    and raw_description.endswith('"')):
        errors.append("frontmatter: description contains ': ' and must be quoted")

    for needle in ("AGENTS.md", ".gitignore", BEGIN, END, "docs/README.md",
                   "kb-search", "kb-curate", "gitmark.py index",
                   "gitmark.py lint --strict", "gitmark.py map -o docs-map.html",
                   ".agents/skills/", "идемпотент", "вне маркеров", "одну пустую строку",
                   "уже актуален", "замени только внутренний текст",
                   "[WARN]", "[FAIL]"):
        if needle not in body:
            errors.append(f"body: missing {needle!r}")

    for needle in BOOTSTRAP_NEEDLES:
        if needle not in body:
            errors.append(f"bootstrap: missing {needle!r}")

    for term in FORBIDDEN:
        if _mentions(text, term):
            errors.append(f"forbidden entity {term!r}")

    # Whitespace is flattened first: the skill prose wraps at 80 columns, so a
    # wording returned across a line break must still redden (panel probe).
    flattened = re.sub(r"\s+", " ", text.lower())
    for phrase in FORBIDDEN_WORDINGS:
        if phrase in flattened:
            errors.append(f"forbidden wording {phrase!r}")

    try:
        block = _block(text)
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if block != BLOCK:
            errors.append("block: the fenced ontoship block is not the verbatim template")
        for marker in (BEGIN, END):
            if block.count(marker) != 1:
                errors.append(f"block: expected exactly one {marker!r}")

    for line in GITIGNORE_LINES:
        if _standalone_lines(text).count(line) != 1:
            errors.append(f"body: expected exactly one standalone {line!r} rule")

    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/core-kb.md#рамки — skills/init/SKILL.md."""
    assert SKILL.is_file(), "the init skill is missing"
    assert SKILL.parent.name == "init", "bundle directory must match the skill name"
    text = SKILL.read_text("utf-8")
    fields, _ = _parse_skill(text)
    assert fields["name"] == "init"
    assert 3 <= len(_unquote(fields["description"])) <= 500
    assert _contract_errors(text) == []


def test_block_is_verbatim_and_has_one_marker_pair():
    """spec: docs/plans/harness-agnostic.md#готово — the managed block, `<!-- BEGIN ontoship -->` … `<!-- END … -->`."""
    text = SKILL.read_text("utf-8")
    assert _block(text) == BLOCK
    # The prose marker, the template and the verification grep each name the pair once.
    assert text.count(BEGIN) == text.count(END) == 3


def test_gitignore_lines_are_the_four_the_kb_requires():
    """spec: docs/plans/harness-agnostic.md#готово — `.gitmark/`, `*-map.html`, `.scratch/`, `.agents/skills/`."""
    lines = _standalone_lines(SKILL.read_text("utf-8"))
    assert lines == list(GITIGNORE_LINES)


def test_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a missing marker, line, name or a leaked entity."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_end = text.replace(f"\n{END}\n", "\n", 1)
    assert missing_end != text
    assert any("fenced ontoship block" in error for error in _contract_errors(missing_end))

    missing_rule = text.replace("\n*-map.html\n", "\n*-map.html.bak\n", 1)
    assert missing_rule != text
    assert any("*-map.html" in error for error in _contract_errors(missing_rule))

    leaked_entity = text + "\nCreate the docs/reference/commands.md registry.\n"
    assert any("registry" in error for error in _contract_errors(leaked_entity))

    leaked_install_root = text + "\nInstall into .zcode/skills instead.\n"
    assert any(".zcode" in error for error in _contract_errors(leaked_install_root))

    leaked_legacy_root = text + "\nKeep the old .dsh/skills link.\n"
    assert any(".dsh" in error for error in _contract_errors(leaked_legacy_root))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert any("name" in error for error in _contract_errors(missing_name))

    unquoted_description = "\n".join(
        "description: " + _unquote(line[len('description: "'):-1])
        if line.startswith('description: "') else line
        for line in text.splitlines())
    assert unquoted_description != text
    assert any("must be quoted" in error
               for error in _contract_errors(unquoted_description))

    edited_block = text.replace("## База знаний (OntoShip)",
                                "## База знаний (изменено)", 1)
    assert any("verbatim" in error for error in _contract_errors(edited_block))


def test_init_owns_the_role_registry_as_a_third_file():
    """spec: docs/plans/review-config.md#готово — контракт «два файла» расширен до трёх:
    AGENTS.md, .gitignore, .agents/config.toml."""
    text = SKILL.read_text("utf-8")
    assert "Три файла, ничего больше" in text
    assert ".agents/config.toml" in text


def test_bootstrap_asks_core_role_models_from_active_host_models():
    """spec: docs/plans/review-config.md#готово — вопрос по ролям текущей версии
    ядра, выбор из доступных моделей хоста."""
    text = SKILL.read_text("utf-8")
    for role in CORE_ROLES:
        assert role in text, f"core role {role} is not named"
    assert "ask" in text
    assert "активные модели" in text


def test_critic_model_must_differ_from_the_session_model():
    """spec: docs/plans/review-config.md#готово — для critic совпадение выбранной
    модели с сессионной — отказ с объяснением."""
    text = SKILL.read_text("utf-8")
    assert "обязана отличаться от модели сессии" in text
    assert "отказ с объяснением" in text


def test_existing_config_is_untouched_and_a_new_role_is_a_named_gap():
    """spec: docs/plans/review-config.md#ограничения — новая роль ядра при
    существующем конфиге: названный пропуск, без молчаливой дописки."""
    text = SKILL.read_text("utf-8")
    assert "не трогай" in text
    assert "пропуск" in text
    assert "не дописывай" in text


def test_no_model_source_stops_with_a_named_gap():
    """spec: docs/plans/review-config.md#готово — деградация без источника
    моделей — названный пробел."""
    text = SKILL.read_text("utf-8")
    assert "назови пробел и остановись" in text


def test_bootstrap_runs_the_bundled_generator():
    """spec: docs/plans/review-config.md#готово — генерация определений доступна
    установленному проекту: бандл init несёт генератор (решение оператора
    2026-10-29)."""
    text = SKILL.read_text("utf-8")
    assert GENERATOR_PATH in text


def test_bootstrap_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    bootstrap contract rejects a lost registry, a lost core role, a lost refusal,
    a lost gap rule and a lost generator path."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_registry = text.replace(".agents/config.toml", ".agents/roles.toml")
    assert no_registry != text
    assert any(".agents/config.toml" in error for error in _contract_errors(no_registry))

    # "kritic" does not contain the needle, so the replacement really removes it.
    no_critic = text.replace("critic", "kritic")
    assert no_critic != text
    assert any("critic" in error for error in _contract_errors(no_critic))

    no_refusal = text.replace("отказ с объяснением и перевыбор", "перевыбор")
    assert no_refusal != text
    assert any("отказ с объяснением" in error for error in _contract_errors(no_refusal))

    no_gap = text.replace("назови пробел и остановись", "остановись")
    assert no_gap != text
    assert any("назови пробел и остановись" in error for error in _contract_errors(no_gap))

    no_generator = text.replace(GENERATOR_PATH, "gen.py")
    assert no_generator != text
    assert any(GENERATOR_PATH in error for error in _contract_errors(no_generator))


def test_curator_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    curator bootstrap rejects a lost sixth role (in the check list itself, not
    just any mention), a lost active-list guard, a lost deviation rule, a lost
    level rule and a lost level source (onto-doc solution 9 mutations)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_curator = text.replace("curator", "kurator")
    assert no_curator != text
    assert any("curator" in error for error in _contract_errors(no_curator))

    # The named mutation: the sixth role dropped from the check list itself.
    no_list = text.replace("`critic`, `curator` — с секциями", "`critic` — с секциями")
    assert no_list != text
    assert any("`critic`, `curator` — с секциями конфига" in error
               for error in _contract_errors(no_list))

    # Solution 9's guard: the default is recommended only while it is active.
    no_guard = text.replace(" пока она в списке активных", "")
    assert no_guard != text
    assert any("пока она в списке активных" in error for error in _contract_errors(no_guard))

    no_deviation = text.replace("и назови отклонение от дефолта.", "")
    assert no_deviation != text
    assert any("назови отклонение от дефолта" in error for error in _contract_errors(no_deviation))

    no_level = text.replace("максимум из доступных уровней выбранной модели",
                            "заданный конфигом уровень")
    assert no_level != text
    assert any("максимум из доступных уровней выбранной модели" in error
               for error in _contract_errors(no_level))

    no_source = text.replace("тот же список активных моделей шага 1",
                             "отдельный каталог уровней")
    assert no_source != text
    assert any("тот же список активных моделей шага 1" in error
               for error in _contract_errors(no_source))

    no_omit = text.replace("У модели без уровней ключ `level` опусти.", "")
    assert no_omit != text
    assert any("У модели без уровней ключ `level` опусти" in error
               for error in _contract_errors(no_omit))


def test_registry_wording_contract_can_fail():
    """invariant: docs/plans/review-loose-ends.md#готово — the wording contract
    rejects the old registry phrase and the old bootstrap heading brought back,
    each once and in any case."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    reverted_body = text.replace("реестр ролей:", "реестр ролей ревью:", 1)
    assert reverted_body != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(reverted_body))

    reverted_heading = text.replace("## 4. Бутстрап ролей\n",
                                    "## 4. Бутстрап ролей ревью\n")
    assert reverted_heading != text
    assert any("бутстрап ролей ревью" in error
               for error in _contract_errors(reverted_heading))

    # Case-insensitive: a capitalised return in the description is caught too.
    reverted_description = text.replace("реестр ролей .agents/config.toml",
                                        "Реестр ролей ревью .agents/config.toml")
    assert reverted_description != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(reverted_description))

    # A wording wrapped across a line break is caught too.
    wrapped_return = text.replace("реестр ролей:", "реестр ролей\n  ревью:", 1)
    assert wrapped_return != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(wrapped_return))
