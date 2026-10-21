# OntoShip (DSH) — точка входа

OntoShip — метод и project-local пакет: **база знаний на markdown + git** с
детерминированным поиском, интервью, которое разрешает план до появления кода,
tracer-bullet тикетами и гейтированным ship-потоком — всё на нативных примитивах
хоста.

> Канон — [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md).
> Он арбитр: правило, которое ему противоречит, принадлежит строгому профилю или
> истории, а не умолчанию.

## Начни здесь

- **Продолжить** → [docs/ops/continue.md](docs/ops/continue.md) — состояние, открытая
  работа, порядок тикетов, факты окружения, стартовый промпт.
- **Канон** → [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md)
- **Источники** → [docs/reference/sources.md](docs/reference/sources.md)
- **KB** → [docs/README.md](docs/README.md)

## Раскладка

```
docs/          KB: канон, тестирование, источники, планы, ops
tickets/       локальный трекер исполнения (не KB; закрытые тикеты хранят доказательства)
vendor/        база движка ontoship-zcode (MIT); тикет 01 урезает её
skills/        ядровые скиллы: kb-search, kb-curate, init
scripts/       project-local канал установки (link/copy/check)
tests/         тесты движка, контрактов скиллов и установки
```

## Принцип

Markdown + git — источник истины. Всё производное — поисковый индекс, HTML-граф —
перегенерируется и никогда не коммитится как истина. `README.md` каждой папки — её
индекс; не давай документу стать сиротой. Ищи в KB до ответа или записи нового
документа.

## Форма

- **KB** durable; **spec** durable; **тикеты** эфемерны.
- **Факты** — работа агента; **решения** — работа оператора.
- Тест доказывает **пункт спеки** или охраняет **инвариант проекта** — ничего больше.
- Правила живут в механизмах (гейты хоста, промпты, тесты, движок) или не живут
  вообще.

## Язык документации

Вся документация проекта — планы, спеки, тикеты, справочники, runbook'и и проза
скиллов — на русском. Английский остаётся только для машинно-значимых литералов:
команд, путей, идентификаторов, ключей frontmatter, значений `node_type`, маркеров и
проверяемых строк. Вывод команд и сообщения об ошибках передаются как есть. Код и
комментарии в коде — по конвенции проекта; если её нет, комментарии на английском.

## Сопровождение

База движка — `vendor/ontoship-zcode/gitmark.py`; тикет 01 создаёт
`skills/kb-search/gitmark.py`. Когда он существует:

```bash
python3 skills/kb-search/gitmark.py index    # пересобрать индекс после правки документов
python3 skills/kb-search/gitmark.py lint     # проверки онтологии
python3 skills/kb-search/gitmark.py map -o docs-map.html
```

<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `.agents/skills/kb-search/gitmark.py` для прямого запуска.
- Новые или обновлённые документы: загрузи скилл `kb-curate` — сначала поиск, никогда
  не дублируй.
- Сопровождение после правки документов:

  ```sh
  python3 .agents/skills/kb-search/gitmark.py index
  python3 .agents/skills/kb-search/gitmark.py lint --strict
  python3 .agents/skills/kb-search/gitmark.py map -o docs-map.html
  ```

- KB — это markdown + git: `.gitmark/`, `*-map.html` и `.scratch/` производные или
  эфемерные — никогда не коммитятся.
<!-- END ontoship -->
