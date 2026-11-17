# Evidence тикета 06 «Релиз core v0.7.0»

Юнит core-team-boundaries, спека «Готово» 6 (решение 6, триаж
G14/G18/S4). База исполнения — main `d41dd87` (после приёмки 05/07);
база нарезки `88c8825` — историческая, красные факты сняты на ней.

- [01-release.md](01-release.md) — карта релиза: тег, push, пробы,
  записи отсрочки и стека.
- [02-red-base.md](02-red-base.md) — базовые факты: тега нет, состав
  11 на базе нарезки, chain-команды в блоке AGENTS.md, записей нет.
- 03-checks.md — проверки релиза (после merge и тегирования):
  ls-remote, чистая установка из тега (10 бандлов, check: ok),
  selfhost повторный init (diff AGENTS.md + тест managed-block).
- 04-panel.md — отчёт ревью-панели.
- install-from-tag.log — лог установки и check из дерева тега.
- selfhost-init.diff — diff AGENTS.md повторного init (ожидание: 0).