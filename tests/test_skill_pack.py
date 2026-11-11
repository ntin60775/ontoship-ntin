"""Contract for the pack skill (standards-autoship ticket 01).

The bundle must be discoverable as ``<root>/pack/SKILL.md`` and carry the
standards-pack contract: a model-invoked skill naming the bundle contract
reference with the full guard phrase, the stdlib validator with the named
refusal contour (stderr, exit 2, empty stdout), the project pack root
``.agents/packs/``, the norm priority order and the reference pack as the
living example. The contract reference file carries no repo paths and its
relative links resolve.

spec: docs/plans/standards-autoship.md#готово — бандл pack: скилл,
      API-документ контракта, валидатор, эталонный пак; паритет перечня
      бандлов сторожит состав
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
invariant: docs/plans/bundle-references.md#готово — guard phrase in every
      referencing step; retired carriers stay out of shipped bodies
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUNDLE = REPO / "skills" / "pack"
SKILL = BUNDLE / "SKILL.md"
CONTRACT = BUNDLE / "references" / "pack-contract.md"
VALIDATOR = BUNDLE / "validate_pack.py"
REFERENCE = BUNDLE / "reference-pack"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500

REQUIRED_PHRASES = (
    "references/pack-contract.md",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/pack-contract.md`",
    "написал свой, бери его",
    "validate_pack.py",
    "exit 2",
    "stdout пустой",
    ".agents/packs/",
    "канон > стандарты проекта > пак команды > пак стека > базовый документ",
    "reviewer-<kontur>-<aspect>",
    "reference-pack/",
    "только stdlib",
)
FORBIDDEN_ROOTS = (".dsh", ".zcode", ".qoder")
OLD_CARRIERS = (
    "docs/reference/review-roles.md",
    "docs/reference/harnesses.md",
    "docs/reference/testing.md",
    "docs/decisions/ontoship-core.md",
)
CONTRACT_PHRASES = (
    "manifest.json",
    "team",
    "stack",
    "MAJOR.MINOR.PATCH",
    "reviewer-<kontur>-<aspect>",
    "expect_exit",
    "валидатор проверяет схему, не семантику",
)


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n"), "frontmatter must open the file"
    body = text.split("---\n", 2)[1]
    fields: dict[str, str] = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields


def test_skill_is_a_model_invoked_pack_contract() -> None:
    """spec: docs/plans/standards-autoship.md#готово — скилл pack модельный,
    несёт контракт, валидацию и эталонный пак."""
    text = SKILL.read_text(encoding="utf-8")
    fields = _frontmatter(text)
    assert fields["name"] == "pack"
    assert NAME_RE.fullmatch(fields["name"])
    assert len(fields["description"]) <= DESCRIPTION_MAX
    assert "disable-model-invocation" not in text, \
        "pack is model-invoked: the agent validates packs itself"
    lowered = _normalized(text)
    for phrase in REQUIRED_PHRASES:
        assert _normalized(phrase) in lowered, f"lost phrase {phrase!r}"


def test_skill_names_no_harness_root_or_retired_carrier() -> None:
    """invariant: docs/plans/harness-agnostic.md#готово — skill texts name no
    harness root; invariant: docs/plans/bundle-references.md#готово — retired
    carriers stay out of shipped bodies."""
    lowered = _normalized(SKILL.read_text(encoding="utf-8"))
    for root in FORBIDDEN_ROOTS:
        assert root not in lowered, f"forbidden harness root {root!r}"
    for carrier in OLD_CARRIERS:
        assert carrier not in lowered, f"retired carrier {carrier!r}"


def test_contract_reference_is_portable() -> None:
    """spec: docs/plans/standards-autoship.md#готово — API-документ контракта
    в references/: без репо-путей, ссылки резолвятся."""
    text = CONTRACT.read_text(encoding="utf-8")
    for needle in ("docs/plans/", "skills/"):
        assert needle not in text, f"repo path {needle!r} in contract"
    lowered = _normalized(text)
    for phrase in CONTRACT_PHRASES:
        assert _normalized(phrase) in lowered, f"contract lost {phrase!r}"
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if re.match(r"(?:https?:|mailto:|#|/)", target):
            continue
        assert (CONTRACT.parent / target).resolve().exists(), \
            f"dead link {target!r}"


def test_reference_pack_passes_the_validator() -> None:
    """spec: docs/plans/standards-autoship.md#готово — эталонный минимальный
    пак: валидатор на нём проходит."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(REFERENCE)],
        capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "✓ пак reference-pack (team, 1.0.0) валиден" in result.stdout


def test_skill_contract_can_fail() -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт умеет падать:
    потеря guard-фразы и приоритета норм краснит проверку."""
    text = SKILL.read_text(encoding="utf-8")
    for phrase in ("написал свой, бери его",
                   "канон > стандарты проекта > пак команды > пак стека > базовый документ"):
        assert _normalized(phrase) in _normalized(text)
        pattern = re.escape(phrase).replace("\\ ", r"\s+")
        stripped = re.sub(pattern, "", text, flags=re.IGNORECASE)
        assert stripped != text, "the mutation must change the text"
        assert _normalized(phrase) not in _normalized(stripped)