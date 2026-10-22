"""Contract for the init skill and the managed block it writes.

The skill is prose: its "code" is the text an agent follows. These checks pin the
shipped artifact — the DSH frontmatter, the two files init owns, the marker cases and
the verbatim block — and prove the check can fail (mutation probe).

spec: docs/plans/harness-agnostic.md#готово — skills/init/SKILL.md, the managed block,
      .gitignore (four lines), harness-neutral prose
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
FORBIDDEN = ("registry", "provenance", "reel", "acceptance chord", "inventory",
             "serve", ".dsh", ".zcode", ".qoder", "commands.md")

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

    for term in FORBIDDEN:
        if _mentions(text, term):
            errors.append(f"forbidden entity {term!r}")

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