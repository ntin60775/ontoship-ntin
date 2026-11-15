# Тикет 13 — артефакты фикса tool-schedule у orchestrator

Проба 2026-11-15 на изолированном хосте 3093 (живой GUI PID 3746641 не
перезапускался). Фикс: team v0.2.1 (`eea68d1`, тег), стек `fc645f1`
(пин; после правки P1 — удалён закоммиченный симлинк `node_modules`). Контракт 2 не менялся — правка полноты композиции.

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
- `06b-live-sessions-after-cleanup.txt` — после уборки на хосте 0 сессий,
  пробных сессий 13 нет;
- `07-ntin-dev-pytest.log` — ntin **776 passed** (нормы не менялись);
- `08-ntin-lint.log` — `gitmark lint --strict` чист;
- `01-live-profile-before.sha256`, `09-live-profile-after.sha256` —
  sha256 живого профиля до/после; сравнение на хосте: совпадает (не
  изменён);
- `04-project-baseline.sha256`, `10-project-tree-after.sha256` — sha256
  дерева temp-проекта до/после; сравнение на хосте: совпадает (проба
  его не правила).
- `05b-live-listtools-schedule.txt` — вырезка полного listTools
  `schedule_*` из спилла (в events результат обрезан);
- `09-panel.md` — вердикты панели, P1/P2/P3 и инцидент доставки;
- `11-prod-install-check.log`, `10-prod-checks.log` — prod-проверки
  после merge.

Уборка: четыре пробные сессии 13 удалены; задача снята. Изолированный
хост оставлен для пробы 07 (v0.2.1), живой профиль не менялся.

## Расхождение прохода (названо)

При проверке стека понадобился пин v0.2.1, и team main был преждевременно
слит на `eea68d1` до панели. Оркестратор зафиксировал отклонение от нормы
ship; team main восстановлен `git reset --hard d36d483`, ветка
`tp13-schedule` (`eea68d1`) и тег `v0.2.1` сохранены; dev-прогоны стека до
merge шли с `ONTOSHIP_TEAM_DIR` на team-worktree. Дальнейший merge — после
панели, по норме.
