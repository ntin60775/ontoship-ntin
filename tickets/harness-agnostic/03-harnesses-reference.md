# 03: справочник харнессов

**Что построить:** durable-справочник `docs/reference/harnesses.md` с матрицей
zcode 3.16.2, DSH и Qoder 0.4.8: какой project-local корень скиллов читает каждый,
какие ранги и приоритеты действуют, где это доказано в исходниках и что делать, когда
настройка выключена. Справочник не описывает глобальную установку как канал проекта.

**Блокируется:** 01.

**Статус:** сделан (2026-10-21)

- [x] Матрица называет `<project>/.agents/skills` общим корнем и точный путь
      харнесс-специфичного корня для каждого: DSH `.dsh/skills` (ранг 100 против 200 у
      `.agents`), zcode 3.16.2 `.zcode/skills` и `.agents/skills`, Qoder 0.4.8
      `.agents/skills` при `skills.loadFromAgentsDirectory: true`.
- [x] Для каждого утверждения назван источник: файл и функция в исходниках
      (`skill-filesystem/src/index.ts`, `app.asar` →
      `resolveAncestorWorkspaceRoots`, `qoder-worker-runtime.obf.mjs` →
      `buildProjectSkillDirectorySet` / `resolveAgentSkillsDir`) или живая настройка.
- [x] Записан запасной вариант Qoder, когда `loadFromAgentsDirectory` выключен, и
      правило: отказ харнесса от `.agents/skills` — новый план, а не адаптер.
- [x] Все три харнесса читают `AGENTS.md` из корня проекта; это записано с
      источником.
- [x] `docs/reference/README.md` и `docs/README.md` ссылаются на справочник; lint
      чистый, документ не сирота.

**Что я могу показать, когда это готово?** Открыть `docs/reference/harnesses.md` и
увидеть три строки матрицы с путями, рангами и доказательствами; `lint --strict`
чистый; `search "agents/skills"` находит справочник.

## Доказательства (2026-10-21)

- **Поставлено:** `docs/reference/harnesses.md` (88 строк) — матрица трёх харнессов,
  ранги DSH, workspace-кандидаты zcode, условие Qoder, `AGENTS.md`, запасные варианты
  и границы проверки. Источники названы функциями и файлами, а не пересказом.
- **Индексы:** ссылка добавлена в `docs/reference/README.md` (и в его `links`) и в
  `docs/README.md`; документ не сирота.
- **Линт:** `lint --strict` → `✓ чисто (30 файлов · —)`, код 0.
- **Поиск:** `search "agents/skills"` → первым хитом `docs/reference/harnesses.md`;
  `search "loadFromAgentsDirectory"` → тот же документ и тикет 03.
- **Рамки:** новых инвариантов и полей онтологии нет; документ — обычный `reference`.

**Остаток:** тикет 04 — dogfood и миграция репозитория.
