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
2026-10-23; юнит закрыт: тикеты 01–02 сделаны,

| # | тикет | блокируется |
|---|---|---|
| 01 | [dry-run: link-режим](install-dry-run/01-dry-run-link.md) | — |
| 02 | [dry-run: copy-режим](install-dry-run/02-dry-run-copy.md) | 01 |

Пятый юнит [`review-config`](../docs/plans/review-config.md) закрыт 2026-10-29:
спека утверждена на план-гейте 2026-10-28 (решения 1–14), все пять тикетов
сделаны и приняты оператором; юнит доказал сам себя — живое доказательство
собрано в [тикете 05](review-config/05-live-proof.md).

| # | тикет | блокируется |
|---|---|---|
| 01 | [механизм: конфиг и генерация](review-config/01-mechanism.md) | — |
| 02 | [init: бутстрап-выбор моделей](review-config/02-init-config.md) | 01 |
| 03 | [скилл critic и восьмой бандл](review-config/03-critic-skill.md) | 01 |
| 04 | [панель в ship, справочник ролей](review-config/04-panel-ship-roles.md) | 01, 03 |
| 05 | [живое доказательство](review-config/05-live-proof.md) | 01, 02, 03, 04 |

Закрытый юнит [`evidence-verification`](../docs/plans/evidence-verification.md):
спека утверждена на план-гейте 2026-10-29 (решения 1–6 — ask-раунд оператора;
решение 7 — 2026-10-30, итог разбора пропущенных шагов); тикеты 01–03 приняты
2026-10-30 (02 — в переформулированной оператором редакции), тикет 04 —
в тот же день по выбору оператора. Исполнение — один тикет за прогон; критери
тикетов первыми показывают новую форму: артефакт и ожидание в каждом. Критик
юнита прогнан 2026-10-30 до первого ship (`dwfrun-4facb4e8`), находки —
оператору.

| # | тикет | блокируется |
|---|---|---|
| 01 | [правила приёмки](evidence-verification/01-acceptance-rules.md) | — |
| 02 | [роли ревью](evidence-verification/02-review-roles.md) | 01 |
| 03 | [ранняя фаза](evidence-verification/03-early-phase.md) | — |
| 04 | [фазовые переходы](evidence-verification/04-phase-checklists.md) | 01, 03 |

Открытый мини-юнит [`ship-isolation`](../docs/plans/ship-isolation.md): спека
утверждена на план-гейте 2026-10-30 (решения 1–3 — ask-раунд оператора);
нарезка — один тикет, по решению 2 спеки.

| # | тикет | блокируется |
|---|---|---|
| 01 | [безусловный worktree](ship-isolation/01-unconditional-worktree.md) | — |

Открытый юнит [`onto-doc`](../docs/plans/onto-doc.md): спека утверждена на
план-гейте 2026-10-30 (решения 1–11: директивы 1–5 и 11; ask-раунд — 7, 8, 10
и утверждение; гейт подтвердил 6 и 9); тикеты нарезаны тем же днём, один
вопрос на тикет. Критик нарезки `dwfrun-15f9e3c4` (3 P1 / 9 P2 / 4 P3)
закрыт решением оператора «править всё, включая разрез тикета 03»:
тикеты 01–02 и 05 доработаны, 03 разрезан на init (03) и вендор-README
с индексами (04). Квиз нарезки пропущен директивой оператора — зацепка
в [continue.md](../docs/ops/continue.md).

| # | тикет | блокируется |
|---|---|---|
| 01 | [конфиг и генератор](onto-doc/01-config-generator.md) | — |
| 02 | [скилл и прогон](onto-doc/02-skill-run.md) | 01 |
| 03 | [init: шестая роль](onto-doc/03-init-sixth-role.md) | 01 |
| 04 | [вендор-README и индексы](onto-doc/04-vendor-readme-indexes.md) | — |
| 05 | [живое доказательство](onto-doc/05-live-proof.md) | 02 |

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
