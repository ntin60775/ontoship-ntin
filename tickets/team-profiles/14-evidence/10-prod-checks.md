# 14 — prod-проверки после merge

Merge: ветка `tp14-triviality` перебазирована на main `3ed9415` и влита
fast-forward в `73d31ce` (2026-11-16). Проверки — на main после merge.

| проверка | команда | результат | лог |
|---|---|---|---|
| полный набор | `pytest -q` | **789 passed** | `10-prod-pytest.log` |
| KB lint | `python3 skills/kb-search/gitmark.py lint --strict` | чисто, код 0 | `11-prod-lint.log` |
| install | `scripts/install.sh --copy /tmp/tp14-prod-install` + `--check` | `ok`/`check: ok`, код 0 | `12-prod-install.log` |

Прод-контур повторяет dev-цифры (789/чисто/ok); расхождений ожидание/факт
нет.
