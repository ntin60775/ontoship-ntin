# Стартовый промпт — тикет 01 юнита deliver (ядро)

Исполняй тикет 01 «Бандл deliver и строка входа» юнита `deliver`
через скилл `ship` — один тикет за запуск, полный контур от worktree
до merge и автоприёмки.

## Прочитай до работы (порядок)

1. `docs/ops/continue.md` — абзац «Открыт юнит deliver» и «Факты
   окружения».
2. `docs/plans/deliver.md` — спека (ревизия по триажу): разделы
   «Протокол deliver», «Контракт акта», «Готово» 1–2, решения 1, 7,
   тривиальные решения.
3. `tickets/deliver/01-deliver-bundle.md` — твой тикет: критерии,
   демо-путь, ограничения.
4. `tickets/deliver/00-projection-report.md` — нормы триажа G-15
   (каталог обновляется в сессии), G-18 (построчное владение
   gitignore), G-24 (description без литерала «раскатай ядро в X»),
   G-26 (selfhost-порядок).
5. `tickets/deliver/handoff-parallel-01-02.md` — разделение файлов,
   маршруты, бюджет, точки остановки.
6. Загрузи скилл `ship` и следуй ему.

## Контур

- Репо: `/home/prog7/home/dev/contrib/forks/ontoship-ntin`,
  main = `cf479db`. Worktree `ontoship-ntin-wt-dlv01`, ветка
  `dlv01-deliver-bundle` от main. База красной пробы: `40c0dc6`.
- Параллельно другая сессия исполняет тикет 02 в репо
  consumer-registry. Разделение: трогай только файлы ядра по тикету
  01, `tickets/deliver/01-*` и `tickets/deliver/01-evidence/`.
  НЕ трогай: continue.md, tickets/README.md, docs/plans/README.md,
  файлы тикета 02, репо consumer-registry. Запись приёмки — в свой
  файл тикета; сводную запись делает сессия планирования.

## Состав среза (критерии тикета — источник истины)

- `skills/deliver/SKILL.md`: description семантики поставки/обновления
  (без литерала «раскатай ядро в X»); полный протокол и контракт акта
  из спеки; текст коннектора (скилл реестра есть — загрузи и следуй
  правилам, файла нет — старт ведения затем акт; скилла нет — пробел
  называется, fallback нет). Проектных фактов в бандле нет.
- Состав 11: массив `SKILLS` и usage `scripts/install.sh`, кортеж
  `SKILLS` `tests/test_install.py`, индекс `skills/README.md` —
  одним срезом, паритет зелёный.
- Шаблон блока `skills/init/SKILL.md`: строка команды «деплой и
  обновление» со ссылкой на deliver; пины `tests/test_skill_init.py`
  (литерал блока, ENTRY_RULES) тем же срезом; selfhost-блок репо —
  повторным init (diff пуст после).
- Selfhost-порядок: носители → `scripts/install.sh .` (link) →
  `--check` ok; членство deliver в каталоге текущей сессии.
- Красная проба финальным набором на `40c0dc6` — failed по существу.

## Панель и гейты

- Четыре ревьюера по `.agents/config.toml` ядра:
  `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`, `max`; сверь
  с живым `list_subagent_models`, спавн с явными
  provider/model/reasoning_effort. Один проход правок по находкам.
- Dev/prod: полный набор pytest (после сноса worktree либо
  `pytest tests/` — вложенные worktree краснят import mismatch),
  `lint --strict`, selfhost `check: ok`, чистая copy-установка в
  temp (11 бандлов). Гейты пака: паков нет — ноль.
- Merge ff в main, автоприёмка на полном зелёном контуре, запись
  фактов в файл тикета, worktree снести. Push main по SSH.

## Стоп-точки

Неразобранное расхождение ожидание/факт; панель красная после одного
прохода правок; маршрут недоступен; бюджет > 600k токенов — стоп,
handoff, вопрос оператору. Скоуп не расширять: зацепки сверх
критериев — в свою секцию `tickets/deliver/leads.md`.

## Отчёт

Фактами: коммиты среза/merge, красная проба (числа), панель
(вердикты, находки, закрытие), набор/lint/check, пробелы. Без воды.