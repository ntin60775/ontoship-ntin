#!/usr/bin/env python3
"""Исполнитель механических гейтов паков стандартов OntoShip.

Шаг «Механические гейты пака» скилла ship: конфиги-данные гейтов
установленных паков исполняет ядро в окружении проекта — команда как
список аргументов без shell-интерпретации, рабочий каталог — корень
проекта, код выхода сверяется с `expect_exit` манифеста. Контур: все
гейты зелёные — exit 0 со строкой на гейт и сводкой; красный гейт —
exit 1 с именем гейта, ожидаемым и полученным кодом и выводом команды;
нарушение контракта пака или usage-ошибка — именованный отказ (stderr,
exit 2, stdout пустой), как у валидатора. Паков нет — названный ноль,
exit 0. Вывод в UTF-8 независимо от локали; недоверенный текст (имена
гейтов, вывод команд) редактируется на границе вывода.

Трассировка ниже адресует документы репозитория метода ontoship-ntin;
в проект-потребитель они не ставятся — адреса живут в репозитории
метода (провенанс назван явно, комментарий не врёт).

spec: docs/plans/standards-autoship.md#готово — «Готово» 8: шаг
      механических гейтов пака, конфиги-данные исполняет ядро
spec: docs/plans/standards-autoship.md#ограничения — пак — доверенный
      источник команды; валидатор проверяет схему, не семантику
invariant: docs/plans/core-kb.md#готово — движки метода только stdlib
target: cli-utf8 — вывод в UTF-8 независимо от локали
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from validate_pack import PackError, validate

# Named threshold: a gate longer than this is red with a named reason,
# not a hung pass. The contract names the value (pack-contract.md).
TIMEOUT_S = 600

# Untrusted text at the output boundary: control, C1 and bidi/format
# characters become a visible marker (the pack validator idiom).
REDACT_RE = re.compile(r"[\x00-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e]")


def _redact(text: str) -> str:
    return REDACT_RE.sub("·", text)


def _force_utf8_output() -> None:
    """Вывод CLI — UTF-8 независимо от локали и PYTHONIOENCODING (идиома
    юнита cli-utf8): кириллица и `✓` роняли `print` в C-локали без
    PYTHONUTF8. `errors="backslashreplace"` на обоих потоках сохраняет
    контракт отказа. Поток без `reconfigure` (переопределён тестом) не
    трогается.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def _run_gate(command: list[str], root: Path) -> tuple[int | None, str, str]:
    """Код выхода и вывод команды; None — команда не найдена или таймаут,
    причина третьим элементом. Без shell-интерпретации, в окружении
    проекта."""
    try:
        proc = subprocess.run(command, cwd=root, shell=False,
                              capture_output=True, text=True,
                              encoding="utf-8", errors="backslashreplace",
                              timeout=TIMEOUT_S)
    except FileNotFoundError:
        return None, "", f"команда не найдена: {command[0]}"
    except subprocess.TimeoutExpired:
        return None, "", f"таймаут {TIMEOUT_S} с"
    return proc.returncode, proc.stdout, proc.stderr


def main(argv: list[str] | None = None) -> int:
    _force_utf8_output()
    parser = argparse.ArgumentParser(
        prog="run_gates",
        description="Исполнитель механических гейтов установленных паков.")
    parser.add_argument("project", help="корень проекта с .agents/packs/")
    args = parser.parse_args(argv)
    root = Path(args.project)
    if root.exists() and not root.is_dir():
        print(f"gates: ожидается каталог: {str(root)!r}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"gates: каталог не существует: {str(root)!r}", file=sys.stderr)
        return 2
    packs_root = root / ".agents" / "packs"
    packs = sorted(path for path in packs_root.iterdir() if path.is_dir()) \
        if packs_root.is_dir() else []
    if not packs:
        print("паков нет: гейтов 0")
        return 0
    total = 0
    red = 0
    for pack in packs:
        try:
            name, _type, _version = validate(pack)
        except PackError as e:
            print(f"gates: {_redact(str(e))}", file=sys.stderr)
            return 2
        manifest = json.loads((pack / "manifest.json").read_text("utf-8"))
        for gate in manifest.get("gates", []):
            total += 1
            expected = gate.get("expect_exit", 0)
            code, out, err = _run_gate(gate["command"], root)
            label = _redact(f"{name}/{gate['name']}")
            if code is None:
                red += 1
                print(f"✗ гейт {label}: {_redact(err)}")
                continue
            if code == expected:
                print(f"✓ гейт {label}: exit {code}")
            else:
                red += 1
                print(f"✗ гейт {label}: ожидался exit {expected}, "
                      f"получен {code}")
            for stream_text in (out, err):
                if stream_text.strip():
                    for line in stream_text.splitlines():
                        print(f"    {_redact(line)}")
    if red:
        print(f"гейты паков: {red} из {total} красные")
        return 1
    print(f"✓ гейты паков: {total} пройдено")
    return 0


if __name__ == "__main__":
    sys.exit(main())