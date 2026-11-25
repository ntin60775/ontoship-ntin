"""Ticket 01 evidence: the config is the single source of values, the tests
guard the spec's structural invariant.

Run from the repo root:
    git show 6a75096:tests/test_role_registry.py > /tmp/base_trr.py
    python3 tickets/registry-source/01-evidence/probes.py

Method: import the shipped test modules and the base-revision module, build
every mutation from the config text itself, print the full checker output.
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

repo = Path.cwd().resolve()
sys.path.insert(0, str(repo / "tests"))


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


current = load("current_trr", str(repo / "tests/test_role_registry.py"))
current.REPO = repo
base = load("base_trr", "/tmp/base_trr.py")
base.REPO = repo

config = (repo / ".agents" / "config.toml").read_text("utf-8")


def tree_with(text: str) -> Path:
    root = Path(tempfile.mkdtemp()) / "tree"
    (root / "skills" / "init").mkdir(parents=True)
    (root / ".agents").mkdir(parents=True)
    (root / ".agents" / "config.toml").write_text(text, "utf-8")
    (root / "skills" / "init" / "roles.py").write_text(
        (repo / "skills" / "init" / "roles.py").read_text("utf-8"), "utf-8")
    return root


print("== green probe: first pool model part -> '<provider>/model-probe' ==")
mutated = current._structurally_valid_route_change(config)
slice_errors = current._config_errors(tree_with(mutated))
print("slice _config_errors:", slice_errors or "[] (green)")
print("base  _config_errors:", base._config_errors(tree_with(mutated)))
print()

print("== config-built mutation probes (full checker output) ==")
core = current._parsed_tuple((repo / "skills" / "init" / "roles.py").read_text("utf-8"),
                             "CORE_ROLES")
models = current._pool_models(config)
role = core[-1]
probes = (
    ("no-pool-section", current._without_pool_section(config)),
    ("lost-level", current._blank_first_pool_level(config)),
    ("duplicate-entry", current._duplicate_first_pool_entry(config)),
    ("short-pool", current._drop_last_pool_entry(config)),
    ("same-model-twice", current._replace_in_pool(config, models[-1], models[0])),
    ("same-model-cross-provider", current._cross_provider_same_model(config)),
    ("lost-core-section",
     config.replace(f"[agents.{role}]", f"[agents.{role}-lost]", 1)),
)
for name, text in probes:
    print(f"{name}: {current._config_errors(tree_with(text))}")
print()

print("== init parity: every structural clause is load-bearing ==")
init_text = (repo / "skills" / "init" / "SKILL.md").read_text("utf-8")
print("clean:", current._init_pool_errors(init_text) or "[] (green)")
for old, new in (
    ("три различных модели по model-части", "три маршрута пула"),
    ("варианты — из живого `list_subagent_models`", "варианты — из конфига"),
    ("запись — после ответа оператора", "запись без ask"),
):
    changed = current._replace_flexible(init_text, old, new)
    print(f"mutation {old[:40]!r}: {current._init_pool_errors(changed)}")
print()

print("== test_skill_critic: pool invariant and no-hardcode ==")
critic = load("current_critic", str(repo / "tests/test_skill_critic.py"))
routes = critic._pool_models()
print("config pool:", routes)
print("distinct:", critic._pool_errors(routes) or "[] (green)")
print("empty pool:", critic._pool_errors(()))
print("duplicate route:", critic._pool_errors((routes[0], routes[0], routes[1])))
provider, _separator, model_part = routes[0].partition("/")
print("same model, other provider:",
      critic._pool_errors((routes[0], f"other-provider/{model_part}", routes[2])))
critic_text = (repo / "skills" / "critic" / "SKILL.md").read_text("utf-8")
print("skill hardcodes no route:",
      critic._hardcoded_pool_errors(critic_text, routes) or "[] (green)")
planted = critic_text + f"\nМаршрут члена: `{routes[0]}`.\n"
print("planted route:", critic._hardcoded_pool_errors(planted, routes))
print()

print("== robustness: a section appended after the pool does not disturb a probe ==")
appended = config + '\n[agents.extra]\nmodel = "x-provider/x-model"\n'
print("short-pool on the appended config:",
      current._config_errors(tree_with(current._drop_last_pool_entry(appended))))
