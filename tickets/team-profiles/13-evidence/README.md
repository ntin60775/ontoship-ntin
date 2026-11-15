# Тикет 13 — артефакты фикса tool-schedule у orchestrator

Проба 2026-11-15 на изолированном хосте 3093 (живой GUI PID 3746641 не
перезапускался). Фикс: team v0.2.1 (`eea68d1`, тег), стек `e64f52a`
(пин). Контракт 2 не менялся — правка полноты композиции.

## Файлы

- `01-team-tests.log` — team vitest **124 passed** (включая новый
  контракт: orchestrator несёт `tool-schedule`, executor/scout — нет);
- `02-team-build.log` — team build зелёный (lib не менялся);
- `03-composition-red-on-base.log` — тот же тест на базе v0.2.0
  (`d36d483`): **1 failed / 35 passed** (строки у orchestrator нет);
- `04-stack-tests.log` — стек от пина v0.2.1: **25 passed**
  (`ONTOSHIP_TEAM_DIR` = team-worktree, до merge по норме ship);
- `05-live-orch-wait.json`, `05-live-orch-events.json`,
  `05-live-tool-records.json` — API-сессия `1c-orchestrator` на
  изолированном хосте: `Tool.listTools` содержит
  `schedule_create/schedule_list/schedule_edit/schedule_view`;
  `schedule_create` создал `schedule-bbdc964e…` (`this_session`, active),
  `schedule_view` вернул active, `schedule_edit` delete — `deleted:true`;
- `06-live-schedule-catalog-after.txt` — каталог после пробы: tp13-задач
  нет (гостевые задачи хоста не тронуты);
- `07-ntin-dev-pytest.log` — ntin **776 passed** (нормы не менялись);
- `08-ntin-lint.log` — `gitmark lint --strict` чист;
- `09-panel.md` — вердикты панели и проход правок (после прогона).

Уборка: четыре пробные сессии 13 удалены; задача снята. Изолированный
хост оставлен для пробы 07 (v0.2.1), живой профиль не менялся.
