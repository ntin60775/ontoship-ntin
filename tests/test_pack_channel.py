"""Spec tests for the installer pack channel (standards-autoship ticket 02).

The channel installs one validated pack per run into
<project>/.agents/packs/<name>: link by default, --copy detached,
--dry-run without writes; the source must pass the pack contract
validator before any write, the name comes from the manifest. --check
validates installed packs by the contract and names every invalid pack.
Expected behavior comes from the ticket and the pack contract, not from
the installer's own wording.

spec: docs/plans/standards-autoship.md#готово — канал паков установщика:
      установка copy/link, отказ на невалидном манифесте, --check
      валидирует манифесты и называет пропуски
spec: docs/plans/standards-autoship.md#готово — массив SKILLS ядра не
      меняется: пак не становится бандлом ядра
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "scripts" / "install.sh"
REFERENCE = REPO / "skills" / "pack" / "reference-pack"


def _install(*args: str):
    return subprocess.run(["bash", str(INSTALL), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=120, cwd=REPO)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    return root


def _broken_pack(tmp_path: Path) -> Path:
    # Каталог совпадает с name манифеста: первая проверка, которая должна
    # сработать, — тип, а не имя каталога.
    pack = tmp_path / "reference-pack"
    shutil.copytree(REFERENCE, pack)
    manifest = pack / "manifest.json"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace('"team"', '"contour"'),
        encoding="utf-8")
    return pack


def test_pack_link_install_and_idempotence(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — канал ставит пак
    link-режимом и идемпотентен."""
    first = _install("--pack", str(REFERENCE), str(project))
    assert first.returncode == 0, first.stderr
    assert "linked pack reference-pack" in first.stdout
    target = project / ".agents" / "packs" / "reference-pack"
    assert target.is_symlink()
    assert target.resolve() == REFERENCE.resolve()
    assert (target / "manifest.json").is_file()
    second = _install("--pack", str(REFERENCE), str(project))
    assert second.returncode == 0, second.stderr
    assert "unchanged pack reference-pack" in second.stdout


def test_pack_copy_install_is_detached(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — copy-режим канала."""
    result = _install("--copy", "--pack", str(REFERENCE), str(project))
    assert result.returncode == 0, result.stderr
    assert "copied pack reference-pack" in result.stdout
    target = project / ".agents" / "packs" / "reference-pack"
    assert target.is_dir() and not target.is_symlink()
    assert (target / "manifest.json").is_file()
    assert (target / "roles" / "reference-code.md").is_file()
    assert not list(target.rglob("__pycache__"))
    again = _install("--copy", "--pack", str(REFERENCE), str(project))
    assert "unchanged pack reference-pack" in again.stdout


def test_installed_pack_dir_matches_manifest_name(tmp_path: Path,
                                                  project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — каталог цели равен
    name манифеста. Контракт требует равенства имени каталога-источника и
    name, поэтому источник имени (манифест vs каталог) наблюдательно не
    отличим; тест доказывает равенство цели манифесту, не источник имени."""
    import json
    source = tmp_path / "reference-pack"
    shutil.copytree(REFERENCE, source)
    expected = json.loads(
        (source / "manifest.json").read_text(encoding="utf-8"))["name"]
    result = _install("--pack", str(source), str(project))
    assert result.returncode == 0, result.stderr
    assert f"linked pack {expected}" in result.stdout
    assert (project / ".agents" / "packs" / expected).exists()


def test_invalid_source_installs_nothing(tmp_path: Path,
                                         project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — отказ на невалидном
    манифесте именованный, до записи."""
    broken = _broken_pack(tmp_path)
    result = _install("--pack", str(broken), str(project))
    assert result.returncode == 1
    assert "pack refused by contract" in result.stderr
    assert "team или stack" in result.stderr
    assert not (project / ".agents" / "packs").exists()


def test_pack_channel_does_not_install_skills(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — канал паков отделён
    от канала скиллов."""
    result = _install("--pack", str(REFERENCE), str(project))
    assert result.returncode == 0, result.stderr
    assert not (project / ".agents" / "skills").exists()


def test_dry_run_pack_writes_nothing(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — dry-run канала без
    записи."""
    result = _install("--dry-run", "--pack", str(REFERENCE), str(project))
    assert result.returncode == 0, result.stderr
    assert "would link pack reference-pack" in result.stdout
    assert not (project / ".agents").exists()


def test_pack_usage_errors(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — usage-контур
    канала."""
    no_source = _install("--pack")
    assert no_source.returncode == 2
    assert "--pack expects a <source>" in no_source.stderr
    empty_source = _install("--pack", "", str(project))
    assert empty_source.returncode == 2
    assert "non-empty <source>" in empty_source.stderr
    assert not (project / ".agents").exists()
    twice = _install("--pack", str(REFERENCE), "--pack", str(REFERENCE),
                     str(project))
    assert twice.returncode == 2
    assert "--pack given twice" in twice.stderr
    with_check = _install("--check", "--pack", str(REFERENCE), str(project))
    assert with_check.returncode == 2
    assert "mutually exclusive" in with_check.stderr
    not_a_dir = _install("--pack", str(project / "missing"), str(project))
    assert not_a_dir.returncode == 2
    assert "not a pack directory" in not_a_dir.stderr


def test_check_names_a_non_directory_packs_root(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — --check называет
    пропуски: не-каталог на месте packs — drift, не молчаливый ok."""
    assert _install(str(project)).returncode == 0
    agents = project / ".agents"
    (agents / "packs").write_text("not a directory\n", encoding="utf-8")
    result = _install("--check", str(project))
    assert result.returncode == 1
    assert "drift: packs: not a directory" in result.stderr
    assert "check: 1 pack(s) drifted" in result.stderr


def test_check_report_stays_line_based_for_wild_names(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — имя с ФС недоверено:
    управляющие символы заменяются, отчёт остаётся построчным."""
    assert _install(str(project)).returncode == 0
    packs = project / ".agents" / "packs"
    packs.mkdir(parents=True)
    wild = packs / "we\nird"
    wild.mkdir()
    result = _install("--check", str(project))
    assert result.returncode == 1
    drift_lines = [line for line in result.stderr.splitlines()
                   if line.startswith("drift: pack ")]
    assert len(drift_lines) == 1
    assert "we·ird" in drift_lines[0]


def test_link_refuses_to_replace_a_copy(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — предполётный отказ
    канала: link не заменяет detached-копию."""
    assert _install("--copy", "--pack", str(REFERENCE),
                    str(project)).returncode == 0
    result = _install("--pack", str(REFERENCE), str(project))
    assert result.returncode == 1
    assert "refusing to replace a non-symlink" in result.stderr


def test_check_validates_installed_packs(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — --check валидирует
    манифесты установленных паков."""
    assert _install(str(project)).returncode == 0
    assert _install("--pack", str(REFERENCE), str(project)).returncode == 0
    result = _install("--check", str(project))
    assert result.returncode == 0, result.stderr
    assert "ok pack reference-pack" in result.stdout
    assert "check: ok" in result.stdout


def test_check_names_a_broken_pack(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — --check называет
    пропуски: невалидный пак — drift с причиной, exit 1."""
    assert _install(str(project)).returncode == 0
    assert _install("--copy", "--pack", str(REFERENCE),
                    str(project)).returncode == 0
    manifest = project / ".agents" / "packs" / "reference-pack" / "manifest.json"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace('"team"', '"contour"'),
        encoding="utf-8")
    result = _install("--check", str(project))
    assert result.returncode == 1
    assert "drift: pack reference-pack:" in result.stderr
    assert "team или stack" in result.stderr
    assert "check: 1 pack(s) drifted" in result.stderr


def test_check_without_packs_stays_ok(project: Path) -> None:
    """spec: docs/plans/standards-autoship.md#готово — паки опциональны:
    нет каталога — нет проверок паков."""
    assert _install(str(project)).returncode == 0
    result = _install("--check", str(project))
    assert result.returncode == 0, result.stderr
    assert "check: ok" in result.stdout
    assert "ok pack reference-pack" not in result.stdout


def test_skills_array_unchanged_by_pack_channel() -> None:
    """spec: docs/plans/standards-autoship.md#готово — массив SKILLS ядра
    не меняется каналом паков; состав выводится из массива SKILLS,
    паритет сторожит test_install. core-team-boundaries 03: chain выведен
    из ядра — литерал несёт состав без него; deliver 01: состав несёт
    deliver."""
    source = INSTALL.read_text(encoding="utf-8")
    assert "readonly SKILLS=(kb-search kb-curate init grilling to-tickets " \
        "ship testing critic onto-doc pack deliver)" in source
