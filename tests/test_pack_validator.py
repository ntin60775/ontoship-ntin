"""Spec tests for the pack validator (standards-autoship ticket 01).

The validator enforces the pack contract API v1: the reference pack
passes, every contract mutation is a named refusal (stderr, exit 2,
empty stdout), usage errors share the refusal contour, and the output
stays UTF-8 under a C locale. Expected values come from the contract
reference (skills/pack/references/pack-contract.md), never recomputed
by the validator's own logic.

spec: docs/plans/standards-autoship.md#готово — валидатор краснеет на
      нарушении схемы и проходит на эталоне; негативная матрица
target: cli-utf8 — вывод в UTF-8 независимо от локали (C-локаль)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "skills" / "pack" / "validate_pack.py"
REFERENCE = REPO / "skills" / "pack" / "reference-pack"


def _run(pack: Path, *extra: str, env: dict | None = None):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(pack), *extra],
        capture_output=True, text=True, encoding="utf-8", env=env)


def _copy_reference(tmp_path: Path, name: str = "reference-pack") -> Path:
    pack = tmp_path / name
    shutil.copytree(REFERENCE, pack)
    return pack


def _manifest(pack: Path) -> dict:
    return json.loads((pack / "manifest.json").read_text(encoding="utf-8"))


def _write_manifest(pack: Path, manifest: dict) -> None:
    (pack / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _mutate(pack: Path, change) -> None:
    manifest = _manifest(pack)
    change(manifest)
    _write_manifest(pack, manifest)


def test_reference_pack_is_valid(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — эталон проходит."""
    pack = _copy_reference(tmp_path)
    result = _run(pack)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "✓ пак reference-pack (team, 1.0.0) валиден"
    assert result.stderr == ""


def test_minimal_manifest_without_optional_keys(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: standards/roles/gates необязательны."""
    pack = _copy_reference(tmp_path, name="reference")
    _write_manifest(pack, {"name": "reference", "type": "stack",
                           "version": "0.1.0"})
    result = _run(pack)
    assert result.returncode == 0, result.stderr
    assert "✓ пак reference (stack, 0.1.0) валиден" in result.stdout


def _drop(key):
    return lambda m: m.pop(key)


def _set(key, value):
    return lambda m: m.__setitem__(key, value)


MUTATIONS = [
    ("unknown_key", _set("extra", 1), "неизвестные ключи"),
    ("no_name", _drop("name"), "нет обязательного ключа name"),
    ("empty_name", _set("name", ""), "name — [a-z0-9-]"),
    ("bad_name_chars", _set("name", "Reference!"), "name — [a-z0-9-]"),
    ("no_type", _drop("type"), "нет обязательного ключа type"),
    ("bad_type", _set("type", "contour"), "type — team или stack"),
    ("no_version", _drop("version"), "нет обязательного ключа version"),
    ("bad_version", _set("version", "1.0"), "version — MAJOR.MINOR.PATCH"),
    ("standards_not_list", _set("standards", "standards/reference-standards.md"),
     "standards — список"),
    ("standards_missing_file", _set("standards", ["standards/none.md"]),
     "файл не существует"),
    ("standards_not_md", _set("standards", ["standards/x.txt"]),
     "ожидается .md"),
    ("standards_escape", _set("standards", ["../escape.md"]), "без '..'"),
    ("standards_absolute", _set("standards", ["/etc/passwd"]),
     "относительный"),
    ("roles_not_list", _set("roles", {}), "roles — список"),
    ("role_not_object", _set("roles", ["x"]), "роль — объект"),
    ("role_unknown_key",
     _set("roles", [{"name": "reviewer-reference-code",
                     "checklist": "roles/reference-code.md", "area": "код"}]),
     "неизвестные ключи"),
    ("role_bad_name",
     _set("roles", [{"name": "reviewer-code",
                     "checklist": "roles/reference-code.md"}]),
     "имя роли"),
    ("role_missing_checklist",
     _set("roles", [{"name": "reviewer-reference-code"}]),
     "обязательные ключи name и checklist"),
    ("role_checklist_missing",
     _set("roles", [{"name": "reviewer-reference-code",
                     "checklist": "roles/none.md"}]),
     "файл не существует"),
    ("gates_not_list", _set("gates", {}), "gates — список"),
    ("gate_not_object", _set("gates", ["x"]), "гейт — объект"),
    ("gate_unknown_key",
     _set("gates", [{"name": "g", "command": ["true"], "shell": True}]),
     "неизвестные ключи"),
    ("gate_no_name", _set("gates", [{"command": ["true"]}]),
     "обязательные ключи name и command"),
    ("gate_empty_command", _set("gates", [{"name": "g", "command": []}]),
     "command — непустой список строк"),
    ("gate_command_not_strings",
     _set("gates", [{"name": "g", "command": [1, 2]}]),
     "command — непустой список строк"),
    ("gate_exit_not_int",
     _set("gates", [{"name": "g", "command": ["true"], "expect_exit": "0"}]),
     "expect_exit — целое число"),
    ("gate_exit_bool",
     _set("gates", [{"name": "g", "command": ["true"], "expect_exit": True}]),
     "expect_exit — целое число"),
]


@pytest.mark.parametrize("label,change,reason", MUTATIONS,
                         ids=[m[0] for m in MUTATIONS])
def test_contract_mutations_are_named_refusals(tmp_path: Path, label: str,
                                               change, reason: str) -> None:
    """spec: docs/plans/standards-autoship.md#готово — каждая мутация
    контракта отвергается именованным отказом (stderr, exit 2, stdout пуст)."""
    pack = _copy_reference(tmp_path)
    before = (pack / "manifest.json").read_text(encoding="utf-8")
    _mutate(pack, change)
    assert (pack / "manifest.json").read_text(encoding="utf-8") != before, \
        "the mutation must change the manifest"
    result = _run(pack)
    assert result.returncode == 2, f"{label}: {result.stdout} {result.stderr}"
    assert result.stdout == "", f"{label}: stdout must stay empty"
    assert reason in result.stderr, f"{label}: {result.stderr}"


def test_missing_manifest_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест обязателен."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").unlink()
    result = _run(pack)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "manifest.json не существует" in result.stderr


def test_broken_json_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест должен быть JSON-объектом (битый JSON)."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").write_text("{not json", encoding="utf-8")
    result = _run(pack)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "не JSON" in result.stderr


def test_non_object_manifest_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест должен быть JSON-объектом (не объект)."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").write_text("[]", encoding="utf-8")
    result = _run(pack)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "JSON-объект" in result.stderr


def test_directory_name_mismatch_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: имя каталога совпадает с name манифеста."""
    pack = _copy_reference(tmp_path, name="other")
    result = _run(pack)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "не совпадает с именем каталога" in result.stderr


def test_usage_errors_share_the_refusal_contour(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: usage-ошибки тем же контуром отказа."""
    no_args = subprocess.run([sys.executable, str(VALIDATOR)],
                             capture_output=True, text=True, encoding="utf-8")
    assert no_args.returncode == 2
    missing = _run(tmp_path / "nowhere")
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert "каталог не существует" in missing.stderr


def test_output_is_utf8_under_c_locale(tmp_path: Path) -> None:
    """target: cli-utf8 — вывод в UTF-8 при LC_ALL=C без PYTHONUTF8."""
    env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0",
           "PYTHONCOERCECLOCALE": "0"}
    pack = _copy_reference(tmp_path)
    good = _run(pack, env=env)
    assert good.returncode == 0, good.stderr
    assert "✓ пак reference-pack" in good.stdout
    assert "Traceback" not in good.stderr
    _mutate(pack, _set("type", "contour"))
    bad = _run(pack, env=env)
    assert bad.returncode == 2
    assert bad.stdout == ""
    assert "type — team или stack" in bad.stderr
    assert "Traceback" not in bad.stderr