"""Contract for the deliver skill (deliver unit, ticket 01).

The bundle is the intent carrier «поставить/обновить OntoShip в проекте»:
the full delivery/update protocol lives in the skill, the init block only
names the command (decision 1). These checks pin the shipped artifact
against the spec sections «Протокол deliver» and «Контракт акта» and the
connector branches of decision 7: the registry skill present — follow its
rules, the file absent — start the ledger then write the act, the skill
absent — a named gap, no fallback record. The description carries the
delivery/update semantics without the paraphrase literals «раскатай ядро
в X» (triage G-24); model invocation stays open — the catalog routes the
intent by description. The bundle names no project facts: it installs
into foreign repositories.

spec: docs/plans/deliver.md#готово — «Готово» 1: бандл существует, несёт
      протокол и текст коннектора, description семантики поставки/обновления
spec: docs/plans/deliver.md#протокол-deliver — восемь шагов: источник,
      поиск X, состояние, канал, установка/обновление, init, акт, отчёт
spec: docs/plans/deliver.md#контракт-акта — поля акта, followups,
      acceptance-пробел, deployed.json не заводится
spec: docs/plans/deliver.md#решения — решения 1, 7: носитель интента —
      скилл + строка блока; коннектор начинает ведение при отсутствующем файле
invariant: docs/reference/text-style.md#смысловое-направление — проектных
      фактов в бандле нет: абсолютные пути, имена сессий, порты
invariant: docs/decisions/ontoship-core.md#одно правило качества — the
      contract check can fail
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "deliver" / "SKILL.md"

# The routing carrier: the description must match the intent semantically
# («Готово» 1) — delivery, update and deploy of OntoShip in a project.
DESCRIPTION_NEEDLES = (
    "Поставка и обновление OntoShip в проекте",
    "поставить OntoShip в проект",
    "обновить установку",
    "деплой и обновление",
)
# G-24: the paraphrase «раскатай ядро в X» shares no words with the
# carriers — its literals must not leak into the description.
DESCRIPTION_FORBIDDEN = ("раскатай", "ядро")

# One anchor per protocol norm («Протокол deliver»); checked on the
# whitespace-flattened text, so an 80-column wrap cannot hide a clause.
PROTOCOL_NEEDLES = (
    "`scripts/install.sh` лежит в корне репо ядра, не в бандле",
    "realpath бандла `.agents/skills/deliver`",
    "copy-продюсер — ask оператора о чекауте ядра",
    "Молчаливого клона и remote нет",
    "Канал продюсера и путь использованного install.sh фиксируй в evidence",
    "имя → реестр потребителей и соседние чекауты",
    "не найден — ask пути, не угадывай",
    "`install.sh --check <X>` до обновления",
    "до утверждения «поставлено»",
    "`check: ok` не отменяет warning",
    "ask канала link/copy",
    "смена канала — ask оператора",
    "(relink), не деструктив",
    "«copy differs»",
    "останавливается на ask удаления",
    "После свежей установки и при обновлении — скилл init",
    "только между маркерами ontoship",
    "install.sh сам init не запускает",
    "скилл реестра `consumer-registry`",
    "файла реестра нет — исполни старт ведения по правилам скилла",
    "Скилла нет — запись не делается",
    "fallback-записи в другой носитель нет",
    "deliver не ставит реестр потребителям",
    "continue.md целевого проекта deliver не пишет",
    "Версия до/после, канал, вывод check, warning",
)

# The act contract («Контракт акта», triage G-6/G-7): every field rule.
CONTRACT_NEEDLES = (
    "`action` = `rollout` (свежая поставка) | `update` (обновление)",
    "`actor` = сессия deliver",
    "тег link-дерева, иначе `git describe`",
    "без прежней записи — `unknown` с названным пробелом",
    "`from` = прежнее `consumers[].version`",
    "`updated_at` обновляется",
    "открытые followups (`done: false`)",
    "followup «свежая сессия потребителя»",
    "`acceptance[]` deliver не заполняет",
    "deployed.json не заводится",
)

# Project facts never ship in a bundle (text-style, «Смысловое направление»
# 4): absolute paths, session names, loopback addresses.
PROJECT_FACT_RE = re.compile(r"/home/|/tmp/|session-[0-9a-f]|dwfrun-|127\.0\.0\.1")


def _frontmatter(text: str) -> dict[str, str]:
    """Parse the single-line YAML frontmatter the skill uses."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"')
    return {}


def _contract_errors(text: str) -> list[str]:
    """Every violated deliver-bundle rule; empty means the carrier is sound."""
    errors: list[str] = []
    fields = _frontmatter(text)
    if fields.get("name") != "deliver":
        errors.append("frontmatter: name is not deliver")
    description = fields.get("description", "")
    if not 3 <= len(description) <= 500:
        errors.append("frontmatter: description length out of 3..500")
    # Decision 1: the catalog routes the intent by description — a
    # user-only flag would kill the native routing.
    if "disable-model-invocation" in text:
        errors.append("frontmatter: model invocation must stay open")
    for needle in DESCRIPTION_NEEDLES:
        if needle not in description:
            errors.append(f"description: missing intent semantics {needle!r}")
    for word in DESCRIPTION_FORBIDDEN:
        if word in description.lower():
            errors.append(f"description: paraphrase literal {word!r} (G-24)")
    flat = re.sub(r"\s+", " ", text)
    for needle in PROTOCOL_NEEDLES:
        if needle not in flat:
            errors.append(f"protocol: missing {needle!r}")
    for needle in CONTRACT_NEEDLES:
        if needle not in flat:
            errors.append(f"act contract: missing {needle!r}")
    match = PROJECT_FACT_RE.search(text)
    if match:
        errors.append(f"project fact in the bundle: {match.group(0)!r}")
    return errors


def test_bundle_carries_the_protocol_and_the_act_contract():
    """spec: docs/plans/deliver.md#готово — «Готово» 1, решения 1, 7:
    skills/deliver/SKILL.md существует и несёт протокол из спеки, текст
    коннектора и контракт акта; на базе падает — файла нет."""
    assert SKILL.is_file(), "the deliver bundle is missing"
    assert SKILL.parent.name == "deliver", "bundle directory must match the skill name"
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_description_carries_intent_without_paraphrase_literals():
    """spec: docs/plans/deliver.md#готово — «Готово» 1, триаж G-24:
    description несёт семантику поставки/обновления/деплоя и не содержит
    литералов парафраза «раскатай ядро в X»; инъекция литерала краснит."""
    text = SKILL.read_text("utf-8")
    description = _frontmatter(text)["description"]
    for needle in DESCRIPTION_NEEDLES:
        assert needle in description, f"intent semantics missing: {needle!r}"
    for word in DESCRIPTION_FORBIDDEN:
        assert word not in description.lower(), \
            f"paraphrase literal {word!r} leaked into the description"

    injected = text.replace(
        "Поставка и обновление OntoShip в проекте:",
        "Раскатай ядро в X. Поставка и обновление OntoShip в проекте:", 1)
    assert injected != text
    assert any("paraphrase literal" in error
               for error in _contract_errors(injected))


def test_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the contract reddens on a lost protocol norm, a lost act-contract
    clause, a seeded project fact and on the missing bundle (the base
    commit state); every needle names its own error."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"

    flat = re.sub(r"\s+", " ", text)
    for needle in PROTOCOL_NEEDLES + CONTRACT_NEEDLES:
        mutated = flat.replace(needle, "", 1)
        assert mutated != flat, needle
        errors = _contract_errors(mutated)
        assert any(needle in error for error in errors), (needle, errors)

    factual = text + "\nПример: /home/operator/project.\n"
    assert any("project fact" in error for error in _contract_errors(factual))

    # The base commit carries no bundle: the empty carrier reddens the
    # frontmatter and every protocol clause, not a vacuous pass.
    errors = _contract_errors("")
    assert any("name is not deliver" in error for error in errors)
    assert any(error.startswith("protocol:") for error in errors)
    assert any(error.startswith("act contract:") for error in errors)