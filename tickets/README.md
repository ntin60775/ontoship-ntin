# Тикеты

Локальный трекер исполнения. Один файл на тикет, блокеры первыми. Тикеты — **не
документы KB**: без frontmatter, без инвариантов онтологии, без реестра планов. Они
отслеживаются только чтобы свежий клон мог продолжить работу; закрытый тикет помечен
сделанным и хранит доказательства в трекере (оператор может удалить тикеты закрытого
юнита; git хранит историю).

Durable-контракт лежит в [`docs/plans/`](../docs/plans/README.md). Первый юнит
`core-kb` закрыт: все шесть тикетов сделаны (2026-10-21). Второй юнит
[`harness-agnostic`](../docs/plans/harness-agnostic.md) тоже закрыт: утверждён
2026-10-21, все четыре тикета сделаны; они лежат в
[`harness-agnostic/`](harness-agnostic/01-install-root.md) как история. Третий юнит — [workflow-skills](../docs/plans/workflow-skills.md): спека утверждена
2026-10-21; тикеты нарезаны 2026-10-21 после оценки агента — один вопрос
ask-инструмента на тикет, с вариантами действий (канон, «Три фазы»). Юнит закрыт
2026-10-22: тикеты 01–06 сделаны, 06 (dogfood) дал сквозной прогон.

| # | тикет | блокируется |
|---|---|---|
| 01 | [grilling](workflow-skills/01-grilling.md) | — |
| 02 | [to-tickets](workflow-skills/02-to-tickets.md) | — |
| 03 | [ship](workflow-skills/03-ship.md) | — |
| 04 | [testing](workflow-skills/04-testing.md) | — |
| 05 | [install](workflow-skills/05-install.md) | 01, 02, 03, 04 |
| 06 | [dogfood](workflow-skills/06-dogfood.md) | 05 |

Dogfood-прогон 06 оставил свой игрушечный юнит — режим `--dry-run` установщика.
Спека [`install-dry-run`](../docs/plans/install-dry-run.md) утверждена оператором
2026-10-23; 01 сделан, 02 открыт:

| # | тикет | блокируется |
|---|---|---|
| 01 | [dry-run: link-режим](install-dry-run/01-dry-run-link.md) | — |
| 02 | [dry-run: copy-режим](install-dry-run/02-dry-run-copy.md) | 01 |

Закрытый юнит `harness-agnostic` остаётся историей:

| # | тикет | блокируется |
|---|---|---|
| 01 | [корень установки](harness-agnostic/01-install-root.md) | — |
| 02 | [переносимые скиллы и init](harness-agnostic/02-portable-skills.md) | 01 |
| 03 | [справочник харнессов](harness-agnostic/03-harnesses-reference.md) | 01 |
| 04 | [dogfood на трёх](harness-agnostic/04-dogfood.md) | 01, 02, 03 |

Закрытый юнит `core-kb` остаётся историей:

| # | тикет | блокируется |
|---|---|---|
| 01 | [движок](core-kb/01-engine.md) | — |
| 02 | [скилл kb-search](core-kb/02-kb-search-skill.md) | 01 |
| 03 | [kb-curate + онтология](core-kb/03-kb-curate-ontology.md) | 01 |
| 04 | [скилл init](core-kb/04-init-skill.md) | 01 |
| 05 | [установка](core-kb/05-install.md) | 02, 03, 04 |
| 06 | [dogfood](core-kb/06-dogfood.md) | 05 |
