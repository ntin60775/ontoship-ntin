#!/usr/bin/env python3
"""OntoShip core — generate zcode agent definitions from the role registry.

usage: skills/init/gen_agents.py <project>

The generator travels inside the init skill bundle, so an installed project
runs it as .agents/skills/init/gen_agents.py. The registry is
<project>/.agents/config.toml: one `[agents.<name>]` section
per role with the required key `model`. The generator keeps exactly one
definition per role in <project>/.zcode/agents/<name>.md with `model:` taken
from the config. A definition whose content differs from the rendered one —
a changed model above all — is reported (old and new model) and rewritten;
unchanged definitions are left untouched, so a rerun with an unchanged config
never rewrites files. No config file means nothing to do and nothing written.

Validation distinguishes unknown from invalid: unknown sections or keys warn
on stderr and do not fail; a role without `model`, a non-string or empty
model, an unusable role name, a non-table role section and broken TOML fail
with a named error (exit 1). Stdlib only (tomllib since Python 3.11).
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ConfigError(Exception):
    """Invalid config — refuse with a named error."""


def parse_config(raw: bytes) -> tuple[dict[str, str], list[str]]:
    """Return {role: model} and the warnings for unknown sections or keys.

    Raise ConfigError on anything invalid: broken TOML, a non-table `agents`
    or role section, a role without `model`, a non-string or empty model, an
    unusable role name.
    """
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"broken TOML: {exc}") from exc

    warnings: list[str] = []
    for key, value in data.items():
        if key == "agents":
            continue
        kind = "section" if isinstance(value, dict) else "key"
        warnings.append(f"unknown {kind} {key!r} ignored")

    roles: dict[str, str] = {}
    agents = data.get("agents")
    if agents is None:
        return roles, warnings
    if not isinstance(agents, dict):
        raise ConfigError("[agents] must be a table of role sections")

    for name, section in agents.items():
        if not isinstance(section, dict):
            raise ConfigError(f"[agents.{name}] must be a table")
        if not NAME_RE.match(name):
            raise ConfigError(
                f"invalid role name {name!r}: use letters, digits, '.', '_' or '-'"
            )
        if "model" not in section:
            raise ConfigError(f"[agents.{name}]: required key 'model' is missing")
        model = section["model"]
        if not isinstance(model, str) or not model.strip():
            raise ConfigError(f"[agents.{name}]: 'model' must be a non-empty string")
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in model):
            raise ConfigError(
                f"[agents.{name}]: 'model' must not contain control characters"
            )
        for key in section:
            if key != "model":
                warnings.append(f"[agents.{name}]: unknown key {key!r} ignored")
        roles[name] = model
    return roles, warnings


def render(name: str, model: str) -> str:
    """One definition: frontmatter carries the configured model."""
    quoted = model.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "---\n"
        f'description: Ревью-роль OntoShip "{name}".\n'
        f'model: "{quoted}"\n'
        "---\n"
        "\n"
        f"# {name}\n"
        "\n"
        "Роль ревью OntoShip. Модель назначена конфигом `.agents/config.toml`\n"
        f"(секция `[agents.{name}]`, ключ `model`); чек-лист роли передаётся при\n"
        "запуске панели. Определение производное — перегенерируется\n"
        "`skills/init/gen_agents.py`, не редактируется вручную.\n"
    )


def current_model(path: Path) -> str | None:
    """The `model:` value of an existing definition's frontmatter."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith("model:"):
            value = line[len("model:"):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            return value
    return None


def sync(project: Path) -> int:
    config = project / ".agents" / "config.toml"
    if not config.is_file():
        print(f"no {config.relative_to(project)} — nothing to generate")
        return 0

    try:
        roles, warnings = parse_config(config.read_bytes())
    except ConfigError as exc:
        print(f"gen_agents: {config.relative_to(project)}: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"gen_agents: warning: {warning}", file=sys.stderr)

    agents_dir = project / ".zcode" / "agents"
    for name in sorted(roles):
        target = agents_dir / f"{name}.md"
        expected = render(name, roles[name])
        if target.is_file() and target.read_text(encoding="utf-8") == expected:
            print(f"{name}: ok")
            continue
        if not target.exists():
            print(f"{name}: created")
        else:
            old = current_model(target)
            if old is not None and old != roles[name]:
                print(f"{name}: model {old!r} -> {roles[name]!r} — regenerated")
            else:
                print(f"{name}: content differs — regenerated")
        try:
            if not agents_dir.is_dir():
                agents_dir.mkdir(parents=True)
            target.write_text(expected, encoding="utf-8")
        except OSError as exc:
            print(f"gen_agents: cannot write {target}: {exc}", file=sys.stderr)
            return 1
    print(f"{len(roles)} role(s) in sync")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("usage: skills/init/gen_agents.py <project>", file=sys.stderr)
        return 2
    project = Path(argv[1])
    if not project.is_dir():
        print(f"gen_agents: no such project directory: {project}", file=sys.stderr)
        return 1
    return sync(project)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
