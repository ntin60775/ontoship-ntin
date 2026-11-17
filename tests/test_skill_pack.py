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
KB_CONTRACT = REPO / "docs" / "reference" / "pack-contract.md"
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
    "--pack",
    "run_gates.py",
    # Approval mark: who approved, not when; the date lives in the frontmatter.
    "решение оператора (кто утвердил)",
    "дата — во frontmatter",
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
    # Pack definition, trust boundary and norm-level scope (logika review):
    # the gates live in the manifest as data, not as files of the pack.
    "каталог с манифестом `manifest.json` и необязательными файлами",
    "конфиги гейтов живут в манифесте как данные",
    "гейт — декларация команды в манифесте, не исполняемый файл пака",
    "доверие паку — названное решение оператора",
    "объём уровней: стандарты проекта — документы проекта, кроме базового документа",
    "базовый документ — нижний уровень",
    # standards-autoship 05: the gate-execution contract of the core runner.
    "исполнение гейтов",
    "run_gates.py",
    "exit 1",
    "без shell-интерпретации",
)
# The bundle file and the project reference are two carriers of one contract;
# a reworded definition in one of them alone is a parity break.
PARITY_PHRASES = (
    "каталог с манифестом `manifest.json` и необязательными файлами стандартов и чек-листов ролей",
    "конфиги гейтов живут в манифесте как данные",
    "гейт — декларация команды в манифесте, не исполняемый файл пака",
    "доверие паку — названное решение оператора",
    "объём уровней: стандарты проекта — документы проекта, кроме базового документа",
    "паки — отдельный класс по источнику (команда или стек)",
    "базовый документ — нижний уровень",
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


def _bundle_texts() -> dict[str, str]:
    texts = {"SKILL.md": SKILL.read_text(encoding="utf-8"),
             "references/pack-contract.md": CONTRACT.read_text(encoding="utf-8"),
             "validate_pack.py": VALIDATOR.read_text(encoding="utf-8")}
    for path in sorted(REFERENCE.rglob("*")):
        if path.is_file():
            texts[str(path.relative_to(BUNDLE))] = path.read_text(encoding="utf-8")
    return texts


def test_skill_names_no_harness_root_or_retired_carrier() -> None:
    """invariant: docs/plans/harness-agnostic.md#готово — skill texts name no
    harness root; invariant: docs/plans/bundle-references.md#готово — retired
    carriers stay out of shipped bodies. Every shipped bundle file is a
    carrier, not only SKILL.md."""
    for name, text in _bundle_texts().items():
        lowered = _normalized(text)
        for root in FORBIDDEN_ROOTS:
            assert root not in lowered, f"{name}: forbidden harness root {root!r}"
        for carrier in OLD_CARRIERS:
            assert carrier not in lowered, f"{name}: retired carrier {carrier!r}"


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


def test_contract_carriers_keep_one_definition() -> None:
    """spec: docs/plans/standards-autoship.md#готово — два носителя контракта
    (файл бандла и проектный справочник) несут одну формулировку: пак — это
    манифест и файлы стандартов и чек-листов, гейты живут в манифесте как
    данные; доверие паку — решение оператора, не свойство данных; лестница
    норм названа рядом с объёмом её уровней."""
    for path in (CONTRACT, KB_CONTRACT):
        lowered = _normalized(path.read_text(encoding="utf-8"))
        for phrase in PARITY_PHRASES:
            assert _normalized(phrase) in lowered, \
                f"{path.name} lost {phrase!r}"

    # can-fail: a drift in one carrier alone reddens the parity guard.
    text = KB_CONTRACT.read_text(encoding="utf-8")
    mutated = text.replace("каталог с манифестом", "каталог-пак", 1)
    assert mutated != text, "the mutation must change the carrier"
    assert _normalized(PARITY_PHRASES[0]) not in _normalized(mutated)


def test_reference_pack_passes_the_validator() -> None:
    """spec: docs/plans/standards-autoship.md#готово — эталонный минимальный
    пак: валидатор на нём проходит."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(REFERENCE)],
        capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "✓ пак reference-pack (team, 1.0.0) валиден" in result.stdout


def test_gate_execution_contract_is_named() -> None:
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 8 (тикет 05):
    шаг механических гейтов пака опирается на исполнитель бандла —
    run_gates.py рядом с валидатором; контракт исполнения назван в
    API-документе, скилл ведёт в него."""
    assert (BUNDLE / "run_gates.py").is_file(), "the gate runner is missing"
    contract = _normalized(CONTRACT.read_text(encoding="utf-8"))
    for phrase in ("исполнение гейтов", "run_gates.py", "exit 1",
                   "без shell-интерпретации"):
        assert phrase in contract, f"the execution contract lost {phrase!r}"
    skill = _normalized(SKILL.read_text(encoding="utf-8"))
    assert "run_gates.py" in skill
    assert "механические гейты пака" in skill

    # can-fail: the contract check reddens when the execution section leaves.
    text = CONTRACT.read_text(encoding="utf-8")
    stripped = text.replace("## Исполнение гейтов", "## Прочее", 1)
    assert stripped != text
    assert "исполнение гейтов" not in _normalized(stripped)


def _missing_phrases(text: str) -> list[str]:
    lowered = _normalized(text)
    return [phrase for phrase in REQUIRED_PHRASES
            if _normalized(phrase) not in lowered]


def test_channel_gap_wording_is_gone() -> None:
    """spec: docs/plans/standards-autoship.md#готово — канал --pack и
    обнаружение init поставлены: оговорка пробела снята с носителей."""
    for path in (SKILL, CONTRACT):
        lowered = _normalized(path.read_text(encoding="utf-8"))
        assert "ещё не поставлены" not in lowered, path
        assert "пока канал не поставлен" not in lowered, path


def test_skill_contract_can_fail() -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт умеет падать:
    потеря guard-фразы и приоритета норм краснит проверку (предикат гоняется
    по мутированному носителю, не по собственному срезу строки)."""
    text = SKILL.read_text(encoding="utf-8")
    assert _missing_phrases(text) == []
    for phrase in ("написал свой, бери его",
                   "канон > стандарты проекта > пак команды > пак стека > базовый документ"):
        pattern = re.escape(phrase).replace("\\ ", r"\s+")
        stripped = re.sub(pattern, "", text, flags=re.IGNORECASE)
        assert stripped != text, "the mutation must change the text"
        assert phrase in _missing_phrases(stripped)
