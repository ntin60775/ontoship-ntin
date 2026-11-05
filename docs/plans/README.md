---
node_type: index
title: Планы
service: _platform
status: active
updated: 2026-11-05
links:
  part_of: [../README.md]
  relates_to: [core-kb.md, harness-agnostic.md, workflow-skills.md, install-dry-run.md, review-config.md, evidence-verification.md, ship-isolation.md, onto-doc.md, understanding-check.md, review-loose-ends.md, role-registry.md, entry-and-continuity.md, bundle-references.md, canon-section-in-bundles.md, plan-gate-ask.md, to-tickets-agent.md, ../decisions/ontoship-core.md, ../ops/continue.md]
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
  харнессов и релиз v0.3.0 (утверждена 2026-11-02, решения 1–6; завершён
  2026-11-02: тикеты 01–03 влиты и приняты, тикет 04 не активировался —
  условие не наступило, тикет 05 влит и принят — релиз v0.3.0, тег
  на origin, пин каталога, selfhost-миграция).
- [bundle-references.md](bundle-references.md) — справочники метода в бандлах:
  `references/` в ship, onto-doc, testing, guard-фраза перекрытия проектом,
  паритет носителей, каналы установки, фраза-граница в канон (утверждён
  2026-11-03, четыре решения одним проходом; критик dwfrun-f9578d66 —
  правки внесены; тикеты 01–04 все влиты и приняты: 01 — 2026-11-03,
  merge `9e48183`, панель `dwfrun-f83cd168`, 404 passed; 02 —
  2026-11-03, панель `dwfrun-0ec0823b`, набор 433 passed;
  03 — 2026-11-03, релиз v0.4.0 (merge `3760fb0`, панель
  `dwfrun-8702999c`, тег на origin, пин каталога `130a4a0`, чистая
  установка по пину); 04 — 2026-11-04, приёмка потребителя (merge
  `58a48f0`: update erp-demo v0.3.0 → v0.4.0, проба путей чистая,
  rollout в реестре, живой прогон — панель их сессии
  `dwfrun-8cdf4fa8` на срезе их тикета 05, карточка сверена с
  фактом) — юнит закрыт.
- [canon-section-in-bundles.md](canon-section-in-bundles.md) — секция канона
  «Три фазы» в бандлах: `method-phases.md` в ship, перепись шести
  носителей-упоминаний канона в пяти скиллах, guard-фраза, якорный
  паритет, релиз v0.5.0, приёмка update erp-demo (утверждена на
  план-гейте 2026-11-04; критик dwfrun-2bc9db7a закрыт «править всё»;
  тикет 01 влит и принят 2026-11-04, merge `351a1a5`, панель
  `dwfrun-023d5b6f`, 446 passed; тикет 02 — релиз v0.5.0: merge
  `09a4b94`, панель `dwfrun-7b09b760`, тег на origin, пин каталога
  `7d07080`, чистая установка по пину, update erp-demo (проба путей
  чистая) — влит и принят 2026-11-04 — юнит закрыт).
- [plan-gate-ask.md](plan-gate-ask.md) — план-гейт ask-проходом и ограда
  молчания: форма гейта и запрет автономии без ответа в скилле grilling
  (утверждён на план-гейте 2026-11-05 ask-проходом — первая живая проба
  формы юнита; критик dwfrun-82b9d971 — `ready_after_fixes`, 6 находок
  закрыты «править всё»; тикет 01 принят, в работе).
- [to-tickets-agent.md](to-tickets-agent.md) — to-tickets вызывает агент:
  фраза канона и зеркала, снятие флага disable-model-invocation со
  скилла, переворот контрактного теста (утверждён на план-гейте
  2026-11-05 ask-проходом; решения оператора: формулировка «вызывает
  агент», флаг убрать; нарезка — один тикет принят ask-ом в том же
  прогоне; в работе).

Четырнадцать юнитов закрыты: шесть основных (`core-kb`, `harness-agnostic`,
`workflow-skills`, `review-config`, `evidence-verification`, `onto-doc`),
игрушечный `install-dry-run` (2026-10-23), мини-юниты `ship-isolation`,
`understanding-check`, `review-loose-ends`, `role-registry` (тикет 01
влит и принят у каждого; панели — `dwfrun-752d8bbe`, `dwfrun-c609052e`,
`dwfrun-a26587f5`, `dwfrun-c90a3f20`) и юниты `entry-and-continuity`
(2026-11-02, релиз v0.3.0), `bundle-references` (2026-11-04, релиз
v0.4.0) и `canon-section-in-bundles` (2026-11-04, релиз v0.5.0).
Юнит `onto-doc` закрыт 2026-11-01: нарезка — тикеты 01–05, все
влиты и приняты (живое доказательство — прогон `dwfrun-5efcd1d0`).
Открытая работа и пробелы харнессов записаны
в [continue.md](../ops/continue.md).
