---
node_type: index
title: Планы
service: _platform
status: active
updated: 2026-11-02
links:
  part_of: [../README.md]
  relates_to: [core-kb.md, harness-agnostic.md, workflow-skills.md, install-dry-run.md, review-config.md, evidence-verification.md, ship-isolation.md, onto-doc.md, understanding-check.md, review-loose-ends.md, role-registry.md, entry-and-continuity.md, ../decisions/ontoship-core.md, ../ops/continue.md]
---

# Планы

Контракты планов (`node_type: plan`) — durable-спеки одного юнита. Тикеты
эфемерны и здесь не живут; `to-tickets` публикует их в
`.scratch/<slug>/issues/` или трекер после план-гейта.

- [core-kb.md](core-kb.md) — первый юнит: устанавливаемое ядро KB (утверждён;
  завершён, тикеты 01–06).
- [harness-agnostic.md](harness-agnostic.md) — project-local корни каналов:
  `.agents/skills` и `.zcode/skills`, для zcode, DSH и Qoder (утверждён
  2026-10-21; завершён, тикеты 01–04; каналы — по приписке 2026-11-02).
- [workflow-skills.md](workflow-skills.md) — фазы метода как скиллы: `grilling`,
  `to-tickets`, `ship`, `testing` (утверждена 2026-10-21; завершена 2026-10-22,
  тикеты 01–06).
- [install-dry-run.md](install-dry-run.md) — режим `--dry-run` установщика:
  план без записи (утверждён и завершён 2026-10-23, тикеты 01–02).
- [review-config.md](review-config.md) — проектный конфиг субагентов, панель
  ревью-специалистов и критик плана (утверждён 2026-10-28, решения 1–14;
  завершён 2026-10-29, тикеты 01–05).
- [evidence-verification.md](evidence-verification.md) — артефакт доказательства
  вместо красно-зелёного семафора: носители в «Готово», разбор расхождений,
  ранняя оценка цены доказательства (утверждён 2026-10-29, решения 1–6;
  завершён 2026-10-30, тикеты 01–04).
- [ship-isolation.md](ship-isolation.md) — безусловный изолированный worktree
  для шипа: шаг 1 скилла ship и контракт без «или ветку» (утверждён
  2026-10-30, решения 1–3; завершён 2026-10-30: тикет 01 влит
  и принят, merge `355285a`, панель `dwfrun-752d8bbe`).
- [onto-doc.md](onto-doc.md) — тяжёлая док-часть из оригинала: fan-out
  кураторов на модели из конфига, `[agents.curator]` и уровни ролей
  (утверждён 2026-10-30, решения 1–11; завершён 2026-11-01, тикеты 01–05).
- [review-loose-ends.md](review-loose-ends.md) — мини-юнит: сторож
  паритета перечня бандлов и нейтральные формулировки реестра ролей
  (утверждён 2026-11-01, решения 1–3; критик dwfrun-6c6159cc — «план
  пригоден после правок», закрыт «править всё»; завершён 2026-11-01:
  тикет 01 влит и принят, срез `2550560`, панель dwfrun-a26587f5,
  366 passed).
- [understanding-check.md](understanding-check.md) — сверка понимания вместо
  квиза в нарезке: шаг 3 `to-tickets` и его контракт (утверждён 2026-10-30,
  решения 1–6; завершён 2026-10-30: тикет 01 влит и принят, merge
  `85188bf`, панель `dwfrun-c609052e`).
- [role-registry.md](role-registry.md) — мини-юнит: машинный источник
  перечня ролей ядра — `roles.py` бандла init, кортежи ядра и панели,
  якорный паритетный тест (утверждён 2026-11-01, решения 1–4; завершён
  2026-11-02: тикет 01 влит и принят, срез `03b2e12`, панель
  `dwfrun-c90a3f20`, 383 passed).
- [entry-and-continuity.md](entry-and-continuity.md) — вход в метод после
  установки в чужой проект: секция «Вход в работу» в управляемом блоке init,
  скелет `continue.md`, живой полигон, условный SessionStart-хук, приписка
  харнессов и релиз v0.3.0 (утверждена 2026-11-02, решения 1–6; тикеты 01–03
  влиты и приняты, тикет 04 не активировался — условие не наступило,
  тикет 05 в работе — релиз за merge).

Одиннадцать юнитов закрыты: шесть основных (`core-kb`, `harness-agnostic`,
`workflow-skills`, `review-config`, `evidence-verification`, `onto-doc`),
игрушечный `install-dry-run` (2026-10-23) и мини-юниты `ship-isolation`,
`understanding-check`, `review-loose-ends`, `role-registry` (тикет 01
влит и принят у каждого; панели — `dwfrun-752d8bbe`, `dwfrun-c609052e`,
`dwfrun-a26587f5`, `dwfrun-c90a3f20`). Юнит `onto-doc` закрыт 2026-11-01:
нарезка — тикеты 01–05, все влиты и приняты (живое доказательство — прогон
`dwfrun-5efcd1d0`). Открыт юнит `entry-and-continuity`: тикеты 01–03
влиты и приняты, тикет 04 не активировался, тикет 05 в работе. Открытая
работа и пробелы харнессов записаны в [continue.md](../ops/continue.md).
