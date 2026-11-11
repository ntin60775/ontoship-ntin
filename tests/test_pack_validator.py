"""Spec tests for the pack validator (standards-autoship ticket 01).

The validator enforces the pack contract API v1: the reference pack
passes, every contract mutation is a named refusal (stderr, exit 2,
empty stdout), usage errors share the refusal contour, untrusted text
is redacted, and the output stays UTF-8 under a C locale. Expected
values come from the contract reference
(skills/pack/references/pack-contract.md), never recomputed by the
validator's own logic.

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


def _run(pack: Path, env: dict | None = None):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(pack)],
        capture_output=True, text=True, encoding="utf-8", env=env,
        timeout=60)


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


def _assert_refusal(result, reason: str) -> None:
    assert result.returncode == 2, f"{result.stdout} {result.stderr}"
    assert result.stdout == "", "stdout must stay empty on refusal"
    assert reason in result.stderr, result.stderr


def test_reference_pack_is_valid(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — эталон проходит."""
    pack = _copy_reference(tmp_path)
    result = _run(pack)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "✓ пак reference-pack (team, 1.0.0) валиден"
    assert result.stderr == ""


def test_minimal_manifest_without_optional_keys(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт:
    standards/roles/gates необязательны."""
    pack = _copy_reference(tmp_path, name="reference")
    _write_manifest(pack, {"name": "reference", "type": "stack",
                           "version": "0.1.0"})
    result = _run(pack)
    assert result.returncode == 0, result.stderr
    assert "✓ пак reference (stack, 0.1.0) валиден" in result.stdout


def test_gate_without_expect_exit_is_valid(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт:
    expect_exit необязателен, по умолчанию 0."""
    pack = _copy_reference(tmp_path)
    _mutate(pack, lambda m: m["gates"][0].pop("expect_exit"))
    result = _run(pack)
    assert result.returncode == 0, result.stderr


def _drop(key):
    return lambda m: m.pop(key)


def _set(key, value):
    return lambda m: m.__setitem__(key, value)


# Fragments are contract literals (pack-contract.md), not validator
# message wording: rephrasing a refusal without behavior change must
# not redden the suite.
MUTATIONS = [
    ("unknown_key", _set("extra", 1), "неизвестные ключи"),
    ("no_name", _drop("name"), "нет обязательного ключа name"),
    ("empty_name", _set("name", ""), "[a-z0-9]+(-[a-z0-9]+)*"),
    ("bad_name_chars", _set("name", "Reference!"), "[a-z0-9]+(-[a-z0-9]+)*"),
    ("no_type", _drop("type"), "нет обязательного ключа type"),
    ("bad_type", _set("type", "contour"), "team или stack"),
    ("no_version", _drop("version"), "нет обязательного ключа version"),
    ("bad_version", _set("version", "1.0"), "MAJOR.MINOR.PATCH"),
    ("version_unicode_digits", _set("version", "1.٠.0"), "MAJOR.MINOR.PATCH"),
    ("standards_not_list", _set("standards", "standards/reference-standards.md"),
     "standards — список"),
    ("standards_not_string", _set("standards", [5]), "путь — непустая строка"),
    ("standards_empty_string", _set("standards", [""]),
     "путь — непустая строка"),
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
     "reviewer-<kontur>-<aspect>"),
    ("role_missing_checklist",
     _set("roles", [{"name": "reviewer-reference-code"}]),
     "обязательные ключи name и checklist"),
    ("role_checklist_not_string",
     _set("roles", [{"name": "reviewer-reference-code", "checklist": 5}]),
     "путь — непустая строка"),
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
    ("gate_empty_name",
     _set("gates", [{"name": "", "command": ["true"]}]),
     "name — непустая строка"),
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
    _assert_refusal(_run(pack), reason)


def test_symlink_out_of_pack_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: цель
    внутри пака; симлинк наружу не проходит."""
    pack = _copy_reference(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("# outside\n", encoding="utf-8")
    link = pack / "standards" / "link.md"
    link.symlink_to(outside)
    _mutate(pack, _set("standards", ["standards/link.md"]))
    _assert_refusal(_run(pack), "цель вне пака")


def test_missing_manifest_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест
    обязателен."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").unlink()
    _assert_refusal(_run(pack), "manifest.json не существует")


def test_broken_json_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест
    должен быть JSON-объектом (битый JSON)."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").write_text("{not json", encoding="utf-8")
    _assert_refusal(_run(pack), "не JSON")


def test_non_object_manifest_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: манифест
    должен быть JSON-объектом (не объект)."""
    pack = _copy_reference(tmp_path)
    (pack / "manifest.json").write_text("[]", encoding="utf-8")
    _assert_refusal(_run(pack), "JSON-объект")


@pytest.mark.skipif(os.geteuid() == 0, reason="root читает chmod 000")
def test_unreadable_manifest_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — I/O-ошибка чтения
    манифеста — именованный отказ, не трейсбек."""
    pack = _copy_reference(tmp_path)
    manifest = pack / "manifest.json"
    manifest.chmod(0o000)
    try:
        _assert_refusal(_run(pack), "не читается")
    finally:
        manifest.chmod(0o644)


def test_directory_name_mismatch_is_a_named_refusal(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — контракт: имя
    каталога совпадает с name манифеста."""
    pack = _copy_reference(tmp_path, name="other")
    _assert_refusal(_run(pack), "не совпадает с именем каталога")


def test_refusal_redacts_untrusted_text(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — текст манифеста
    недоверен: управляющие символы не попадают в stderr сырыми."""
    pack = _copy_reference(tmp_path)
    _mutate(pack, _set("standards", ["\x1b[31mRED.md\nforged: line"]))
    result = _run(pack)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "\x1b" not in result.stderr, "ANSI injection into stderr"
    assert "\nforged" not in result.stderr, "forged line into stderr"


def test_usage_errors_share_the_refusal_contour(tmp_path: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — usage-ошибки тем же
    контуром отказа (stderr, exit 2, stdout пуст)."""
    no_args = subprocess.run([sys.executable, str(VALIDATOR)],
                             capture_output=True, text=True,
                             encoding="utf-8", timeout=60)
    assert no_args.returncode == 2
    assert no_args.stdout == ""
    assert no_args.stderr != ""
    missing = _run(tmp_path / "nowhere")
    _assert_refusal(missing, "каталог не существует")
    file_arg = _run(REPO / "skills" / "README.md")
    _assert_refusal(file_arg, "ожидается каталог")


def test_output_is_utf8_under_c_locale(tmp_path: Path) -> None:
    """target: cli-utf8 — вывод в UTF-8 при LC_ALL=C без PYTHONUTF8."""
    env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0",
           "PYTHONCOERCECLOCALE": "0"}
    # PYTHONIOENCODING снят: иначе тест зеленеет и без UTF-8-гарда
    env.pop("PYTHONIOENCODING", None)
    pack = _copy_reference(tmp_path)
    good = _run(pack, env=env)
    assert good.returncode == 0, good.stderr
    assert "✓ пак reference-pack" in good.stdout
    assert "Traceback" not in good.stderr
    _mutate(pack, _set("type", "contour"))
    bad = _run(pack, env=env)
    assert bad.returncode == 2
    assert bad.stdout == ""
    assert "team или stack" in bad.stderr
    assert "Traceback" not in bad.stderr