# Стартовый промпт — тикет 02 юнита deliver (реестр)

Исполняй тикет 02 «Реестр DSH-нативен» юнита `deliver` через скилл
`ship` — один тикет за запуск, полный контур от worktree до merge и
автоприёмки. Контур тикета — репо consumer-registry, не ядро; сессия
корневая в ядре, потому что носитель норм — ядро.

## Прочитай до работы (порядок)

1. `/home/prog7/home/dev/contrib/forks/ontoship-ntin/docs/ops/continue.md`
   — абзац «Открыт юнит deliver» и «Факты окружения».
2. `/home/prog7/home/dev/contrib/forks/ontoship-ntin/docs/plans/deliver.md`
   — спека: решения 3–4, 7, «Готово» 5, рамки G-8 (схема: поля/const/
   required неизменны, путевые литералы правятся), тривиальное
   «бандл самонесущий».
3. `/home/prog7/home/dev/contrib/forks/ontoship-ntin/tickets/deliver/02-registry-dsh.md`
   — твой тикет: критерии, демо-путь, ограничения.
4. `/home/prog7/home/dev/contrib/forks/ontoship-ntin/tickets/deliver/00-projection-report.md`
   — нормы триажа G-8, G-20 (идемпотентный старт), G-21 (grep zcode
   пуст), G-27 (предупреждение о потере файла).
5. `/home/prog7/home/dev/contrib/forks/ontoship-ntin/tickets/deliver/handoff-parallel-01-02.md`
   — разделение файлов, маршруты, бюджет, точки остановки.
6. Загрузи скилл `ship` из ядра и следуй ему.

## Контур

- Репо работы: `/home/prog7/home/dev/personal/consumer-registry`,
  main = `f7c479e` = тег `v0.2.0`, remote
  `git@github.com:ntin60775/consumer-registry.git` (SSH). Worktree
  `ontoship-registry-wt-dlv02`, ветка `dlv02-registry-dsh` от main —
  создай `git worktree add` В РЕПО РЕЕСТРА (хостовый create_worktree
  работает на репо сессии — ядро; прецедент sa05). База красной
  пробы: `v0.2.0` (`f7c479e`).
- В репо реестра стоит старое поколение OntoShip (9 бандлов) и
  устаревший конфиг ролей — НЕ обновляй и НЕ используй его маршруты
  (вне скоупа). Панель — по реестру ролей ЯДРА
  (`/home/prog7/home/dev/contrib/forks/ontoship-ntin/.agents/config.toml`).
- Параллельно другая сессия исполняет тикет 01 в ядре. Разделение:
  трогай только файлы репо реестра, `tickets/deliver/02-*` и
  `tickets/deliver/02-evidence/` (в трекере ядра). НЕ трогай: файлы
  ядра (кроме названных), continue.md, tickets/README.md,
  docs/plans/README.md, файлы тикета 01. Запись приёмки — в свой
  файл тикета; сводную запись делает сессия планирования.
- Коммиты реестра локальные; push и тег v0.3.0 — тикет 04, не здесь.

## Состав среза (критерии тикета — источник истины)

- Свой `scripts/install.sh`: link/copy/check одного бандла
  `consumer-registry`, идемпотентен, пишет только `.agents/skills`,
  preflight отказывает вместо полуустановки — контур установщика
  ядра (`scripts/install.sh` ядра — образец).
- Бандл самонесущий: `skills/consumer-registry/` несёт SKILL.md,
  `templates/` (схема, каркас, gitignore.snippet),
  `scripts/registry_check.py`; валидатор запускается из бандла.
- Пути `.agents`: дом `<продюсер>/.agents/registry.local.json`;
  сниппет `.agents/registry.local.json`; описательные тексты
  схемы/каркаса/докстринга — новый путь. Поля, структура, `const`
  версии, required-наборы схемы НЕ меняются (сверка с v0.2.0).
- ZCode-канал снят: `.zcode-plugin/`, `deploy.json` удалены;
  `grep -r zcode` по содержимому бандла пуст.
- SKILL.md DSH-идиомы (`name`/`description`); старт ведения
  идемпотентен (повторный — diff пуст, строка не дублируется);
  предупреждение «снос .agents уничтожает реестр, бэкап вне v1»;
  правило сверки followups done=false перед поставкой сохранено.
- Тесты адаптированы под новые пути (без nice-to-have); красная
  проба финальным набором на `v0.2.0` — failed по существу.

## Демо и гейты

- Установка в temp-продюсер (link и copy): старт ведения создаёт
  `.agents/registry.local.json` из каркаса + свою строку gitignore
  (чужие целы); повторный старт — diff пуст; валидатор зелёный на
  ЗАПОЛНЕННОМ реестре (ненулевые consumers/deploy_log с актом, не
  на голом каркасе).
- Панель: четыре ревьюера
  `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`, `max` (реестр
  ядра); сверь с живым `list_subagent_models`, спавн с явными
  provider/model/reasoning_effort. Один проход правок.
- Dev/prod: тесты реестра зелёные, чистая установка из среза в temp,
  grep zcode пуст. Гейты пака: ноль.
- Merge ff в registry main (локально), автоприёмка на полном зелёном
  контуре, запись фактов в файл тикета (в трекере ядра), worktree
  снести.

## Стоп-точки

Неразобранное расхождение ожидание/факт; панель красная после одного
прохода правок; маршрут недоступен; бюджет > 600k токенов — стоп,
handoff, вопрос оператору. Скоуп не расширять: зацепки — в свою
секцию `tickets/deliver/leads.md`.

## Отчёт

Фактами: коммиты среза/merge (реестр), красная проба (числа), панель
(вердикты, находки, закрытие), тесты/установка/grep, пробелы. Без воды.