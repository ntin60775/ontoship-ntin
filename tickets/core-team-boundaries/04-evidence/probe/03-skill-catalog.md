# Каталог скиллов сессии — проба ctb04 (2026-11-17)

Источник: skill-каталог сессии (available_skills после установки ядра) +
`ls .agents/skills/` проекта. Установка: 10 symlink-бандлов из
`ontoship-ntin/skills/`, `install.sh --check` → `check: ok`.

## Проектные бандлы OntoShip — 10, chain нет

| скилл | фаза/роль |
|---|---|
| `grilling` | фаза 1: интервью → спека, план-гейт |
| `critic` | проекционная валидация спеки до нарезки |
| `to-tickets` | фаза 2: нарезка спеки на тикеты |
| `ship` | фаза 3: один проход worktree → merge, автоприёмка |
| `testing` | правило доказательных тестов (spec/invariant/target) |
| `init` | точка входа проекта (AGENTS.md, .gitignore, реестр, continue.md) |
| `kb-search` | поиск по KB (GitMark) |
| `kb-curate` | создание/правка документов KB |
| `onto-doc` | полная сборка KB онто-доком |
| `pack` | контракт паков стандартов команды/стека |

Скиллов цепочек (chain/оркестрация юнитов) в каталоге нет — ядро самодостаточно
на голом DSH-хосте без team/stack-бандлов.

## Прочие скиллы сессии (хост/профиль, не OntoShip) — 13

`bruno-api`, `dsh-doc`, `llm-wiki`, `logika`, `neuraldeep-api`,
`neuraldeep-speech`, `office`, `office-docx`, `office-pptx`, `office-xlsx`,
`official-plugins`, `personalized-pages`, `screenshotting-gui`.

## Профиль (plugin_manager)

Полный вывод — `03-plugin-manager.json`: `list_plugins` 228/228 записей,
`list_bundles` 29/29 бандлов. Совпадений `ontoship-*` — 0 в обоих списках.
Team-бандл пресетов уровня профиля отсутствует; паков `.agents/packs/` нет.