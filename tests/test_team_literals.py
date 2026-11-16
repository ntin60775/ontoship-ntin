"""Invariant: the core carries no team mechanisms in its skill texts.

spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3, критерий 4,
триаж G11: инвариант team-литералов — скан skills/**/SKILL.md,
skills/*/references/*.md и массива SKILLS установщика; литералы —
session_read, ontoshipExecutors, allowedAgentPresets, id пресетов команды
(architect, orchestrator, executor, scout). Коннектор ≠ зависимость:
называть team ссылкой-коннектором не запрещено (канон, «Границы») — скан
ловит механизмы и id пресетов, не имя бандла; область — скиллы, не весь
репо (история тикетов и спеки литералы несут легитимно).
invariant: docs/decisions/ontoship-core.md#границы — ядро функционально
самодостаточно: доводит тикет до main без team.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Team plugin services and the subagent allowlist key: exact literals.
TEAM_SERVICE_LITERALS = ("session_read", "ontoshipExecutors", "allowedAgentPresets")
# Team preset ids (cordis.patch.yml of ontoship-team): whole words, so a
# stack id like 1c-executor is caught too, while «architectural» is not.
TEAM_PRESET_IDS = ("architect", "orchestrator", "executor", "scout")
PRESET_RE = re.compile(r"\b(?:" + "|".join(TEAM_PRESET_IDS) + r")\b")
SKILLS_ARRAY_RE = re.compile(r"^readonly SKILLS=\(([^)]*)\)", re.MULTILINE)


def _scope(root: Path) -> list[Path]:
    """The named scan scope: every bundle SKILL.md (nested included) and
    every bundle references file."""
    return sorted(root.glob("skills/**/SKILL.md")) + \
        sorted(root.glob("skills/*/references/*.md"))


def _text_errors(rel: str, text: str) -> list[str]:
    errors: list[str] = []
    for literal in TEAM_SERVICE_LITERALS:
        if literal in text:
            errors.append(f"{rel}: team literal {literal!r}")
    for match in PRESET_RE.finditer(text):
        errors.append(f"{rel}: team preset id {match.group(0)!r}")
    return errors


def _scan(root: Path) -> list[str]:
    """Every team-literal violation in the named scope; empty is sound."""
    errors: list[str] = []
    for path in _scope(root):
        errors.extend(_text_errors(str(path.relative_to(root)),
                                   path.read_text("utf-8")))
    install = root / "scripts" / "install.sh"
    if install.is_file():
        match = SKILLS_ARRAY_RE.search(install.read_text("utf-8"))
        if match:
            errors.extend(_text_errors("scripts/install.sh SKILLS",
                                       match.group(1)))
    return errors


def test_core_skills_carry_no_team_literals() -> None:
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3,
    критерий 4: скиллы ядра и массив SKILLS не несут team-литералов;
    на базе краснеет — skills/chain нёс session_read, ontoshipExecutors,
    allowedAgentPresets и id пресетов."""
    assert _scan(REPO) == []


def test_scan_catches_seeded_literals(tmp_path: Path) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the scan can fail: every named literal planted into a SKILL.md, a
    references file or the SKILLS array reddens with its own name."""
    for literal in TEAM_SERVICE_LITERALS + TEAM_PRESET_IDS:
        skill = tmp_path / "skills" / "probe" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(f"# probe\n\nUse {literal} here.\n", "utf-8")
        errors = _scan(tmp_path)
        assert any(literal in error and "skills/probe/SKILL.md" in error
                   for error in errors), (literal, errors)
        skill.unlink()

        ref = tmp_path / "skills" / "probe" / "references" / "note.md"
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.write_text(f"note {literal}\n", "utf-8")
        errors = _scan(tmp_path)
        assert any(literal in error and "references/note.md" in error
                   for error in errors), (literal, errors)
        ref.unlink()

        install = tmp_path / "scripts" / "install.sh"
        install.parent.mkdir(parents=True, exist_ok=True)
        install.write_text(f"readonly SKILLS=(kb-search {literal})\n",
                           "utf-8")
        errors = _scan(tmp_path)
        assert any(literal in error and "SKILLS" in error
                   for error in errors), (literal, errors)
        install.unlink()


def test_scan_scope_covers_nested_bundles(tmp_path: Path) -> None:
    """invariant: docs/plans/core-team-boundaries.md#готово — триаж G11:
    the scope is skills/**/SKILL.md, not only the top level — a nested
    bundle SKILL.md carrying a literal is caught."""
    nested = tmp_path / "skills" / "outer" / "inner" / "SKILL.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("session_read\n", "utf-8")
    errors = _scan(tmp_path)
    assert any("skills/outer/inner/SKILL.md" in error for error in errors), \
        errors


def test_preset_ids_match_whole_words(tmp_path: Path) -> None:
    """invariant: docs/plans/core-team-boundaries.md#готово — the preset-id
    scan is whole-word: a stack id (1c-executor) is caught, an innocent
    word sharing the stem (architectural) is not — the guard must not
    redden legitimate prose."""
    skill = tmp_path / "skills" / "probe" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("architectural orchestrators execution scoutish\n",
                     "utf-8")
    assert _scan(tmp_path) == [], "innocent stems must not fire"
    skill.write_text("the 1c-executor preset\n", "utf-8")
    errors = _scan(tmp_path)
    assert any("executor" in error for error in errors), errors