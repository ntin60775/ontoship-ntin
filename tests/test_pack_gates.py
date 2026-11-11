"""Contract and behaviour of the pack gate runner (standards-autoship 05).

The core executes the pack gates: ``skills/pack/run_gates.py`` reads the
manifests of the packs installed in ``<project>/.agents/packs/`` and runs
every gate command as an argument list without shell interpretation, in the
project environment, comparing the exit code with ``expect_exit``. The
contour: green — exit 0 with a per-gate line and a summary; a red gate —
exit 1 naming the gate, the expected and the actual code and the command
output; a contract or usage violation — the named refusal of the validator
(stderr, exit 2, empty stdout). No packs — a named zero, exit 0. The output
is UTF-8 regardless of the locale (the cli-utf8 idiom); untrusted text is
redacted at the boundary; a gate longer than the timeout is red with a named
reason.

The marker-gate case is the target test of the ticket's demo path: the gate
falls on the broken toy diff and passes after the fix — the executor reads
the output, a green summary without the read output is not a proof.

spec: docs/plans/standards-autoship.md#готово — «Готово» 8: шаг механических
      гейтов пака, конфиги-данные исполняет ядро в окружении проекта
spec: docs/plans/standards-autoship.md#ограничения — конфиги гейтов пака —
      данные, которые исполняет ядро; валидатор проверяет схему, не семантику
target: standards-autoship 05 demo — гейт умеет падать и проходит после
      правки игрушечного диффа (marker-gate)
invariant: docs/plans/core-kb.md#готово — движки метода только stdlib
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BUNDLE = REPO / "skills" / "pack"
RUNNER = BUNDLE / "run_gates.py"
REFERENCE = BUNDLE / "reference-pack"


def _run(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run([sys.executable, str(RUNNER), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          env=full_env)


def _pack(root: Path, name: str, gates: list[dict]) -> Path:
    """A minimal valid pack with the given gates under the project pack root."""
    pack = root / ".agents" / "packs" / name
    pack.mkdir(parents=True)
    manifest = {"name": name, "type": "team", "version": "1.0.0",
                "gates": gates}
    (pack / "manifest.json").write_text(json.dumps(manifest), "utf-8")
    return pack


def _install_reference(root: Path) -> Path:
    target = root / ".agents" / "packs" / "reference-pack"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REFERENCE, target)
    return target


@pytest.fixture()
def runner():
    """The runner module imported by path, the bundle dir on sys.path."""
    sys.path.insert(0, str(BUNDLE))
    try:
        spec = importlib.util.spec_from_file_location("run_gates", RUNNER)
        module = importlib.util.module_from_spec(spec)
        sys.modules["run_gates"] = module
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path.remove(str(BUNDLE))
        sys.modules.pop("run_gates", None)


def test_runner_is_a_stdlib_bundle_file():
    """spec: docs/plans/standards-autoship.md#готово — исполнитель гейтов
    лежит в бандле pack рядом с валидатором, только stdlib."""
    assert RUNNER.is_file(), "the gate runner is missing from the pack bundle"
    source = RUNNER.read_text("utf-8")
    for line in source.splitlines():
        if line.startswith(("import ", "from ")):
            module = line.split()[1].split(".")[0]
            assert module in sys.stdlib_module_names or module == "validate_pack", \
                f"non-stdlib import {module!r}"


def test_usage_refusals_are_named(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#ограничения — usage-ошибки и
    нарушения контракта — именованный отказ: stderr, exit 2, stdout пустой."""
    no_args = _run([])
    assert no_args.returncode == 2
    assert no_args.stdout == ""
    assert no_args.stderr.strip()

    missing = _run([str(tmp_path / "absent")])
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert "не существует" in missing.stderr

    a_file = tmp_path / "file"
    a_file.write_text("x", "utf-8")
    not_dir = _run([str(a_file)])
    assert not_dir.returncode == 2
    assert not_dir.stdout == ""
    assert "каталог" in not_dir.stderr


def test_no_packs_is_a_named_zero(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — паков нет: шаг
    называет ноль, контур зелёный."""
    result = _run([str(tmp_path)])
    assert result.returncode == 0
    assert "паков нет: гейтов 0" in result.stdout

    (tmp_path / ".agents" / "packs").mkdir(parents=True)
    empty = _run([str(tmp_path)])
    assert empty.returncode == 0
    assert "паков нет: гейтов 0" in empty.stdout


def test_reference_pack_gate_runs_green(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — гейт эталонного пака
    исполняется в окружении проекта, вывод прочитан: строка на гейт, вывод
    команды и зелёная сводка."""
    _install_reference(tmp_path)
    result = _run([str(tmp_path)])
    assert result.returncode == 0, result.stderr
    assert "✓ гейт reference-pack/reference-gate: exit 0" in result.stdout
    assert "reference gate: ok" in result.stdout
    assert "✓ гейты паков: 1 пройдено" in result.stdout


def test_gate_falls_on_the_broken_diff_and_passes_after_the_fix(tmp_path: Path):
    """target: standards-autoship 05 demo — гейт умеет падать и проходит
    после правки: marker-gate красен на игрушечном диффе без маркера и
    зелёный после правки; ожидание — из контракта гейта (expect_exit 0),
    не пересчитано кодом теста."""
    _pack(tmp_path, "toy-pack", [{
        "name": "marker-gate",
        "command": ["python3", "-c",
                    "import pathlib, sys; "
                    "sys.exit(0 if pathlib.Path('marker.txt').is_file() else 1)"],
    }])
    red = _run([str(tmp_path)])
    assert red.returncode == 1
    assert "✗ гейт toy-pack/marker-gate" in red.stdout
    assert "ожидался exit 0, получен 1" in red.stdout
    assert "1 из 1 красные" in red.stdout

    (tmp_path / "marker.txt").write_text("fixed\n", "utf-8")
    green = _run([str(tmp_path)])
    assert green.returncode == 0, green.stdout
    assert "✓ гейт toy-pack/marker-gate: exit 0" in green.stdout
    assert "✓ гейты паков: 1 пройдено" in green.stdout


def test_expect_exit_is_compared_not_assumed(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — код выхода сверяется
    с expect_exit манифеста: ненулевой ожидаемый код — штатный зелёный,
    расхождение — красный гейт."""
    _pack(tmp_path, "exit-pack", [
        {"name": "exit-three", "command": ["python3", "-c", "import sys; sys.exit(3)"],
         "expect_exit": 3},
    ])
    green = _run([str(tmp_path)])
    assert green.returncode == 0, green.stdout
    assert "✓ гейт exit-pack/exit-three: exit 3" in green.stdout

    _pack(tmp_path, "mismatch-pack", [
        {"name": "exit-three", "command": ["python3", "-c", "import sys; sys.exit(3)"],
         "expect_exit": 0},
    ])
    red = _run([str(tmp_path)])
    assert red.returncode == 1
    assert "✗ гейт mismatch-pack/exit-three" in red.stdout
    assert "ожидался exit 0, получен 3" in red.stdout


def test_command_runs_without_shell_interpretation(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#ограничения — команда гейта
    исполняется без shell-интерпретации: метасимволы — литералы аргумента,
    вторая команда не исполняется."""
    _pack(tmp_path, "shell-pack", [
        {"name": "literal", "command": ["echo", "hello; touch pwned"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 0, result.stdout
    assert "hello; touch pwned" in result.stdout
    assert not (tmp_path / "pwned").exists(), "the shell interpreted the command"


def test_command_runs_in_the_project_environment(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — гейты исполняются в
    окружении проекта: рабочий каталог команды — корень проекта."""
    _pack(tmp_path, "cwd-pack", [
        {"name": "cwd", "command": ["python3", "-c", "import os; print(os.getcwd())"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 0, result.stdout
    assert str(tmp_path) in result.stdout


def test_missing_command_is_a_red_gate_not_a_crash(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — ненайденная команда
    гейта — красный гейт с названной причиной, не краш исполнителя."""
    _pack(tmp_path, "absent-pack", [
        {"name": "absent", "command": ["no-such-command-sa05"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 1
    assert "✗ гейт absent-pack/absent" in result.stdout
    assert "команда не найдена" in result.stdout


def test_invalid_manifest_is_the_validator_refusal(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#ограничения — невалидный
    манифест останавливает исполнение именованным отказом валидатора:
    stderr, exit 2, stdout пустой."""
    pack = tmp_path / ".agents" / "packs" / "broken-pack"
    pack.mkdir(parents=True)
    (pack / "manifest.json").write_text(
        json.dumps({"name": "broken-pack", "type": "guild", "version": "1.0.0"}),
        "utf-8")
    result = _run([str(tmp_path)])
    assert result.returncode == 2
    assert result.stdout == ""
    assert "type" in result.stderr


def test_untrusted_output_is_redacted(tmp_path: Path):
    """invariant: docs/plans/core-kb.md#готово — недоверенный текст на
    границе вывода: управляющие символы вывода команды заменяются видимым
    маркером, ANSI-инъекция не проходит."""
    _pack(tmp_path, "ansi-pack", [
        {"name": "ansi", "command": ["python3", "-c",
                                     "print('\\x1b[31mRED\\x1b[0m')"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 0, result.stdout
    assert "\x1b" not in result.stdout
    assert "·[31mRED·[0m" in result.stdout


def test_output_is_utf8_in_the_c_locale(tmp_path: Path):
    """target: cli-utf8 — вывод исполнителя в UTF-8 независимо от локали:
    кириллица и `✓` не крашат прогон в C-локали без PYTHONUTF8. Команда
    гейта пишет UTF-8 байты напрямую: argv остаётся ASCII (входная
    C-локаль с не-ASCII argv — названная граница юнита cli-utf8)."""
    _pack(tmp_path, "utf8-pack", [
        {"name": "кириллица", "command": ["python3", "-c",
                                         "import sys; sys.stdout.buffer.write("
                                         "b'\\xd0\\xbf\\xd1\\x80\\xd0\\xb8\\xd0\\xb2\\xd0\\xb5\\xd1\\x82 "
                                         "\\xe2\\x9c\\x93')"]},
    ])
    result = _run([str(tmp_path)],
                  env={"LC_ALL": "C", "PYTHONUTF8": "0",
                       "PYTHONIOENCODING": "ascii"})
    assert result.returncode == 0, result.stderr
    assert "привет ✓" in result.stdout
    assert "✓ гейты паков: 1 пройдено" in result.stdout


def test_timeout_is_a_red_gate_with_a_named_reason(tmp_path: Path, runner,
                                                   monkeypatch, capsys):
    """spec: docs/plans/standards-autoship.md#готово — гейт дольше таймаута
    — красный с названной причиной; порог — именованная константа."""
    _pack(tmp_path, "slow-pack", [
        {"name": "slow", "command": ["python3", "-c",
                                     "import time; time.sleep(30)"]},
    ])
    monkeypatch.setattr(runner, "TIMEOUT_S", 0.3)
    code = runner.main([str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "✗ гейт slow-pack/slow" in out
    assert "таймаут" in out


def test_two_packs_one_red_names_both_and_the_count(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — гейты всех
    установленных паков исполняются: сводка называет число красных, каждый
    гейт назван своим паком."""
    _pack(tmp_path, "green-pack", [
        {"name": "ok", "command": ["python3", "-c", "print('ok')"]},
    ])
    _pack(tmp_path, "red-pack", [
        {"name": "bad", "command": ["python3", "-c", "import sys; sys.exit(1)"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 1
    assert "✓ гейт green-pack/ok" in result.stdout
    assert "✗ гейт red-pack/bad" in result.stdout
    assert "1 из 2 красные" in result.stdout


def test_gate_stderr_is_shown_on_red(tmp_path: Path):
    """spec: docs/plans/standards-autoship.md#готово — вывод команды гейта
    прочитан исполнителем: stderr красной команды попадает в отчёт."""
    _pack(tmp_path, "err-pack", [
        {"name": "err", "command": ["python3", "-c",
                                    "import sys; print('причина сбоя', file=sys.stderr); sys.exit(1)"]},
    ])
    result = _run([str(tmp_path)])
    assert result.returncode == 1
    assert "причина сбоя" in result.stdout