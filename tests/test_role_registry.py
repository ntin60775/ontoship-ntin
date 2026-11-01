"""Anchor parity between the role registry and its carriers.

spec: docs/plans/role-registry.md#готово — skills/init/roles.py is the machine
source of the role lists; every carrier (the test tuples, the init skill's
check line, the reference base-set sections) must stay in two-way parity with
it. Parsing is text-based, like the installer array SKILLS; the check-list
parser is reused from tests/test_skill_init.py, not duplicated.

Every check takes a root parameter (the _parity_errors pattern of
tests/test_install.py): probes mutate copies in a temporary tree, the working
tree is never modified.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

import test_skill_init  # reuse: the check-list parser, not duplicated

REPO = Path(__file__).resolve().parent.parent
REGISTRY = "skills/init/roles.py"

# (file, variable, side): which carrier tuple mirrors which registry tuple.
CARRIER_TUPLES = (
    ("tests/test_skill_init.py", "CORE_ROLES", "core"),
    ("tests/test_gen_agents.py", "CORE_ROLES", "core"),
    ("tests/test_review_roles.py", "ROLES", "panel"),
)

# Every file the parity reads; probes copy them into a temporary tree.
FILES = (REGISTRY, "skills/init/SKILL.md") + tuple(c[0] for c in CARRIER_TUPLES) + (
    "docs/reference/review-roles.md",
)

# (probe, file, old, new, needle): one mutation per carrier direction, per the
# ticket — a dropped role and a phantom role on every carrier, a duplicate
# entry and a PANEL ⊄ CORE break on the registry itself. needle is the error
# fragment that must appear, so the probe proves detection, not just failure.
PROBES = (
    ("skill-init-tuple-drops-critic", "tests/test_skill_init.py",
     ', "critic",\n', ',\n', "misses the critic role"),
    ("skill-init-tuple-phantom", "tests/test_skill_init.py",
     '              "curator")', '              "curator", "auditor")',
     "carries a phantom auditor role"),
    ("gen-agents-tuple-drops-critic", "tests/test_gen_agents.py",
     ', "critic",\n', ',\n', "misses the critic role"),
    ("gen-agents-tuple-phantom", "tests/test_gen_agents.py",
     '              "curator")', '              "curator", "auditor")',
     "carries a phantom auditor role"),
    ("review-roles-tuple-drops-kb", "tests/test_review_roles.py",
     ', "reviewer-kb")', ')', "misses the reviewer-kb role"),
    ("review-roles-tuple-phantom", "tests/test_review_roles.py",
     '"reviewer-kb")', '"reviewer-kb", "auditor")',
     "carries a phantom auditor role"),
    ("skill-check-line-drops-critic", "skills/init/SKILL.md",
     "`critic`, `curator` — с секциями", "`curator` — с секциями",
     "misses the critic role"),
    ("skill-check-line-phantom", "skills/init/SKILL.md",
     "`curator` — с секциями", "`curator`, `auditor` — с секциями",
     "carries a phantom auditor role"),
    ("reference-drops-section", "docs/reference/review-roles.md",
     "### reviewer-code — качество реализации\n", "",
     "misses the reviewer-code role"),
    ("reference-phantom-section", "docs/reference/review-roles.md",
     "## Регламент паков", "### auditor — проба\n\n## Регламент паков",
     "carries a phantom auditor role"),
    ("registry-duplicate-entry", REGISTRY,
     '"critic", "curator")', '"critic", "curator", "critic")',
     "duplicate entry"),
    ("registry-panel-leaves-the-core", REGISTRY,
     'PANEL_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb")',
     'PANEL_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb", "auditor")',
     "not a subset"),
)


def _parsed_tuple(source: str, name: str) -> list[str] | None:
    """Tuple entries parsed as text, or None when the assignment is missing."""
    match = re.search(rf"^{name} = \(([^)]*)\)", source, re.MULTILINE)
    if not match:
        return None
    return [part.strip().strip("\"'") for part in match.group(1).split(",")
            if part.strip()]


def _parity_side(own: list[str], other: list[str], label: str) -> list[str]:
    """Two-way parity of a carrier against its registry tuple."""
    errors = []
    for role in own:
        if role not in other:
            errors.append(f"parity: {label} misses the {role} role")
    for role in other:
        if role not in own:
            errors.append(f"parity: {label} carries a phantom {role} role")
    if sorted(own) != sorted(other):
        errors.append(f"parity: {label} is not a permutation of the registry "
                      "tuple (duplicate entry?)")
    return errors


def _registry_internal_errors(root: Path) -> tuple[list[str] | None, list[str] | None,
                                                   list[str]]:
    """Data-only shape and the internal invariants of the registry itself."""
    errors: list[str] = []
    path = root / REGISTRY
    if not path.is_file():
        return None, None, [f"registry: {REGISTRY} is missing"]
    source = path.read_text("utf-8")
    code = "\n".join(line for line in source.splitlines()
                     if line.strip() and not line.strip().startswith("#"))
    for token in ("def ", "class ", "import ", "lambda "):
        if token in code:
            errors.append(f"registry: roles.py carries executable logic "
                          f"({token.strip()})")
    assigned = re.findall(r"^([A-Za-z_]+) =", code, re.MULTILINE)
    if assigned != ["CORE_ROLES", "PANEL_ROLES"]:
        errors.append(f"registry: roles.py assigns {assigned or 'nothing'} "
                      "instead of the two tuples")
    core = _parsed_tuple(source, "CORE_ROLES")
    panel = _parsed_tuple(source, "PANEL_ROLES")
    if core is None:
        errors.append("registry: roles.py carries no CORE_ROLES tuple")
    if panel is None:
        errors.append("registry: roles.py carries no PANEL_ROLES tuple")
    if core is None or panel is None:
        return core, panel, errors
    for name, entries in (("CORE_ROLES", core), ("PANEL_ROLES", panel)):
        malformed = [e for e in entries
                     if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", e)]
        if malformed:
            errors.append(f"registry: {name} carries non-role tokens {malformed}")
        if len(entries) != len(set(entries)):
            errors.append(f"registry: {name} carries a duplicate entry")
    if not set(panel) <= set(core):
        errors.append("registry: PANEL_ROLES is not a subset of CORE_ROLES")
    return core, panel, errors


def _registry_errors(root: Path) -> list[str]:
    """Every violated registry-parity rule; empty means the carriers agree."""
    core, panel, errors = _registry_internal_errors(root)
    if core is None or panel is None:
        return errors

    for rel, name, kind in CARRIER_TUPLES:
        label = f"the {name} tuple of {rel}"
        path = root / rel
        if not path.is_file():
            errors.append(f"parity: {rel} is missing")
            continue
        entries = _parsed_tuple(path.read_text("utf-8"), name)
        if entries is None:
            errors.append(f"parity: {rel} carries no {name} tuple")
            continue
        errors.extend(_parity_side(core if kind == "core" else panel, entries, label))

    skill = root / "skills" / "init" / "SKILL.md"
    if not skill.is_file():
        errors.append("parity: skills/init/SKILL.md is missing")
    else:
        declared, well_formed = test_skill_init._declared_core_roles(
            skill.read_text("utf-8"))
        if not declared and not well_formed:
            errors.append("parity: the check list anchor of "
                          "skills/init/SKILL.md is missing")
        else:
            if not well_formed:
                errors.append("parity: the check list of skills/init/SKILL.md "
                              "carries a non-role token")
            errors.extend(_parity_side(core, declared,
                                       "the check list of skills/init/SKILL.md"))

    reference = root / "docs" / "reference" / "review-roles.md"
    if not reference.is_file():
        errors.append("parity: docs/reference/review-roles.md is missing")
    else:
        sections = re.findall(r"^### ([a-z0-9][a-z0-9-]*) — ",
                              reference.read_text("utf-8"), re.MULTILINE)
        errors.extend(_parity_side(panel, sections,
                                   "the base-set sections of "
                                   "docs/reference/review-roles.md"))
    return errors


def _carriers(tmp_path: Path, **overrides: str) -> Path:
    """A temporary tree with the carrier files; overrides replace content."""
    root = tmp_path / "tree"
    for rel in FILES:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(overrides.get(rel, (REPO / rel).read_text("utf-8")),
                          "utf-8")
    return root


def test_registry_carries_data_with_the_two_tuples() -> None:
    """spec: docs/plans/role-registry.md#готово-1 — the registry holds the
    two tuples and nothing executable: only data and the origin comment."""
    core, panel, errors = _registry_internal_errors(REPO)
    assert errors == []
    assert core and panel


def test_panel_is_a_subset_of_the_core() -> None:
    """invariant: docs/plans/role-registry.md#готово-1 — PANEL_ROLES ⊆
    CORE_ROLES: the review panel is a subset of the core, in the registry."""
    core, panel, errors = _registry_internal_errors(REPO)
    assert errors == []
    assert set(panel) <= set(core)


def test_registry_holds_two_way_parity_now() -> None:
    """spec: docs/plans/role-registry.md#готово-2 — on the aligned tree every
    carrier agrees with the registry in both directions: no misses, no
    phantoms, no duplicates."""
    assert _registry_errors(REPO) == []


@pytest.mark.parametrize(("probe", "rel", "old", "new", "needle"), PROBES,
                         ids=[p[0] for p in PROBES])
def test_a_mutated_carrier_is_named_by_the_probe(
        tmp_path: Path, probe: str, rel: str, old: str, new: str,
        needle: str) -> None:
    """target: each mutation — a dropped role, a phantom, a duplicate, a
    broken subset — is caught and named, not just met with a non-empty
    error list (spec, Готово 2)."""
    source = (REPO / rel).read_text("utf-8")
    assert old in source, f"the probe {probe} no longer matches its carrier"
    errors = _registry_errors(_carriers(tmp_path, **{rel: source.replace(old, new, 1)}))
    assert any(needle in error for error in errors), errors
