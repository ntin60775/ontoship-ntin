"""Contract for the kb-curate skill and the shipped ontology model.

spec: docs/plans/core-kb.md#рамки — skills/kb-curate/SKILL.md and ontology.md
spec: tickets/core-kb/03-kb-curate-ontology.md — CREATE/UPDATE/DEPRECATE/LINK/REINDEX
invariant: I2 — docs/ontology.md is the single type vocabulary
invariant: I8 — project and shipped ontology bodies agree from the first `## `
invariant: I1/I4 — a curated doc passes; removing its type or breaking its link fails
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from conftest import ENGINE, REPO

SKILL = REPO / "skills" / "kb-curate" / "SKILL.md"
SHIPPED = REPO / "skills" / "kb-curate" / "ontology.md"
PROJECT = REPO / "docs" / "ontology.md"
OPERATIONS = ("CREATE", "UPDATE", "DEPRECATE", "LINK", "REINDEX")
TYPE_ROW = re.compile(r"^\|\s*`([a-z][a-z_0-9]*)`\s*\|")
INVARIANT_ROW = re.compile(r"^\| (I\d+) \|", re.MULTILINE)
CORE_INVARIANTS = {f"I{i}" for i in (1, 2, 3, 4, 5, 6, 8, 9, 10)}


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


def _contract_errors(text: str) -> list[str]:
    """Every violated kb-curate contract; empty means the skill is sound."""
    try:
        fields, body = _parse_skill(text)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    if fields.get("name") != "kb-curate":
        errors.append("frontmatter: name must be kb-curate")
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
    for operation in OPERATIONS:
        if not re.search(rf"^## {operation}\b", body, re.MULTILINE):
            errors.append(f"body: missing operation {operation}")
    for needle in ("docs/ontology.md", "node_type", "README.md",
                   "gitmark.py index", "gitmark.py lint --strict", ".agents/skills"):
        if needle not in body:
            errors.append(f"body: missing {needle!r}")
    flat = re.sub(r"\s+", " ", body)
    if "I7" not in flat or "вне ядра" not in flat:
        errors.append("body: does not state that I7 stays out of the core")
    lowered = text.lower()
    for term in ("provenance", "reel", "acceptance chord"):
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            errors.append(f"forbidden entity {term!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/core-kb.md#рамки — skills/kb-curate/SKILL.md."""
    assert SKILL.is_file(), "the kb-curate skill is missing"
    fields, _ = _parse_skill(SKILL.read_text("utf-8"))
    assert fields["name"] == "kb-curate"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= 500
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_contract_can_fail():
    """invariant: the contract check rejects a missing operation, model or name."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_operation = text.replace("## LINK", "## CONNECT", 1)
    assert missing_operation != text
    assert any("LINK" in error for error in _contract_errors(missing_operation))

    missing_model = text.replace("docs/ontology.md", "docs/nowhere.md")
    assert missing_model != text
    assert any("docs/ontology.md" in error for error in _contract_errors(missing_model))

    leaked_entity = text + "\nUse a provenance line.\n"
    assert any("provenance" in error for error in _contract_errors(leaked_entity))

    leaked_root = text + "\nInstall into .dsh/skills instead.\n"
    assert any(".dsh" in error for error in _contract_errors(leaked_root))

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


def _table_types(text: str) -> list[str]:
    """The types in the `| node_type ...` table, in file order."""
    found: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| node_type "):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            match = TYPE_ROW.match(line)
            if match:
                found.append(match.group(1))
    return found


def _body_from_first_h2(path: Path) -> str:
    """The model body the spec names: everything from the first `## ` heading."""
    lines = path.read_text("utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## "):
            return "\n".join(x.rstrip() for x in lines[index:]).strip()
    return ""


def test_docs_ontology_is_the_single_i2_vocabulary(gm):
    """invariant: I2 — docs/ontology.md is the only type vocabulary lint reads."""
    types = _table_types(PROJECT.read_text("utf-8"))
    assert types, "docs/ontology.md has no `| node_type` table"
    assert len(types) == len(set(types)), "duplicate node_type rows"
    assert gm.node_types(REPO) == set(types)

    for path in sorted((REPO / "docs").rglob("*.md")):
        fm = gm.parse_frontmatter(path.read_text("utf-8"))
        node_type = (fm or {}).get("node_type")
        if node_type:
            assert node_type in types, f"{path.relative_to(REPO)}: {node_type} outside the table"


def test_project_and_shipped_ontology_bodies_agree(gm):
    """invariant: I8 — the two copies are one model from the first `## ` heading."""
    project = _body_from_first_h2(PROJECT)
    shipped = _body_from_first_h2(SHIPPED)
    assert project, "docs/ontology.md has no `## ` body"
    assert project == shipped
    assert gm.ontology_twin_issues(REPO) == []


def test_invariant_table_is_exactly_the_core_set(gm):
    """spec: ticket 03 — I1–I6 and I8–I10; I7 stays out of the core."""
    body = _body_from_first_h2(PROJECT)
    ids = INVARIANT_ROW.findall(body)
    assert set(ids) == CORE_INVARIANTS
    assert len(ids) == len(set(ids)), "duplicate invariant row"
    assert "I7" not in ids
    flat = re.sub(r"\s+", " ", body)
    assert "I7" in flat and "вне ядра" in flat


def test_repository_kb_passes_lint_without_errors(gm):
    """spec: docs/plans/core-kb.md#готово-6 — the curated KB passes lint --strict."""
    result = gm.cmd_lint(REPO)
    assert result["errors"] == [], result["errors"]


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _demo_repo(tmp_path: Path) -> Path:
    _write(tmp_path / "docs" / "ontology.md", SHIPPED.read_text("utf-8"))
    _write(tmp_path / "docs" / "README.md",
           "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
           "[reference](reference/README.md)\n")
    _write(tmp_path / "docs" / "reference" / "README.md",
           "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n\n"
           "[demo](demo.md) — a demo document.\n")
    _write(tmp_path / "docs" / "reference" / "demo.md",
           "---\nnode_type: reference\ntitle: Demo\nservice: _platform\nstatus: active\n"
           "updated: 2026-10-20\nlinks:\n  part_of: [README.md]\n---\n\n"
           "# Demo\n\nSee the [folder index](README.md).\n")
    return tmp_path


def _cli(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ENGINE), "--root", str(root),
                           "lint", "--strict"], capture_output=True, text=True)


def test_demo_doc_passes_then_i1_and_i4_fail_strict(gm, tmp_path: Path):
    """spec: ticket 03 — a doc with a type, body link and README link passes; mutations fail."""
    root = _demo_repo(tmp_path)
    assert gm.cmd_lint(root)["errors"] == []
    assert _cli(root).returncode == 0

    doc = root / "docs" / "reference" / "demo.md"
    valid = doc.read_text("utf-8")

    doc.write_text(valid.replace("node_type: reference\n", "", 1), encoding="utf-8")
    missing_type = gm.cmd_lint(root)["issues"]
    assert any(issue[0] == "ERR" and issue[1] == "I1"
               and issue[2] == "docs/reference/demo.md" for issue in missing_type)
    cli = _cli(root)
    assert cli.returncode == 1
    assert "I1" in cli.stdout

    doc.write_text(valid.replace("(README.md)", "(missing.md)", 1), encoding="utf-8")
    broken_link = gm.cmd_lint(root)["issues"]
    assert any(issue[0] == "ERR" and issue[1] == "I4"
               and issue[2] == "docs/reference/demo.md" for issue in broken_link)
    cli = _cli(root)
    assert cli.returncode == 1
    assert "I4" in cli.stdout