# Тикет 01 — доказательства

Срез `482be7c` (база `7e80cd9`), финальный проход — коммит этого
каталога. Разбор панели — [panel-report.md](panel-report.md).

| артефакт | команда / источник | ожидание | факт |
|---|---|---|---|
| [pytest-green.txt](pytest-green.txt) | `python3 -m pytest tests/ -q` | 0 failed | 860 passed |
| [lint.txt](lint.txt) | `python3 skills/kb-search/gitmark.py lint --strict` | «✓ чисто» | чисто, 64 файла |
| [pytest-red-on-base.txt](pytest-red-on-base.txt) | те же тесты на базе `7e80cd9` | новые иглы красные | 31 failed, 138 passed |
| [verdict-green-on-base.txt](verdict-green-on-base.txt) | `pytest tests/test_skill_ship.py::test_verdict_is_the_role_output` на базе | зелёный на базе | 1 passed |
| [mutation-probe.txt](mutation-probe.txt) | удаление «зацепка ≤10 слов» из `skills/ship/SKILL.md`, `pytest tests/test_skill_ship.py` | контракт краснеет | 11 failed; файл восстановлен |
| [prod-check.txt](prod-check.txt) | `install.sh --copy /tmp/ro01-proj`, `--check`; `--check .` живого чекаута | `check: ok` | copy 11/11 ok, link 11/11 ok |

Расхождения ожидание/факт в проходе: не было.
