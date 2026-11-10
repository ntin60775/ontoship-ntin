"""Bundle references carry the method sections (bundle-references ticket 01).

The six v0.3.0 references to project KB carriers (``docs/reference/…``) are
switched to bundle files: the owner bundle's ``references/`` directory or a
neighbor bundle via the relative ``../<bundle>/references/<file>`` path.
Every referencing step carries the guard phrase — the bundle file is the
primary source, the project overrides it with
``docs/reference/<bundle file name>`` — and every relative markdown link
inside a bundle reference file resolves on disk. Bundle reference files
carry no ntin-repo paths: ``docs/plans/`` and ``skills/`` stay out.

canon-section-in-bundles 01 switches the canon mentions: the header points
of critic, grilling, ship and to-tickets name the bundle section
(``../ship/references/method-phases.md``; ship — its own
``references/method-phases.md``) with the guard phrase, the «Порядок» step
of to-tickets cross-links the section, and no shipped skill body names the
canon path (``docs/decisions/ontoship-core.md``) anymore.

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

# The reference points: (skill, step marker, bundle reference, project
# override doc, reference phrase of this point). The six v0.3.0 switched
# points come first; canon-section-in-bundles 01 added the four header
# points. The marker slices
# the step's enclosing block; the phrase distinguishes two points sharing
# one block (ship names the bundle file twice in «Сборка панели»).
POINTS = (
    ("ship", "**Сборка панели.", "references/review-panel.md",
     "docs/reference/review-panel.md",
     "справочник `references/review-panel.md`"),
    ("ship", "Процедура запуска ролей — в том же", "references/review-panel.md",
     "docs/reference/review-panel.md",
     "процедура запуска ролей — в том же `references/review-panel.md`"),
    ("onto-doc", "2. Запусти fan-out `subagent`", "references/ontodoc-run.md",
     "docs/reference/ontodoc-run.md", "references/ontodoc-run.md"),
    ("onto-doc", "3. Прочитай отчёт прогона",
     "../testing/references/quality-rule.md", "docs/reference/quality-rule.md",
     "../testing/references/quality-rule.md"),
    ("testing", "Носитель правила качества канона", "references/quality-rule.md",
     "docs/reference/quality-rule.md", "references/quality-rule.md"),
    ("to-tickets", "- **Артефакт и ожидание**",
     "../testing/references/quality-rule.md", "docs/reference/quality-rule.md",
     "../testing/references/quality-rule.md"),
    # canon-section-in-bundles 01: the header points that switched from the
    # canon path to the bundle section. Ship owns the file, the other three
    # cross-reference it from their bundles.
    ("critic", "спека плюс тикеты", "../ship/references/method-phases.md",
     "docs/reference/method-phases.md",
     "../ship/references/method-phases.md"),
    ("grilling", "Этот скилл — фаза 1",
     "../ship/references/method-phases.md", "docs/reference/method-phases.md",
     "../ship/references/method-phases.md"),
    ("ship", "Вход — принятый оператором тикет",
     "references/method-phases.md", "docs/reference/method-phases.md",
     "references/method-phases.md"),
    ("to-tickets", "Вход — спека, утверждённая на план-гейте",
     "../ship/references/method-phases.md", "docs/reference/method-phases.md",
     "../ship/references/method-phases.md"),
)

# Every shipped bundle, taken from disk at import: a new bundle joins the
# sweeps by itself, and the tuple cannot drift from the installer array.
SHIPPED_SKILLS = tuple(sorted(path.parent.name
                              for path in SKILLS.glob("*/SKILL.md")))

# Project carriers retired from the shipped skill bodies: the three v0.3.0
# KB pages, and — with canon-section-in-bundles — the canon path itself,
# so «расширение OLD_CARRIERS» stays the single named artifact. The guard's
# override docs (docs/reference/<bundle file>) are different names and stay.
CANON_FILE = "docs/decisions/ontoship-core.md"
OLD_CARRIERS = (
    "docs/reference/review-roles.md",
    "docs/reference/harnesses.md",
    "docs/reference/testing.md",
    CANON_FILE,
)

# The «Порядок» step of to-tickets names the bundle section, not the canon.
ORDER_MARKER = "Критик замыкает нарезку"
CROSSLINK = "../ship/references/method-phases.md"

GUARD_HEAD = "файл бандла — первоисточник"
GUARD_TAIL = "написал свой, бери его"

# The run reference carries one section per harness (dsh-adaptation ticket
# 03): the DSH fan-out procedure lives beside the ZCode workflow procedure.
DSH_RUN_HEADING = "## dsh — прогон онто-дока"

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


def _skill_texts(root: Path = SKILLS,
                 skills: tuple[str, ...] = SHIPPED_SKILLS) -> dict[str, str]:
    """The shipped skill bodies, keyed by bundle name."""
    return {skill: (root / skill / "SKILL.md").read_text("utf-8")
            for skill in skills}


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
    """Every retired carrier of OLD_CARRIERS must be gone from the shipped
    skill bodies."""
    errors: list[str] = []
    for skill, text in texts.items():
        lowered = _normalized_lower(text)
        for carrier in OLD_CARRIERS:
            if carrier in lowered:
                errors.append(f"{skill}: project carrier {carrier!r} "
                              f"still referenced")
    return errors


def _canon_path_errors(texts: dict[str, str]) -> list[str]:
    """No shipped skill body names the ntin canon path anymore."""
    return [f"{skill}: canon path {CANON_PATH!r} still referenced"
            for skill, text in texts.items()
            if CANON_PATH in _normalized_lower(text)]


def _crosslink_errors(texts: dict[str, str]) -> list[str]:
    """The «Порядок» step of to-tickets names the bundle section."""
    try:
        block = _normalized_lower(_enclosing_block(texts["to-tickets"],
                                                   ORDER_MARKER))
    except ValueError:
        return [f"to-tickets: step marker {ORDER_MARKER!r} is missing"]
    if CROSSLINK not in block:
        return [f"to-tickets: step {ORDER_MARKER!r} lost the cross-link "
                f"{CROSSLINK!r}"]
    return []


def _canon_in_references_errors(root: Path = SKILLS) -> list[str]:
    """No shipped references/ file names the ntin canon path: a consumer
    follows bundle files only."""
    return [f"{path.relative_to(root)}: canon path {CANON_FILE!r} still "
            f"referenced"
            for path in reference_files(root)
            if CANON_FILE in path.read_text("utf-8")]


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
    switched references names a project docs/reference/ carrier anymore.
    spec: docs/plans/canon-section-in-bundles.md#готово — no shipped skill
    body names the ntin canon path (OLD_CARRIERS carries it since this
    unit's rewrite)."""
    errors = _old_carrier_errors(_skill_texts())
    assert errors == [], "\n".join(errors)


def test_canon_path_left_the_reference_files():
    """spec: docs/plans/canon-section-in-bundles.md#готово — no bundle
    reference file names the ntin canon path; consumers read the method
    sections from the bundle files."""
    errors = _canon_in_references_errors()
    assert errors == [], "\n".join(errors)


def test_order_step_crosslinks_the_bundle_section():
    """spec: docs/plans/canon-section-in-bundles.md#готово — the «Порядок»
    step of to-tickets names the bundle section instead of the canon."""
    errors = _crosslink_errors(_skill_texts())
    assert errors == [], "\n".join(errors)


@pytest.mark.parametrize("skill", ("critic", "grilling", "ship", "to-tickets"))
def test_method_section_guard_can_fail_per_skill(skill: str):
    """spec: docs/plans/canon-section-in-bundles.md#готово — потеря guard-фразы
    на имя method-phases.md краснит у каждого ссылающегося скилла; ошибки
    называют блок, потерявший фразу."""
    texts = _skill_texts()
    assert _guard_errors(texts) == []
    stripped = _drop_phrase(texts[skill], GUARD_HEAD)
    assert stripped != texts[skill], "the mutation must remove the guard"
    errors = _guard_errors({**texts, skill: stripped})
    assert any(f"{skill}: step" in error and GUARD_HEAD in error
               for error in errors), errors


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


def _dsh_run_section_errors(root: Path = SKILLS) -> list[str]:
    """The onto-doc run reference carries the DSH procedure section.

    spec: docs/plans/dsh-adaptation.md#готово — «Готово» 5: процедура
    DSH-прогона живёт в файле бандла онто-дока; ZCode-раздел снят вместе с
    рельсами, общая строка «DSH и Qoder — вне плана» не возвращается.
    """
    path = root / "onto-doc" / "references" / "ontodoc-run.md"
    if not path.is_file():
        return [f"onto-doc: run reference is missing: {path}"]
    text = _normalized_lower(path.read_text("utf-8"))
    errors: list[str] = []
    if DSH_RUN_HEADING not in text:
        return ["onto-doc: run reference carries no DSH procedure section"]
    section = text.split(DSH_RUN_HEADING, 1)[1].split(" ## ", 1)[0]
    if not section.strip():
        errors.append("onto-doc: DSH procedure section is empty")
    for phrase in ("`subagent` (spawn, не `subagent_fork`)",
                   "в одном сообщении",
                   "git diff --cached --name-only"):
        if phrase not in section:
            errors.append(f"onto-doc: DSH procedure section lost "
                          f"{phrase!r}")
    if "zcode" in text:
        errors.append("onto-doc: a ZCode procedure section is back")
    if "dsh и qoder — вне плана" in text:
        errors.append("onto-doc: the retired «DSH и Qoder — вне плана» "
                      "section is back")
    return errors


def test_run_reference_carries_the_dsh_procedure():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 5: DSH-процедура
онто-дока — раздел файла бандла; ZCode-раздел снят вместе с рельсами,
    общая строка «DSH и Qoder — вне плана» не возвращается."""
    errors = _dsh_run_section_errors()
    assert errors == [], "\n".join(errors)


def test_run_reference_dsh_section_can_fail(tmp_path: Path):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the run reference check rejects a missing DSH section, an empty DSH
    section, a DSH section without the spawn, the single message or the
    staged-diff check, a lost ZCode section and a resurrected combined
    section."""
    path = SKILLS / "onto-doc" / "references" / "ontodoc-run.md"
    text = path.read_text("utf-8")
    assert _dsh_run_section_errors() == []

    no_section = text.replace(DSH_RUN_HEADING, "## dsh — вне плана", 1)
    assert no_section != text
    assert any("no DSH procedure section" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, no_section)))

    head, _, rest = text.partition(DSH_RUN_HEADING)
    _, _, tail = rest.partition("## Qoder")
    empty = f"{head}{DSH_RUN_HEADING}\n\n## Qoder{tail}"
    assert _dsh_run_section_errors(_write_tree(tmp_path, empty))
    assert any("DSH procedure section is empty" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, empty)))

    no_spawn = _drop_phrase(text, "`subagent` (spawn, не `subagent_fork`)")
    assert no_spawn != text
    assert any("spawn, не `subagent_fork`" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, no_spawn)))

    no_single = _drop_phrase(text, "в одном сообщении")
    assert no_single != text
    assert any("в одном сообщении" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, no_single)))

    no_diff = _drop_phrase(text, "git diff --cached --name-only")
    assert no_diff != text
    assert any("git diff --cached --name-only" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, no_diff)))

    zcode_back = text + "\n## zcode — прогон онто-дока\n\nПрогон через workflow.\n"
    assert any("ZCode procedure section is back" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, zcode_back)))

    resurrected = text.replace("## Qoder — вне плана",
                               "## DSH и Qoder — вне плана", 1)
    assert resurrected != text
    assert any("DSH и Qoder" in error
               for error in _dsh_run_section_errors(
                   _write_tree(tmp_path, resurrected)))


def _write_tree(tmp_path: Path, run_text: str) -> Path:
    """A fabricated skills tree whose onto-doc run reference carries run_text."""
    root = tmp_path / "skills"
    shutil.copytree(SKILLS, root, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / "onto-doc" / "references" / "ontodoc-run.md").write_text(
        run_text, "utf-8")
    return root


def test_reference_checks_can_fail(tmp_path: Path):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the checks redden on a lost reference phrase, a missing reference file,
    a lost guard phrase, a priority inversion, a stray project carrier, a
    renamed override doc, a lost cross-link, a leaked canon carrier (in a
    body or in a references/ file), a dangling reference-file link and a
    repo path."""
    texts = _skill_texts()
    assert _reference_errors(texts) == []
    assert _guard_errors(texts) == []
    assert _old_carrier_errors(texts) == []
    assert _canon_in_references_errors() == []
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

    # The «Порядок» step loses its cross-link while the header keeps its
    # own mention: the check is block-scoped, so only the step's occurrence
    # (the last in the body) must go for the probe to redden.
    no_crosslink = "канон".join(
        texts["to-tickets"].rsplit("../ship/references/method-phases.md", 1))
    assert no_crosslink != texts["to-tickets"]
    assert "../ship/references/method-phases.md" in no_crosslink, \
        "the header mention must survive: the check is block-scoped"
    assert any("lost the cross-link" in error
               for error in _crosslink_errors({**texts,
                                               "to-tickets": no_crosslink}))

    # The canon-path sweep: a leaked canon mention in any shipped body
    # reddens, on a fabricated tree so the probes above cannot pre-redden it.
    island_skills = tmp_path / "canon-leak" / "skills"
    island_skills.parent.mkdir()
    shutil.copytree(SKILLS, island_skills,
                    ignore=shutil.ignore_patterns("__pycache__"))
    kb_search_body = (island_skills / "kb-search" / "SKILL.md").read_text("utf-8")
    (island_skills / "kb-search" / "SKILL.md").write_text(
        kb_search_body + "\nКанон — `docs/decisions/ontoship-core.md`.\n",
        "utf-8")
    errors = _old_carrier_errors(_skill_texts(island_skills))
    assert any("kb-search" in error for error in errors), errors

    # The references sweep: a canon-citing file under references/ reddens.
    (island_skills / "ship" / "references" / "canon-note.md").write_text(
        "Смотри канон: `docs/decisions/ontoship-core.md`.\n", "utf-8")
    assert any("canon-note.md" in error
               for error in _canon_in_references_errors(island_skills))

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
