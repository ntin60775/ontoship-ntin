---
node_type: reference
title: Совместимость харнессов — project-local скиллы и AGENTS.md
service: _platform
status: active
updated: 2026-11-10
tags: [harness, skills, review, agents-md, zcode, dsh, qoder]
links:
  part_of: [README.md]
  relates_to: [../plans/harness-agnostic.md, ../plans/review-config.md, ../plans/onto-doc.md, ../plans/entry-and-continuity.md, review-roles.md, ../ops/continue.md]
---

# Совместимость харнессов

Проверено по исходникам и живой конфигурации трёх харнессов. Вывод: корня
`<project>/.agents/skills` (установщик) достаточно для zcode, DSH и Qoder;
слой адаптеров не нужен.
Живые каталоги подтвердили все три сессии: DSH 0.2.2-rc.1 (2026-11-06)
видит восемь модельных скиллов проекта, `ship` вызывается командой
`/ship`. Справочник фиксирует доказательства, чтобы следующая сессия не
выводила их заново.

## Матрица

| харнесс | project-local корень скиллов | приоритет | `AGENTS.md` |
|---|---|---|---|
| DSH | `.agents/skills` (ранг 200); `.dsh/skills` (ранг 100) | `.dsh` выше `.agents` | читает из корня проекта |
| zcode 3.16.2 | `.agents/skills` и `.zcode/skills` в каждом workspace-корне | оба — кандидаты workspace | `NodeContextSourceAdapter` ищет файл от рабочего каталога вверх |
| Qoder 0.4.8 | `.agents/skills` при `skills.loadFromAgentsDirectory: true` | один корень | загружает `AGENTS.md` проекта и файлы предков |

Скилл — это каталог бандла `<root>/<name>/SKILL.md`; установщик кладёт туда
бандлы, состав называет индекс [skills/README.md](../../skills/README.md).
Все три харнесса читают `AGENTS.md` из корня проекта, поэтому точка входа
и управляемый блок живут там.

## Доказательства

### DSH

- Источник: `deepseek-harness/packages/skill/skill-filesystem/src/index.ts`.
- `<project>/.dsh/skills` имеет ранг 100, `<project>/.agents/skills` — ранг 200.
  Меньший ранг побеждает, поэтому старая запись `.dsh` затеняет универсальную.
- `AGENTS.md` загружается из корня проекта.
- Живой каталог DSH 0.2.2-rc.1 (2026-11-06): сессия перечисляет
  `kb-search`, `kb-curate`, `init`, `grilling`, `to-tickets`, `testing`,
  `critic`, `onto-doc` из `.agents/skills`; `ship` — user-invocable
  `/ship`. Прошлая запись о недоступности каталога снята 2026-11-09.

### zcode 3.16.2

- Источник: `app.asar`; функции `resolveAncestorWorkspaceRoots` →
  `getWorkspaceZcodeSkillRoot` / `getWorkspaceAgentsSkillRoot`, их потребляет
  сканирование workspace в `T3`.
- Сканирование идёт вверх по дереву от каждого workspace-корня;
  `.zcode/skills` и `.agents/skills` — оба кандидата.
- `AGENTS.md` разрешает `NodeContextSourceAdapter` от рабочего каталога вверх.
- Живая сессия zcode 3.16.2: все скиллы проекта видны из `.agents/skills`;
  инструмент `Skill` загрузил `kb-search`, `search "canon"` вернул
  `docs/decisions/ontoship-core.md`. Headless-режим не понадобился — проверка
  шла в живой интерактивной сессии.

### Qoder 0.4.8

- Источник: `qoder-worker-runtime.obf.mjs`; функции
  `buildProjectSkillDirectorySet` и `resolveAgentSkillsDir`.
- `<cwd>/.agents/skills` загружается, когда `skills.loadFromAgentsDirectory`
  равен `true`; в живом манифесте запуска стоит `true`.
- Пользовательский `~/.agents/skills` виден в сессии, но проект использует
  только project-local корень.
- `AGENTS.md` загружается вместе с файлами предков.

## Ревью-панель по харнессам

Спека — [review-config.md](../plans/review-config.md): панель запускает
ревью-роли на моделях из `.agents/config.toml`; контракт общий, способы
различаются по харнессам. Контракты ролей — [review-roles.md](review-roles.md).
Носитель методной секции в бандле:
[skills/ship/references/review-panel.md](../../skills/ship/references/review-panel.md)
(файл бандла — первоисточник; эта страница — полный носитель в KB).

### zcode — снят

ZCode-способ панели выведен из проекта: генератора определений и прогонов в
workflow нет, панель живёт только на DSH-рельсах. Возврат — решением оператора.

### DSH — рабочий способ

Роль идёт через `subagent` (spawn, не `subagent_fork`) с явными
`provider`, `model` и `reasoning_effort`: строка `model` —
`<provider>/<model>`, ключ `level` — `reasoning_effort`; адаптер делит
строку по первому `/`. Маршрут и уровень сверяются с живым
`list_subagent_models`; сгенерированные определения ролей не нужны. Все
роли панели стартуют в одном сообщении, отчёт собирается из уведомлений о
завершении и дедуплицируется. Недоступная модель роли — фолбэк на модель
сессии с пометкой в отчёте; провал и на фолбэке — одна повторная проба,
затем остановка прохода: «ревью провёл исполнитель» законным исходом не
является (решение 14).

### Qoder — пробел окружения, вне плана

Живая сессия Qoder 0.4.8 подтвердила каталог скиллов, но запуск ревью-ролей
на назначенных моделях не проверен — пробел окружения. Решение оператора —
Qoder не берём:
адаптер не строится, возврат — только словом оператора в живой сессии.
Qoder — единственный оставшийся пробел панели.

Бутстрап `init` работает на DSH — конфиг ролей пишется из
`list_subagent_models`, генератора определений в проекте нет (решение 2 спеки
[dsh-adaptation](../plans/dsh-adaptation.md); ZCode-ветка выведена из
эксплуатации).

## Прогон онто-дока по харнессам

Спека — [onto-doc.md](../plans/onto-doc.md): кураторы идут на модели из
`[agents.curator]` в `.agents/config.toml`; сверку модели и уровня с каталогом
моделей несёт скилл `skills/onto-doc/SKILL.md`. Контракт прогона общий,
способ запуска — DSH. Носитель методной секции в бандле:
[skills/onto-doc/references/ontodoc-run.md](../../skills/onto-doc/references/ontodoc-run.md)
(файл бандла — первоисточник; эта страница — полный носитель в KB).

### zcode — прогон онто-дока снят

Сохранённый workflow `.zcode/workflows/onto-doc.dwf.ts` из проекта выведен
вместе с ZCode-каналом; прогон живёт только на DSH-рельсах.

### DSH — прогон онто-дока

Прогон — fan-out `subagent` (spawn, не `subagent_fork`) с `provider`,
`model` и `reasoning_effort` из `[agents.curator]`; все кураторы — в одном
сообщении; каждый возвращает JSON-строку `path`/`curator`/`files`/
`refusal`, родитель сверяет объединение `files` с
`git diff --cached --name-only` после `git add -A`; прогон пишет только
внутри `root`. Проверки плана и полная процедура — в
[ontodoc-run.md](../../skills/onto-doc/references/ontodoc-run.md) бандла
`onto-doc`.
### Qoder — прогон онто-дока — пробел окружения

Способ запуска кураторов онто-дока в Qoder живой сессией не подтверждён —
как у ревью-панели выше; возврат — словом оператора.

## Вход в метод по харнессам

Спека — [entry-and-continuity.md](../plans/entry-and-continuity.md): вход в
метод после установки в чужой проект несёт секция «Вход в работу» в
управляемом блоке `AGENTS.md` — её пишет `init`; состояние между сессиями —
`docs/ops/continue.md`. Правило входа нейтрально к харнессу, формулировка
запрета план-режима — решение 5 спеки; полный текст правила живёт в блоке
`AGENTS.md`, здесь он не пересказывается. Блок читают все три харнесса
(матрица выше), поэтому носитель правила один. Механику прохода без
план-режима доказали прогоны полигона юнита (тикеты 01–03); живую пробу
маршрутизации естественных запросов несёт финальный тикет юнита, исход
фиксирует тикет.

## Что это значит для проекта

- Канонический корень единственного канала: `<project>/.agents/skills` —
  установщик `scripts/install.sh`. Канал плагина маркета выведен из проекта
  вместе с ZCode-рельсами. Копий внутри канала нет.
- Установленный движок лежит рядом со своим `SKILL.md` — скиллы называют
  навыковый корень канала: `.agents/skills/kb-search/gitmark.py`. Скилл
  не хардкодит расположение проекта.
- Старые записи `.dsh/skills` и `.qoder/skills`, ручные записи
  `.zcode/skills`, ведущие в этот репозиторий, и прежние раскладки
  `.zcode/skills` — legacy чужих проектов.
  `scripts/install.sh --check` предупреждает о legacy и никогда их не
  удаляет; удаление — решение оператора.
- Строки `.gitignore` — `.gitmark/`, `*-map.html`, `.scratch/` и навыковый
  корень `.agents/skills/` — пишет скилл `init`: установка и производные
  локальны и не коммитятся.

## Запасные варианты и границы

- **Qoder с выключенным `loadFromAgentsDirectory`.** `.agents/skills` не
  попадает в каталог. Включи настройку; копировать скиллы в
  харнесс-специфичный корень в этом юните нельзя.
- **zcode.** Рельс выведен из проекта: бандлы в `.zcode/skills` не ставятся,
  генератор и сохранённые прогоны не поставляются. Совместимость корня
  `.agents/skills` с zcode (матрица и доказательства выше) остаётся фактом
  для сторонних потребителей; возврат рельса — решением оператора.
- **DSH.** `.dsh/skills` остаётся только legacy-корнем в `EXCLUDE_DIRS` движка:
  старая установка не должна попадать в корпус KB.
- **Проверка.** Файловая раскладка доказывает только наличие бандлов. Каталог
  скиллов в свежей сессии — единственное доказательство загрузки; если сессию
  поднять нельзя, пробел фиксируется явно, а не подменяется выводом `ls`.
  Сессии zcode, Qoder и DSH подняты; живой каталог DSH записан в
  [continue.md](../ops/continue.md).

## Связанные документы

- План: [harness-agnostic.md](../plans/harness-agnostic.md) — решение и тикеты.
- Роли: [review-roles.md](review-roles.md) — контракты панели и регламент паков.
- Установка: [scripts/install.sh](../../scripts/install.sh) — канал и `--check`.
- Состояние: [continue.md](../ops/continue.md) — что проверено в этом
  репозитории.
