<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `.agents/skills/kb-search/gitmark.py`; корень — `.agents/skills`.
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

## Вход в работу (OntoShip)

- Изменения этого проекта идут через ship-флоу: скилл `ship` исполняет
  один тикет за запуск — вручную командой `/ship`; свободные правки
  в обход тикета не делаются — прямые решения оператора выше этого
  правила.
- Запрос плана открывает draft-спеку через скилл `grilling`; режим плана
  харнесса не используется.
- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):
  сессия продолжается оттуда и берёт следующий тикет оттуда же.
- Команды: «стартуй юнит» — открыть draft-спеку; `ship` — командой
  `/ship` или «исполняй тикет N»; «деплой и обновление [имя_проекта]» —
  скилл `deliver`.
<!-- END ontoship -->
