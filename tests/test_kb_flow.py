"""KB carriers of the new flow (standards-autoship ticket 07).

``docs/reference/harnesses.md`` carries the chain and projection ways per
harness: the DSH way names the orchestrator's clean root session, the
continuable executor fed via ``send_message`` and the ``[validation]`` pool
of the registry; zcode is named retired, Qoder stays a named gap. The pack
reference ``docs/reference/pack-contract.md`` exists with sound frontmatter,
is linked from the folder index and names the ``--pack`` install channel.
``skills/README.md`` describes the critic bundle as projection validation
before slicing; the retired plan-critique description must not return.

spec: docs/plans/standards-autoship.md#готово — «Готово» 13: справочник
паков в docs/reference/ (проектный носитель контракта), harnesses.md несёт
цепочку и проекции, индексы обновлены
invariant: docs/decisions/ontoship-core.md#одно правило качества — the
contract check can fail
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HARNESSES = REPO / "docs" / "reference" / "harnesses.md"
PACK_REFERENCE = REPO / "docs" / "reference" / "pack-contract.md"
REFERENCE_INDEX = REPO / "docs" / "reference" / "README.md"
SKILLS_INDEX = REPO / "skills" / "README.md"

FLOW_HEADING = "## Цепочка и проекции по харнессам"
DSH_FLOW_NEEDLES = (
    "чистой корневой сессии",
    "send_message",
    "[validation]",
    "subagent",
    "list_subagent_models",
)
RETIRED_CRITIC_DESCRIPTION = "критика плана до первого ship"
CRITIC_DESCRIPTION = "проекционная валидация спеки до нарезки"


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _section(text: str, heading: str) -> str | None:
    """Body of a ``## `` section up to the next ``## `` heading."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.strip() == heading), None)
    if start is None:
        return None
    body: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _h3_blocks(section: str) -> dict[str, str]:
    """Lowered ``###`` heading → normalized heading-plus-body."""
    blocks: dict[str, str] = {}
    heading: str | None = None
    chunks: list[str] = []
    for line in section.splitlines():
        if line.startswith("### "):
            if heading is not None:
                blocks[heading] = _normalized_lower(" ".join(chunks))
            heading = line[4:].strip().lower()
            chunks = [line[4:]]
        elif heading is not None:
            chunks.append(line)
    if heading is not None:
        blocks[heading] = _normalized_lower(" ".join(chunks))
    return blocks


def _flow_errors(harnesses: str) -> list[str]:
    """Every violated chain/projection carrier fact; empty is sound."""
    section = _section(harnesses, FLOW_HEADING)
    if section is None:
        return ["harnesses.md has no chain-and-projections section"]
    errors: list[str] = []
    blocks = _h3_blocks(section)
    dsh_blocks = [block for heading, block in blocks.items()
                  if "dsh" in heading]
    if not dsh_blocks:
        errors.append("the DSH chain/projection way has no subsection")
    else:
        for needle in DSH_FLOW_NEEDLES:
            if needle.lower() not in dsh_blocks[0]:
                errors.append(f"the DSH way lost {needle!r}")
    zcode_retired = any("zcode" in heading and "снят" in block
                        for heading, block in blocks.items())
    if not zcode_retired:
        errors.append("the zcode chain/projection way is not named retired")
    qoder_gap = any("qoder" in heading and "пробел" in block
                    for heading, block in blocks.items())
    if not qoder_gap:
        errors.append("the Qoder chain/projection way is not named a gap")
    return errors


def _frontmatter(text: str) -> dict[str, str]:
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


def _pack_reference_errors(page: str, index: str) -> list[str]:
    """Every violated pack-reference fact; empty is sound."""
    errors: list[str] = []
    fields = _frontmatter(page)
    if fields.get("node_type") != "reference":
        errors.append("pack reference: node_type must be reference")
    if fields.get("status") != "active":
        errors.append("pack reference: status must be active")
    lowered = _normalized_lower(page)
    if "--pack" not in lowered:
        errors.append("pack reference does not name the --pack channel")
    if "гейты" not in lowered or "как данные" not in lowered:
        errors.append("pack reference does not name gates as data")
    if "pack-contract.md" not in index:
        errors.append("docs/reference/README.md does not link pack-contract.md")
    return errors


def test_harnesses_carry_the_chain_and_projections():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 13:
    harnesses.md несёт цепочку и проекции — DSH-способ с чистой корневой
    сессией, продолжаемым исполнителем и пулом валидации; zcode снят,
    Qoder — названный пробел."""
    assert _flow_errors(HARNESSES.read_text("utf-8")) == []


def test_pack_reference_exists_and_is_linked():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 13:
    справочник паков в docs/reference/ — проектный носитель контракта,
    связан из индекса папки, называет канал --pack и гейты как данные."""
    assert PACK_REFERENCE.is_file(), "the pack reference is missing"
    errors = _pack_reference_errors(PACK_REFERENCE.read_text("utf-8"),
                                    REFERENCE_INDEX.read_text("utf-8"))
    assert errors == [], "\n".join(errors)


def test_skills_index_describes_projection_validation():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 13, решение
    16: индекс бандлов описывает critic как проекционную валидацию спеки до
    нарезки; снятая критика плана до первого ship не возвращается."""
    text = SKILLS_INDEX.read_text("utf-8")
    assert CRITIC_DESCRIPTION in _normalized_lower(text)
    assert RETIRED_CRITIC_DESCRIPTION not in _normalized_lower(text)


def test_kb_flow_checks_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the checks redden on a lost flow section, a lost DSH needle, an
    unretired zcode way, a lost Qoder gap, an unlinked pack reference, a
    lost --pack channel and a returned plan-critique description."""
    harnesses = HARNESSES.read_text("utf-8")
    assert _flow_errors(harnesses) == []

    no_section = harnesses.replace(FLOW_HEADING, "## Цепочка вне плана", 1)
    assert no_section != harnesses
    assert any("no chain-and-projections section" in error
               for error in _flow_errors(no_section))

    no_send = harnesses.replace("send_message", "сообщения", 1)
    assert no_send != harnesses
    assert any("send_message" in error for error in _flow_errors(no_send))

    no_pool = harnesses.replace("[validation]", "[agents.critic]", 1)
    assert no_pool != harnesses
    assert any("[validation]" in error for error in _flow_errors(no_pool))

    unretired = harnesses.replace("### zcode — цепочка и проекции сняты",
                                  "### zcode — цепочка и проекции", 1)
    assert unretired != harnesses
    assert any("not named retired" in error
               for error in _flow_errors(unretired))

    no_gap = harnesses.replace(
        "### Qoder — цепочка и проекции — пробел окружения",
        "### Qoder — цепочка и проекции — рабочий способ", 1)
    assert no_gap != harnesses
    assert any("not named a gap" in error for error in _flow_errors(no_gap))

    page = PACK_REFERENCE.read_text("utf-8")
    index = REFERENCE_INDEX.read_text("utf-8")
    assert _pack_reference_errors(page, index) == []
    orphan = index.replace("pack-contract.md", "packs.md")
    assert orphan != index
    assert any("does not link pack-contract.md" in error
               for error in _pack_reference_errors(page, orphan))
    no_channel = page.replace("--pack", "--skills")
    assert no_channel != page
    assert any("--pack" in error
               for error in _pack_reference_errors(no_channel, index))

    skills_index = SKILLS_INDEX.read_text("utf-8")
    returned = skills_index.replace(CRITIC_DESCRIPTION,
                                    RETIRED_CRITIC_DESCRIPTION, 1)
    assert returned != skills_index
    assert RETIRED_CRITIC_DESCRIPTION in _normalized_lower(returned)