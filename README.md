# OntoShip для DSH

> **База знаний проекта — это просто `markdown` + индекс `README` + `git`.**
> Ничего проще не работает лучше.

OntoShip — метод **передачи инженерной практики**: детерминированная база знаний на
markdown, интервью, которое проверяет план на прочность до появления кода,
tracer-bullet тикеты и гейтированный ship-поток по одному тикету за раз.

Этот репозиторий — **чистое переоснование**, а не форк текстов zcode. Он возвращается
к трём источникам и держит только то, что они действительно говорят:

1. **OntoShip** (vakovalskii) — KB и 11-шаговый dev-flow. Продукт — workflow; KB —
   субстрат; онтология необязательна; простота — операционное свойство.
2. **Matt Pocock** — `grilling` (дерево дизайна, фронтир, раунды) и `to-tickets`
   (tracer-bullet, блокирующие рёбра, квиз). Решения и публикация тикетов остаются за
   оператором.
3. **Стратегия тестирования оператора** — тест доказывает пункт спеки, охраняет
   инвариант проекта или воспроизводит реальный сбой (target-тест); сценарии
   агентные (MCP), а не написанные вручную безопасные пути; устаревшие тесты
   удаляются.

Канон — одна страница: [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md).
Источники и что из каждого взято: [docs/reference/sources.md](docs/reference/sources.md).

**Начни здесь:** [docs/ops/continue.md](docs/ops/continue.md) — состояние, порядок
тикетов, открытая работа и стартовый промпт. Юниты
[core-kb](docs/plans/core-kb.md), [harness-agnostic](docs/plans/harness-agnostic.md)
и [workflow-skills](docs/plans/workflow-skills.md) завершены; записи тикетов лежат в
[tickets/](tickets/README.md). Dogfood-прогон 06 оставил игрушечный юнит
[`install-dry-run`](docs/plans/install-dry-run.md): спека утверждена оператором,
тикеты 01–02 влиты — юнит закрыт 2026-10-23.

## Состояние

**Pre-alpha, самодостаточный.** Ядро KB (`core-kb`) завершено и проверено на dogfood:
движок GitMark, `kb-search`, `kb-curate`, `init` и `scripts/install.sh`, 229 тестов и
чистый `lint --strict`. Workflow-скиллы `grilling`, `to-tickets`, `ship` и `testing`
готовы; установка ставит семь скиллов. Сквозной dogfood-прогон прошёл 2026-10-22:
интервью → тикеты → `ship` до локального merge. Открытая работа записана в
[docs/ops/continue.md](docs/ops/continue.md#что-осталось-по-проекту). Предыдущая линия
([ontoship-zcode](https://github.com/ntin60775/ontoship-zcode)) хранится как **строгий
профиль** и история — не умолчание.

## Лицензия

MIT — см. [LICENSE](LICENSE).
