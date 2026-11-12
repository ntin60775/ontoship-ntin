# 01: Прогон виден на доске — реестр, инструменты, первый выстрел

**Спека:** [chain-live-activity](../../docs/plans/chain-live-activity.md),
«Готово» 1, 2, частично 3–4; решения 1, 2, 5, 6, 7.

**Блокируется:** внешний блокер юнита — тикеты 07 и 09 юнита
`standards-autoship` (общие носители harnesses.md и chain).

**Что построить:** сквозной вертикальный срез в репо плагина
`ontoship-chain-board`: схема реестра `.scratch/board/runs/`
(dispatch- и run-файлы, таблица поле→файл→писатель, терминальные фазы,
idle не жив); host-инструменты `ontoship_run_dispatch` (unit, ticket,
executorSession → runId; уборка того же юнита по updatedAt старше 24 ч,
живые не трогает) и `ontoship_run_update` (runId, phase, boardRoot?,
branch?, worktree?, note; привязка caller к executor.session dispatch,
ttlSec 1800/3600 review; raw fs tmp+rename с уникальным tmp, валидация
boardRoot, ошибка ФС → scope: local); базовая модель `parseRunLease` +
`mergeActivity` (run перебивает dispatch, accepted/done из markdown
перебивает activity, порядок по updatedAt); UI — чип «В работе» с
фазой, шапка «в работе K» (только живые), watch каталога реестра,
таймер свежести ~30 с; сборка build.mjs → client.js.

**Демо-путь:** фикстура фейковых lease (dispatch + update) в
client-тесте: дерево vnode доски показывает карточку «В работе» с
фазой и шапку «в работе 1»; host-тест: вызов dispatch создаёт
dispatch-файл с runId, update пишет run-файл.

ожидание: доска показывает выданный и стартовавший прогон без прозы;
на базе плагина инструментов и модели lease нет — тесты красные.

**Критерии приёмки**:

- [ ] Инструменты и схема — артефакт: лог host-тестов плагина;
      ожидание: dispatch создаёт файл схемы v1 (поля по таблице спеки),
      update пишет run, caller ≠ executor.session → отказ с причиной,
      ошибка ФС boardRoot → scope: local, уборка не трогает живые;
      на базовом коммите плагина `ad4b7d8` тесты падают (инструментов
      нет).
- [ ] Модель и первый выстрел UI — артефакт: логи модельных и
      client-тестов (дерево vnode); ожидание: run перебивает dispatch,
      accepted перебивает activity, карточка «В работе» с фазой и
      шапка K=1 на фейковом lease; на базе `ad4b7d8` тесты падают
      (parseRunLease/mergeActivity отсутствуют).