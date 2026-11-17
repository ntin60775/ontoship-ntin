# Evidence тикета 06 «Релиз core v0.7.0»

Юнит core-team-boundaries, спека «Готово» 6 (решение 6, триаж
G18/S4). База исполнения — main `d41dd87` (после приёмки 05/07);
база нарезки `88c8825` — историческая, красные факты критериев 1–3
сняты на ней, записей 4/5 — на `d41dd87`.

Существуют в срезе:

- [01-release.md](01-release.md) — карта релиза: план тега/push/проб,
  записи отсрочки и стека, порядок закрытия юнита (post-tag).
- [02-red-base.md](02-red-base.md) — базовые факты: тега нет, состав
  11 на базе нарезки, chain-команды в блоке AGENTS.md, записей нет.
- [04-panel.md](04-panel.md) — отчёт ревью-панели (один прогон).
- [core-suite.log](core-suite.log) — pytest ядра на срезе.
- [lint.log](lint.log) — lint --strict ядра на срезе.

Вносит post-tag коммит main (хроника релиза), в дереве тега
отсутствуют:

- 03-checks.md — проверки релиза: ls-remote (main + тег), лог чистой
  установки из тега (10 бандлов, check: ok), selfhost повторный init
  (diff AGENTS.md 0 + тест managed-block).
- install-from-tag.log — лог установки и check из дерева тега.
- selfhost-init.diff — diff AGENTS.md повторного init (ожидание: 0).
