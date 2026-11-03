"""Bundle references carry the method sections (bundle-references ticket 01).

The six v0.3.0 references to project KB carriers (``docs/reference/…``) are
switched to bundle files: the owner bundle's ``references/`` directory or a
neighbor bundle via the relative ``../<bundle>/references/<file>`` path.
Every referencing step carries the guard phrase — the bundle file is the
primary source, the project overrides it with
``docs/reference/<bundle file name>`` — and every relative markdown link
inside a bundle reference file resolves on disk. Bundle reference files
carry no ntin-repo paths: ``docs/plans/`` and ``skills/`` stay out.

spec: docs/plans/bundle-references.md#готово — references/ in the ship,
onto-doc and testing bundles; six links switched; files exist on disk
spec: docs/plans/bundle-references.md#рамки — bundle sections stand alone;
no repo paths (docs/plans/, skills/) inside reference files; the owner
layout names the three files
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

# The six v0.3.0 reference points: (skill, step marker, bundle reference,
# project override doc, reference phrase of this point). The marker slices
# the step's enclosing block; the phrase distinguishes two points sharing
# one block (ship names the bundle file twice in «Сборка панели»).
POINTS = (
    ("ship", "**Сборка панели.", "references/review-panel.md",
     "docs/reference/review-panel.md",
     "справочник `references/review-panel.md`"),
    ("ship", "процедура в том же", "references/review-panel.md",
     "docs/reference/review-panel.md",
     "процедура в том же `references/review-panel.md`"),
    ("onto-doc", "2. Запусти сохранённый workflow", "references/ontodoc-run.md",
     "docs/reference/ontodoc-run.md", "references/ontodoc-run.md"),
    ("onto-doc", "3. Прочитай отчёт прогона",
     "../testing/references/quality-rule.md", "docs/reference/quality-rule.md",
     "../testing/references/quality-rule.md"),
    ("testing", "Носитель правила качества канона", "references/quality-rule.md",
     "docs/reference/quality-rule.md", "references/quality-rule.md"),
    ("to-tickets", "- **Артефакт и ожидание**",
     "../testing/references/quality-rule.md", "docs/reference/quality-rule.md",
     "../testing/references/quality-rule.md"),
)

GUARD_SKILLS = ("ship", "onto-doc", "testing", "to-tickets")

# The three v0.3.0 project KB carriers; they must not survive as skill
# references. The guard's override docs (docs/reference/<bundle file>) are
# different names and stay.
OLD_CARRIERS = (
    "docs/reference/review-roles.md",
    "docs/reference/harnesses.md",
    "docs/reference/testing.md",
)

GUARD_HEAD = "файл бандла — первоисточник"
GUARD_TAIL = "написал свой, бери его"

# Blocks end at a blank line, the next bullet/numbered item or a heading.
BLOCK_BREAK = re.compile(r"\n(?=\n|[-*] |\d+\. |#)")

# Relative markdown links inside bundle reference files.
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Project carrier mentions inside a step block (the guard's override among
# them).
CARRIER_MENTION = re.compile(r"docs/reference/[\w.-]+\.md")


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _drop_phrase(text: str, phrase: str) -> str:
    """Remove every occurrence of a phrase regardless of case and internal
    line wrapping (runs of whitespace inside the phrase match any run)."""
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def _enclosing_block(text: str, marker: str) -> str:
    """The block around the marker: bullet/numbered item or paragraph,
    delimited by BLOCK_BREAK on both sides. Breaks are found over the full
    text and filtered by position: a lookahead at the search end must see
    the break that opens the next block."""
    start = text.index(marker)
    before = [m for m in BLOCK_BREAK.finditer(text) if m.start() < start]
    block_start = (before[-1].start() + 1) if before else 0
    after = BLOCK_BREAK.search(text, start)
    block_end = after.start() if after else len(text)
    return text[block_start:block_end].strip()


def _skill_texts(root: Path = SKILLS) -> dict[str, str]:
    """The four switched skill bodies, keyed by bundle name."""
    return {skill: (root / skill / "SKILL.md").read_text("utf-8")
            for skill in GUARD_SKILLS}


def _reference_errors(texts: dict[str, str], root: Path = SKILLS) -> list[str]:
    """Every violated bundle-reference fact; empty means the switch holds."""
    errors: list[str] = []
    for skill, marker, ref, override, phrase in POINTS:
        try:
            block = _normalized_lower(_enclosing_block(texts[skill], marker))
        except ValueError:
            errors.append(f"{skill}: step marker {marker!r} is missing")
            continue
        if phrase not in block:
            errors.append(f"{skill}: step {marker!r} lost the bundle "
                          f"reference {ref!r}")
        for mention in CARRIER_MENTION.findall(block):
            if mention != override:
                errors.append(f"{skill}: step {marker!r} names a non-guard "
                              f"project carrier {mention!r}")
        target = (root / skill / ref).resolve()
        if not target.is_relative_to(root.resolve()):
            errors.append(f"{skill}: bundle reference {ref!r} escapes the "
                          f"skill root")
        elif not target.is_file():
            errors.append(f"{skill}: bundle reference {ref!r} does not exist "
                          f"on disk")
    return errors


def _guard_errors(texts: dict[str, str]) -> list[str]:
    """Every referencing step must carry the full guard phrase."""
    errors: list[str] = []
    for skill, marker, _ref, override, _phrase in POINTS:
        try:
            block = _normalized_lower(_enclosing_block(texts[skill], marker))
        except ValueError:
            errors.append(f"{skill}: step marker {marker!r} is missing")
            continue
        for phrase in (GUARD_HEAD,
                       f"проект переопределяет его документом `{override}`",
                       GUARD_TAIL):
            if phrase not in block:
                errors.append(f"{skill}: step {marker!r} lost the guard "
                              f"phrase {phrase!r}")
    return errors


def _old_carrier_errors(texts: dict[str, str]) -> list[str]:
    """The v0.3.0 project KB carriers must be gone from the four skills."""
    errors: list[str] = []
    for skill, text in texts.items():
        lowered = _normalized_lower(text)
        for carrier in OLD_CARRIERS:
            if carrier in lowered:
                errors.append(f"{skill}: project carrier {carrier!r} "
                              f"still referenced")
    return errors


def reference_files(root: Path = SKILLS) -> list[Path]:
    """Every file under a bundle references/ directory."""
    return sorted(root.glob("*/references/*.md"))


def _link_errors(root: Path = SKILLS) -> list[str]:
    """Every relative markdown link inside a bundle reference file must
    resolve on disk."""
    errors: list[str] = []
    for path in reference_files(root):
        text = path.read_text("utf-8")
        for target in MD_LINK.findall(text):
            if re.match(r"(?:https?:|mailto:|#|/)", target):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{path.relative_to(root)}: dead link "
                              f"{target!r}")
    return errors


def _repo_path_errors(root: Path = SKILLS) -> list[str]:
    """Bundle reference files carry no ntin-repo paths."""
    errors: list[str] = []
    for path in reference_files(root):
        text = path.read_text("utf-8")
        for needle in ("docs/plans/", "skills/"):
            if needle in text:
                errors.append(f"{path.relative_to(root)}: repo path {needle!r}")
    return errors


def test_six_references_point_at_existing_bundle_files():
    """spec: docs/plans/bundle-references.md#готово — every switched step
    names its own reference phrase, points into its own or a neighbor
    bundle's references/, and the file exists on disk."""
    assert reference_files(), "no bundle references/ directories exist"
    errors = _reference_errors(_skill_texts())
    assert errors == [], "\n".join(errors)


def test_every_referencing_step_carries_the_guard():
    """spec: docs/plans/bundle-references.md#готово — guard phrase in every
    referencing step: bundle file is the primary source, the project
    overrides it with docs/reference/<bundle file name>."""
    errors = _guard_errors(_skill_texts())
    assert errors == [], "\n".join(errors)


def test_old_kb_carriers_left_the_skill_bodies():
    """spec: docs/plans/bundle-references.md#готово — none of the six
    switched references names a project docs/reference/ carrier anymore."""
    errors = _old_carrier_errors(_skill_texts())
    assert errors == [], "\n".join(errors)


def test_bundle_reference_links_resolve():
    """spec: docs/plans/bundle-references.md#готово — every relative link
    inside a bundle reference file resolves (cross-bundle neighbors
    included)."""
    assert reference_files(), "no bundle references/ directories exist"
    errors = _link_errors()
    assert errors == [], "\n".join(errors)


def test_bundle_files_carry_no_repo_paths():
    """spec: docs/plans/bundle-references.md#рамки — bundle sections stand
    alone: no docs/plans/ or skills/ paths inside reference files."""
    assert reference_files(), "no bundle references/ directories exist"
    errors = _repo_path_errors()
    assert errors == [], "\n".join(errors)


def test_reference_checks_can_fail(tmp_path: Path):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the checks redden on a lost reference phrase, a missing reference file,
    a lost guard phrase, a priority inversion, a stray project carrier, a
    renamed override doc, a dangling reference-file link and a repo path."""
    texts = _skill_texts()
    assert _reference_errors(texts) == []
    assert _guard_errors(texts) == []
    assert _old_carrier_errors(texts) == []
    assert _link_errors() == []
    assert _repo_path_errors() == []

    # The step-level switch branch: renaming every bundle path away in the
    # ship body loses both reference phrases (ship names the file twice in
    # one block, so the mutation must hit both mentions).
    copied = tmp_path / "copied" / "skills"
    copied.parent.mkdir()
    shutil.copytree(SKILLS, copied,
                    ignore=shutil.ignore_patterns("__pycache__"))
    dead = texts["ship"].replace("references/review-panel.md",
                                 "references/missing-panel.md")
    assert dead != texts["ship"], "the mutation must break the reference"
    (copied / "ship" / "SKILL.md").write_text(dead, "utf-8")
    errors = _reference_errors(_skill_texts(copied), copied)
    assert any("lost the bundle reference" in error for error in errors)

    # The disk-existence branch: the same tree with the reference file
    # removed reddens even though every step text still names it.
    (copied / "ship" / "SKILL.md").write_text(texts["ship"], "utf-8")
    (copied / "ship" / "references" / "review-panel.md").unlink()
    errors = _reference_errors(_skill_texts(copied), copied)
    assert any("does not exist on disk" in error for error in errors)

    # A stray project carrier inside a step block: any docs/reference/<name>
    # other than the guard's own override reddens the switch check.
    stray = texts["ship"].replace(
        "справочник `references/review-panel.md`",
        "справочник `references/review-panel.md` и матрицы "
        "`docs/reference/harnesses.md`", 1)
    assert stray != texts["ship"]
    errors = _reference_errors({**texts, "ship": stray})
    assert any("non-guard project carrier" in error for error in errors)

    stripped = _drop_phrase(texts["testing"], GUARD_HEAD)
    assert stripped != texts["testing"], "the mutation must remove the guard"
    assert any(GUARD_HEAD in error
               for error in _guard_errors({**texts, "testing": stripped}))

    inverted = texts["ship"].replace("Файл бандла — первоисточник",
                                     "Файл проекта — первоисточник", 1)
    assert inverted != texts["ship"]
    assert any(GUARD_HEAD in error
               for error in _guard_errors({**texts, "ship": inverted}))

    # The guard must live inside its step: moving it to the file tail keeps
    # the words but loses the block. Normalized body, so a reflow of the
    # носитель cannot silently no-op the mutation.
    flat = re.sub(r"\s+", " ", texts["testing"])
    relocated = flat.replace(
        "Файл бандла — первоисточник; проект переопределяет его документом",
        "", 1).rstrip() + (
        "\n\nФайл бандла — первоисточник; проект переопределяет его "
        "документом `docs/reference/quality-rule.md` — написал свой, "
        "бери его.")
    assert relocated != flat
    assert any(GUARD_HEAD in error
               for error in _guard_errors({**texts, "testing": relocated}))

    renamed = texts["ship"].replace("docs/reference/review-panel.md",
                                    "docs/reference/review-roles.md", 1)
    assert renamed != texts["ship"]
    errors = _reference_errors({**texts, "ship": renamed})
    assert any("non-guard project carrier" in error for error in errors)
    assert any("docs/reference/review-panel.md" in error
               for error in _guard_errors({**texts, "ship": renamed}))

    # The link and hygiene checks on an isolated fabricated tree, so the
    # probes above cannot pre-redden them.
    island = tmp_path / "island" / "skills"
    dangling = island / "demo" / "references"
    dangling.mkdir(parents=True)
    (dangling / "note.md").write_text(
        "[сосед](../../neighbor/references/absent.md)\n", "utf-8")
    assert any("dead link" in error for error in _link_errors(island))
    (dangling / "note.md").write_text(
        "Внутри живёт путь `skills/README.md`.\n", "utf-8")
    assert any("skills/" in error for error in _repo_path_errors(island))


def test_reference_escape_branch_can_fail(tmp_path: Path,
                                          monkeypatch: pytest.MonkeyPatch):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    a bundle reference resolving outside the skill root reddens (the
    escapes branch of _reference_errors): a fabricated point whose ref
    reaches a real file outside the root, over an otherwise real tree."""
    copied = tmp_path / "skills"
    shutil.copytree(SKILLS, copied,
                    ignore=shutil.ignore_patterns("__pycache__"))
    outside = tmp_path / "outside" / "references"
    outside.mkdir(parents=True)
    (outside / "x.md").write_text("проектный документ вне навыкового корня\n",
                                  "utf-8")
    escaping = ("ship", "**Сборка панели.", "../../../outside/references/x.md",
                "docs/reference/review-panel.md",
                "справочник `references/review-panel.md`")
    monkeypatch.setattr(sys.modules[__name__], "POINTS",
                        (escaping,) + POINTS[1:])
    errors = _reference_errors(_skill_texts(copied), copied)
    assert any("escapes the skill root" in error for error in errors)
