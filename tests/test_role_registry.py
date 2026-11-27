"""Anchor parity between the role registry and its carriers.

spec: docs/plans/role-registry.md#готово — skills/init/roles.py is the machine
source of the role lists; every carrier (the test tuples, the init skill's
check line, the reference base-set sections) must stay in two-way parity with
it. Parsing is text-based, like the installer array SKILLS; the check-list
parser is reused from tests/test_skill_init.py, not duplicated.

spec: docs/plans/registry-source.md#готово — the config is the single source
of the route values; these tests read it and guard the spec's structural
invariant, so a structurally valid route change stays green.

Every check takes a root parameter (the _parity_errors pattern of
tests/test_install.py): probes mutate copies in a temporary tree, the working
tree is never modified.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

import test_review_roles  # reuse: the reference section parser, not duplicated
import test_skill_init  # reuse: the check-list parser, not duplicated

REPO = Path(__file__).resolve().parent.parent
REGISTRY = "skills/init/roles.py"

# (file, variable, side): which carrier tuple mirrors which registry tuple.
CARRIER_TUPLES = (
    ("tests/test_skill_init.py", "CORE_ROLES", "core"),
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
    ("review-roles-tuple-drops-kb", "tests/test_review_roles.py",
     ', "reviewer-kb")', ')', "misses the reviewer-kb role"),
    ("review-roles-tuple-phantom", "tests/test_review_roles.py",
     ', "reviewer-kb")', ', "reviewer-kb", "auditor")',
     "carries a phantom auditor role"),
    ("skill-check-line-drops-critic", "skills/init/SKILL.md",
     "`critic`, `curator` — с секциями", "`curator` — с секциями",
     "misses the critic role"),
    ("skill-check-line-phantom", "skills/init/SKILL.md",
     "`curator` — с секциями", "`curator`, `auditor` — с секциями",
     "carries a phantom auditor role"),
    ("reference-drops-section", "docs/reference/review-roles.md",
     "### reviewer-code — качество реализации\n", "",
     "miss the reviewer-code role"),
    ("reference-phantom-section", "docs/reference/review-roles.md",
     "## Регламент паков", "### auditor — проба\n\n## Регламент паков",
     "phantom section"),
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
    if not errors and sorted(own) != sorted(other):
        # Only a real duplicate survives the miss/phantom sweep above.
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
    for token in ("def ", "class ", "import ", "lambda ", "print(", "raise "):
        if token in code:
            errors.append(f"registry: roles.py carries executable logic "
                          f"({token.strip()})")
    assigned = re.findall(r"^([A-Za-z_]+) =", code, re.MULTILINE)
    wanted = ["CORE_ROLES", "PANEL_ROLES", "POOL_ROUTES", "ROLE_ROUTES"]
    if sorted(assigned) != wanted:
        errors.append(f"registry: roles.py assigns {assigned or 'nothing'} "
                      "instead of the role tuples and the delivery matrix")
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
        # Same semantics as the reference contract: a role owns a section
        # when its name occurs in the heading, not by an exact header shape.
        headings = list(test_review_roles._h3_sections(reference.read_text("utf-8")))
        for role in panel:
            if not any(role in heading.lower() for heading in headings):
                errors.append(f"parity: the base-set sections of "
                              f"docs/reference/review-roles.md miss the "
                              f"{role} role")
        for heading in headings:
            if not any(role in heading.lower() for role in panel):
                errors.append(f"parity: the base-set sections of "
                              f"docs/reference/review-roles.md name a phantom "
                              f"section {heading!r}")
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
    role tuples and the delivery matrix and nothing executable: only data and
    the origin comment."""
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
    """spec: docs/plans/role-registry.md#готово-2 — each mutation, ordered
    by the plan: a dropped role, a phantom, a duplicate, a broken subset is
    caught and named, not just met with a non-empty error list."""
    source = (REPO / rel).read_text("utf-8")
    assert old in source, f"the probe {probe} no longer matches its carrier"
    errors = _registry_errors(_carriers(tmp_path, **{rel: source.replace(old, new, 1)}))
    assert any(needle in error for error in errors), errors


# critic-consilium («Готово» 2), registry-source («Готово»): the committed
# registry carries the panel roles and a validation pool whose VALUES live in
# the config only. The spec's structural invariant is the independent source
# of the expectation: three pool entries, three distinct models by model part,
# a non-empty level per pool entry; a role level may be absent (the model
# default applies). Pack roles are dynamic (installed-pack manifests) and are
# not listed in this repo's registry.
CONFIG = ".agents/config.toml"
INIT = "skills/init/SKILL.md"
POOL_SIZE = 3
POOL_HEADER = "[validation]"
POOL_ENTRY = re.compile(r'^\s*\{\s*model\s*=\s*"')

# The pool is part of the delivery matrix: the canon carries its routes, the
# bootstrap only checks they are live; drift is reconciled by sync_config.py.
INIT_POOL_NEEDLES = (
    "три различных модели по model-части",
    "`POOL_ROUTES`",
    "с живым `list_subagent_models`",
)


def _route_string(value: object) -> bool:
    """A route is a non-empty `provider/model` pair."""
    if not isinstance(value, str):
        return False
    provider, separator, model = value.partition("/")
    return bool(separator and provider and model)


def _config_data(root: Path) -> tuple[dict | None, list[str]]:
    """The parsed config and its parse errors; None means unreadable."""
    import tomllib

    path = root / CONFIG
    if not path.is_file():
        return None, [f"config: {CONFIG} is missing"]
    try:
        return tomllib.loads(path.read_text("utf-8")), []
    except tomllib.TOMLDecodeError as exc:
        return None, [f"config: {CONFIG} is not TOML ({exc})"]


def _config_errors(root: Path) -> list[str]:
    """Every violated registry-config rule; empty means the registry is sound."""
    data, errors = _config_data(root)
    if data is None:
        return errors
    core = _parsed_tuple((root / REGISTRY).read_text("utf-8"), "CORE_ROLES")
    if core is None:
        return errors + ["config: the registry carries no CORE_ROLES tuple"]
    agents = data.get("agents", {})
    if not isinstance(agents, dict):
        return ["config: the agents table is missing"]
    for role in core:
        section = agents.get(role)
        if not isinstance(section, dict) or not _route_string(section.get("model")):
            errors.append(f"config: the {role} role has no model route section")
    validation = data.get("validation")
    if not isinstance(validation, dict):
        return errors + ["config: the validation pool section [validation] is missing"]
    pool = validation.get("pool")
    if pool is None:
        return errors + ["config: the [validation] section carries no pool list"]
    if not isinstance(pool, list):
        return errors + ["config: the validation pool is not a list"]
    entries = []
    for item in pool:
        if not isinstance(item, dict) or not _route_string(item.get("model")) \
                or not isinstance(item.get("level"), str) or not item["level"]:
            errors.append(f"config: a pool entry without model/level: {item!r}")
            continue
        entries.append((item["model"], item["level"]))
    if len(pool) != POOL_SIZE:
        errors.append(f"config: the validation pool carries {len(pool)} entries, "
                      f"want {POOL_SIZE}")
    if len(entries) != len(set(entries)):
        errors.append("config: the validation pool carries a duplicate entry")
    models = [model.split("/", 1)[1] for model, _level in entries]
    if len(models) != len(set(models)):
        errors.append("config: the validation pool carries the same model twice")
    return errors


def _config_tree(tmp_path: Path, config_text: str) -> Path:
    """A temporary tree with the registry source and a mutated config."""
    root = tmp_path / "tree"
    for rel in (REGISTRY, CONFIG):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        content = config_text if rel == CONFIG else (REPO / rel).read_text("utf-8")
        target.write_text(content, "utf-8")
    return root


def _split_pool(text: str) -> tuple[str, str, str]:
    """(before the pool array, the array, after it): mutations stay inside the
    array whatever order the config's sections take."""
    head, separator, tail = text.partition(f"\n{POOL_HEADER}\n")
    assert separator, "the config has no [validation] section to mutate"
    start = tail.find("pool = [")
    assert start >= 0, "the [validation] section carries no pool array"
    end = tail.find("\n]", start)
    assert end >= 0, "the pool array has no closing bracket line"
    end += len("\n]")
    return f"{head}\n{POOL_HEADER}\n" + tail[:start], tail[start:end], tail[end:]


def _pool_lines(text: str) -> list[str]:
    """The pool-array lines, in config order."""
    return _split_pool(text)[1].splitlines(keepends=True)


def _pool_entry_indexes(lines: list[str]) -> list[int]:
    """The indexes of the pool entries; an unexpected layout fails loudly."""
    indexes = [i for i, line in enumerate(lines) if POOL_ENTRY.match(line)]
    assert len(indexes) == POOL_SIZE, (
        f"the pool array carries {len(indexes)} entry lines, want {POOL_SIZE}: "
        "update the mutation helpers")
    return indexes


def _pool_models(text: str) -> list[str]:
    """The pool routes, in config order, read from the config text."""
    import tomllib

    return [entry["model"] for entry in tomllib.loads(text)["validation"]["pool"]]


def _duplicate_first_pool_entry(text: str) -> str:
    lines = _pool_lines(text)
    index = _pool_entry_indexes(lines)[0]
    lines.insert(index + 1, lines[index])
    prefix, _block, suffix = _split_pool(text)
    return prefix + "".join(lines) + suffix


def _drop_last_pool_entry(text: str) -> str:
    lines = _pool_lines(text)
    del lines[_pool_entry_indexes(lines)[-1]]
    prefix, _block, suffix = _split_pool(text)
    return prefix + "".join(lines) + suffix


def _blank_first_pool_level(text: str) -> str:
    lines = _pool_lines(text)
    index = _pool_entry_indexes(lines)[0]
    lines[index] = re.sub(r'level = "[^"]*"', 'level = ""', lines[index], count=1)
    assert 'level = ""' in lines[index], "the first pool entry carries no level"
    prefix, _block, suffix = _split_pool(text)
    return prefix + "".join(lines) + suffix


def _replace_in_pool(text: str, old: str, new: str) -> str:
    prefix, block, suffix = _split_pool(text)
    assert old in block, f"{old!r} is not a pool value"
    return prefix + block.replace(old, new, 1) + suffix


def _route_providers(text: str) -> list[str]:
    """Every provider the config names, roles and pool."""
    import tomllib

    data = tomllib.loads(text)
    routes = [section["model"] for section in data["agents"].values()
              if isinstance(section, dict) and isinstance(section.get("model"), str)]
    return [route.split("/", 1)[0] for route in routes + _pool_models(text)]


def _cross_provider_same_model(text: str) -> str:
    """The last pool entry gets the first entry's model part on another
    provider: one model on two providers is not distinct (spec)."""
    models = _pool_models(text)
    provider, _separator, model_part = models[0].partition("/")
    other = next((candidate for candidate in _route_providers(text)
                  if candidate != provider), "")
    assert other, "the config names a single provider; the probe needs two"
    return _replace_in_pool(text, models[-1], f"{other}/{model_part}")


def _structurally_valid_route_change(text: str) -> str:
    """The first pool route gets a new model part: distinctness is intact."""
    model = _pool_models(text)[0]
    provider = model.split("/", 1)[0]
    return _replace_in_pool(text, model, f"{provider}/model-probe")


def _replace_flexible(text: str, old: str, new: str) -> str:
    """A whitespace-flexible replacement: the skill prose wraps at 80 columns."""
    pattern = re.escape(old).replace("\\ ", r"\s+")
    return re.sub(pattern, new, text, count=1)


def _init_pool_errors(text: str) -> list[str]:
    """The init bootstrap names the pool invariant — three distinct models by
    model part, the ask from the live catalog, the record after the answer —
    not project routes."""
    layout = test_skill_init._branch(text, "## 5. Бутстрап ролей", "## 6. Проверь")
    if not layout:
        return ["init pool: the bootstrap section is missing"]
    flat = re.sub(r"\s+", " ", layout)
    return [f"init pool: missing {needle!r}"
            for needle in INIT_POOL_NEEDLES if needle not in flat]


def test_init_pool_carries_the_invariant() -> None:
    """spec: docs/plans/registry-source.md#готово — паритет config ↔ init по
    инварианту: три различных модели по model-части, ask из живого каталога,
    запись после ответа; пар пула init не несёт."""
    assert set(INIT_POOL_NEEDLES) <= set(test_skill_init.POOL_NEEDLES)
    assert _init_pool_errors((REPO / INIT).read_text("utf-8")) == []


def test_init_pool_parity_can_fail() -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    потеря любой части структуры пула в init краснит паритет."""
    text = (REPO / INIT).read_text("utf-8")
    assert _init_pool_errors(text) == []
    for old, new in (
        ("три различных модели по model-части", "три маршрута пула"),
        ("с живым `list_subagent_models`", "из конфига"),
    ):
        mutated = _replace_flexible(text, old, new)
        assert mutated != text, old
        assert f"init pool: missing {old!r}" in _init_pool_errors(mutated), old


def test_committed_registry_carries_roles_and_the_pool() -> None:
    """spec: docs/plans/registry-source.md#готово — реестр
    .agents/config.toml несёт секции ролей ядра и пул из трёх различных
    моделей по model-части."""
    assert _config_errors(REPO) == []


# init ships the standard layout for new projects; that table is the delivery
# matrix and must equal the project's own registry (operator rule 2026-11-27):
# the table row and the [agents.<role>] section move in one commit, a
# divergence is red — the shipped matrix is never "a project value".
LAYOUT_ROW = re.compile(
    r"^\|\s*(?P<roles>`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\|\s*`(?P<model>[^`]+)`"
    r"\s*\|\s*`(?P<level>[^`]+)`\s*\|$"
)
LAYOUT_MATRIX_NEEDLES = (
    "обязана совпадать с реестром ролей проекта",
    "меняешь таблицу тем же коммитом",
)


def _init_layout_routes(root: Path) -> dict[str, tuple[str, str]]:
    """role -> (model, level) shipped by init's standard-layout table."""
    routes: dict[str, tuple[str, str]] = {}
    for line in (root / INIT).read_text("utf-8").splitlines():
        row = LAYOUT_ROW.match(line.strip())
        if row is None:
            continue
        for role in re.findall(r"`([^`]+)`", row.group("roles")):
            routes[role] = (row.group("model"), row.group("level"))
    return routes


def _matrix_data(root: Path) -> dict[str, object]:
    """Module-level literals of the init bundle data (`roles.py`)."""
    import ast

    values: dict[str, object] = {}
    tree = ast.parse((root / REGISTRY).read_text("utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                continue
    return values


def _layout_parity_errors(root: Path) -> list[str]:
    """Delivery matrix (init table, roles.py, project registry); empty means equal."""
    data, errors = _config_data(root)
    if data is None:
        return errors
    matrix = _matrix_data(root)
    role_routes = {(role, model, level) for role, model, level in matrix.get("ROLE_ROUTES", ())}
    pool_routes = {(model, level) for model, level in matrix.get("POOL_ROUTES", ())}
    table = _init_layout_routes(root)
    text = (root / INIT).read_text("utf-8")
    artifacts = [f"matrix: init carries no {needle!r}"
                 for needle in LAYOUT_MATRIX_NEEDLES if needle not in text]
    agents = data.get("agents")
    if not isinstance(agents, dict):
        return errors + ["matrix: the registry has no agents table"]
    for role, model, level in sorted(role_routes):
        if table.get(role) != (model, level):
            artifacts.append(
                f"matrix: the init table ships {role} as {table.get(role)}, "
                f"roles.py has {(model, level)}")
        section = agents.get(role)
        if not isinstance(section, dict):
            artifacts.append(f"matrix: the registry has no {role} section")
            continue
        actual = (section.get("model"), section.get("level"))
        if actual != (model, level):
            artifacts.append(
                f"matrix: the {role} role ships {model}/{level}, "
                f"the registry has {actual[0]}/{actual[1]}")
    if not role_routes:
        artifacts.append("matrix: roles.py carries no ROLE_ROUTES")
    validation = data.get("validation")
    pool = validation.get("pool") if isinstance(validation, dict) else None
    actual_pool = {(item.get("model"), item.get("level")) for item in pool or []}
    if actual_pool != pool_routes:
        artifacts.append(
            f"matrix: the validation pool ships {sorted(pool_routes)}, "
            f"the registry has {sorted(actual_pool)}")
    if not pool_routes:
        artifacts.append("matrix: roles.py carries no POOL_ROUTES")
    return errors + artifacts


def test_init_layout_equals_the_project_registry() -> None:
    """invariant: docs/reference/review-roles.md#матрица-поставки — таблица
    init и `.agents/config.toml` (model+level каждой роли ядра) совпадают."""
    assert _layout_parity_errors(REPO) == []


def test_layout_parity_can_fail(tmp_path: Path) -> None:
    """invariant: docs/reference/review-roles.md#матрица-поставки — паритет
    краснит в обе стороны: правка таблицы и правка реестра ловятся."""
    def tree() -> Path:
        for rel in (CONFIG, INIT, REGISTRY):
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPO / rel).read_bytes())
        return tmp_path

    root = tree()
    assert _layout_parity_errors(root) == []

    table = (root / INIT).read_text("utf-8")
    mutated_table = table.replace(
        "| `critic` | `qwen-token-plan-max/qwen4-max` | `xhigh` |",
        "| `critic` | `qwen-token-plan-max/qwen4-max` | `medium` |", 1)
    assert mutated_table != table
    (root / INIT).write_text(mutated_table, "utf-8")
    assert "the init table ships critic as" in " ".join(_layout_parity_errors(root))

    (root / INIT).write_text(table, "utf-8")
    assert _layout_parity_errors(root) == []
    config = (root / CONFIG).read_text("utf-8")
    mutated_config = config.replace(
        '[agents.curator]\nmodel = "qwen-token-plan/qwen3.8-flash"\nlevel = "medium"',
        '[agents.curator]\nmodel = "qwen-token-plan/qwen3.8-flash"\nlevel = "high"', 1)
    assert mutated_config != config
    (root / CONFIG).write_text(mutated_config, "utf-8")
    assert "the curator role ships qwen-token-plan/qwen3.8-flash/medium" \
        in " ".join(_layout_parity_errors(root))


SYNC = "skills/init/sync_config.py"

CONSUMER_OLD = """# consumer registry: old mechanics
[agents.reviewer-spec]
model = "qwen-token-plan-deepseek/deepseek-v4.1-flash-1017"
level = "max"

[agents.critic]
model = "qwen-token-plan-max/qwen4-max-preview"
level = "xhigh"

[agents.reviewer-1c-code]
model = "qwen-token-plan-max/qwen4-max"
level = "high"

[validation]
pool = [
  { model = "deepseek-account/deepseek-flash", level = "max" },
]
"""


def _load_sync(root: Path):
    """The init bundle reconciler, imported from its file."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("init_sync_config", root / SYNC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _config_routes(root: Path, text: str) -> tuple[dict[str, tuple[str, str]], set]:
    """Walk data of a config text: core routes and the pool set."""
    import tomllib

    data = tomllib.loads(text)
    agents = data.get("agents", {})
    routes = {role: (section.get("model"), section.get("level"))
              for role, section in agents.items()}
    pool = {(entry["model"], entry["level"]) for entry in data["validation"]["pool"]}
    return routes, pool


def test_sync_reconciles_a_consumer_registry(tmp_path: Path) -> None:
    """rule: docs/reference/review-roles.md#матрица-поставки — поставка
    приводит механики реестра потребителя к матрице; знания проекта вне
    матрицы остаются байт-в-байт."""
    sync = _load_sync(REPO)
    matrix = _matrix_data(REPO)
    reconciled, changes = sync.reconcile(CONSUMER_OLD)
    assert changes
    routes, pool = _config_routes(tmp_path, reconciled)
    for role, model, level in matrix["ROLE_ROUTES"]:
        assert routes[role] == (model, level), role
    assert pool == set(matrix["POOL_ROUTES"])
    assert routes["reviewer-1c-code"] == ("qwen-token-plan-max/qwen4-max", "high")
    assert "# consumer registry: old mechanics" in reconciled
    assert reconciled.count("[agents.") == 7
    again, changes_again = sync.reconcile(reconciled)
    assert (again, changes_again) == (reconciled, [])


def test_sync_bootstraps_an_empty_registry_cleanly(tmp_path: Path) -> None:
    """rule: docs/reference/review-roles.md#матрица-поставки — приведение
    пустого реестра даёт файл без ведущей пустой строки и без хвостов."""
    sync = _load_sync(REPO)
    for seed in ("", "\n", "  \n"):
        text, changes = sync.reconcile(seed)
        assert text.startswith("[agents.reviewer-spec]\n"), repr(seed)
        assert text.endswith("]\n")
        assert changes
        assert sync.reconcile(text)[1] == []


def test_sync_check_reports_drift(tmp_path: Path) -> None:
    """invariant: docs/reference/review-roles.md#матрица-поставки — --check
    красный на разошедшемся реестре и зелёный после приведения."""
    sync = _load_sync(REPO)
    path = tmp_path / "config.toml"
    path.write_text(CONSUMER_OLD, "utf-8")
    assert sync.main(["sync_config.py", "--check", str(path)]) == 1
    assert sync.main(["sync_config.py", str(path)]) == 0
    assert sync.main(["sync_config.py", "--check", str(path)]) == 0
    assert "reviewer-1c-code" in path.read_text("utf-8")


def _without_pool_section(text: str) -> str:
    head, separator, _tail = text.partition(f"\n{POOL_HEADER}\n")
    assert separator, "the config has no [validation] section to remove"
    return head


def test_registry_config_contract_can_fail(tmp_path: Path) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the registry-config contract rejects a lost pool section, a lost level,
    a duplicate entry, a short pool, the same model twice (one model on two
    providers included) and a lost core role section; every mutation is built
    from the config itself."""
    config = (REPO / CONFIG).read_text("utf-8")
    assert _config_errors(REPO) == []
    core = _parsed_tuple((REPO / REGISTRY).read_text("utf-8"), "CORE_ROLES") or []
    models = _pool_models(config)
    role = core[-1]
    probes = (
        ("no-pool-section", _without_pool_section(config),
         "[validation] is missing"),
        ("lost-level", _blank_first_pool_level(config),
         "without model/level"),
        ("duplicate-entry", _duplicate_first_pool_entry(config),
         "duplicate entry"),
        ("short-pool", _drop_last_pool_entry(config), "want 3"),
        ("same-model-twice", _replace_in_pool(config, models[-1], models[0]),
         "same model twice"),
        ("same-model-cross-provider", _cross_provider_same_model(config),
         "same model twice"),
        ("lost-core-section",
         config.replace(f"[agents.{role}]", f"[agents.{role}-lost]", 1),
         f"the {role} role has no model route section"),
    )
    for name, mutated, needle in probes:
        assert mutated != config, f"the probe {name} must change the config"
        errors = _config_errors(_config_tree(tmp_path / name, mutated))
        assert any(needle in error for error in errors), (name, errors)


def test_a_structurally_valid_route_change_is_green(tmp_path: Path) -> None:
    """spec: docs/plans/registry-source.md#готово — смена model-части
    (провайдер тот же) не краснит инвариант: значения живут в конфиге, тест
    сторожит структуру. На базовом коммите тот же сдвиг был красным — тест
    пинил точный стандарт пула."""
    assert _config_errors(REPO) == []
    config = (REPO / CONFIG).read_text("utf-8")
    mutated = _structurally_valid_route_change(config)
    assert mutated != config
    assert _config_errors(_config_tree(tmp_path, mutated)) == []
