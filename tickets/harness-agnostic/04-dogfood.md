# 04: dogfood на трёх харнессах

**Что построить:** этот репозиторий мигрирован на `.agents/skills`: три ссылки на
скиллы, `.dsh/skills` удалён, `AGENTS.md` несёт новый управляемый блок,
`install.sh --check "$PWD"` возвращает 0. Свежие сессии Qoder и DSH и workspace-каталог
zcode показывают три скилла. Если харнесс нельзя проверить, тикет фиксирует ручную
проверку или точный пробел — E2E не подделывается.

**Блокируется:** 01, 02, 03.

**Статус:** сделан (2026-10-21)

- [x] `scripts/install.sh "$PWD"` создаёт `.agents/skills/{kb-search,kb-curate,init}`;
      повторный запуск не меняет ничего; `--check "$PWD"` возвращает 0.
- [x] `.dsh/skills` удалён; `--check` предупреждает о legacy-записи, если она
      воссоздана, и никогда её не удаляет.
- [x] `.gitignore` содержит `.agents/skills/`; управляемый блок `AGENTS.md`
      перегенерирован через `init` и совпадает с шаблоном; второй прогон init не даёт
      diff.
- [x] `pytest` зелёный; `lint --strict` чистый; `search "canon"` и
      `search "target test"` возвращают ожидаемые документы; `stat --json` разбирается;
      `map -o docs-map.html` пишет HTML.
- [x] Qoder: свежая сессия видит `kb-search`, `kb-curate`, `init` из
      `.agents/skills`; DSH: сессия видит те же три; zcode: workspace-каталог содержит
      `.agents/skills` и три бандла. Для каждого — команда или точный пробел.
- [x] `docs/ops/continue.md` фиксирует новое состояние, стартовый промпт и пробелы;
      `docs/plans/core-kb.md` получает однострочную пометку о замене корня;
      `docs/plans/README.md`, `docs/README.md` и `tickets/README.md` обновлены.
- [x] План `harness-agnostic.md` помечен завершённым; все четыре тикета закрыты.

**Что я могу показать, когда это готово?** `ls -l .agents/skills` — три ссылки;
`ls .dsh` — каталога нет; `install.sh --check "$PWD"` — 0; `pytest`, `lint`, поиск,
`stat` и `map` — зелёные; вывод обнаружения скиллов в Qoder/DSH и состояние zcode.

## Доказательства (2026-10-21)

- **Миграция:** `scripts/install.sh "$PWD"` → `unchanged kb-search`, `unchanged
  kb-curate`, `unchanged init`; `--check "$PWD"` → `ok` по трём ссылкам,
  `check: ok`, код 0. `ls -l .agents/skills` — три абсолютные символические ссылки на
  `skills/{kb-search,kb-curate,init}`; `.dsh` отсутствует. Установка не изменилась:
  это тот же бандл, что был в `.dsh/skills`, просто в универсальном корне.
- **Legacy-предупреждение:** воссоздана ссылка `.dsh/skills/kb-search` →
  `skills/kb-search`; `--check` напечатал `warning: legacy .dsh/skills/kb-search points
  into this repository; DSH ranks .dsh/skills (100) above .agents/skills (200), so the
  old entry shadows the universal install — remove it manually`, при этом `check: ok`
  и код 0; ссылка осталась на диске. Демо-ссылка удалена после проверки, `.dsh` снова
  отсутствует.
- **init:** `.gitignore` содержит `.agents/skills/` четвёртой строкой после
  `.gitmark/`, `*-map.html`, `.scratch/`. Драйвер init из `.scratch/ticket-04/`
  сравнивает тело между маркерами с шаблоном из `skills/init/SKILL.md`: два прогона
  подряд — `AGENTS.md: unchanged`, `.gitignore: unchanged`; sha256 до и после
  совпадают: `AGENTS.md` — `add6b0a7…b00a68`, `.gitignore` — `9f1eebcf…84ef9`.
  Управляемый блок — 1046 байт UTF-8.
- **Тесты и линт:** `python3 -m pytest tests/ -q` → **168 passed**;
  `lint --strict` → `✓ чисто (30 файлов · —)`, код 0. Прогон поймал реальный дефект:
  многострочная frontmatter-ссылка `relates_to` в `continue.md` давала I4 `ERR`;
  ссылка сведена в одну строку, тест снова зелёный.
- **Поиск и производные:** `index` → 30 файлов, 148 чанков, 54 ссылки, trigram=on;
  `search "canon"` → первым `docs/decisions/ontoship-core.md`, `search "target test"` →
  `docs/reference/testing.md`; `stat --json` → `{"indexed": true, "files": 30, …,
  "trigram": true}`; `map -o docs-map.html` → 30 файлов, 54 ссылки, 0 вне индекса.
- **Qoder 0.4.8 — подтверждён:** две свежие сессии. Первая
  (`94d44799-0f58-406a-82a8-5d93c26cc3ea`) загрузила `kb-search` через инструмент
  `Skill` (`Launching skill: kb-search`) и выполнила
  `python3 .agents/skills/kb-search/gitmark.py search "canon" -k 1` →
  `docs/decisions/ontoship-core.md:1`. Вторая
  (`ccff3755-3894-48a6-b584-7e36dcc6473b`) перечислила все три project-local скилла
  (`kb-search`, `kb-curate`, `init` — 3/3), загрузила `kb-curate` из
  `.agents/skills/kb-curate` и процитировала его первую строку прозы; файлов не
  меняла.
- **DSH — точный пробел:** `dsh headless` завершается до сессии с
  `MISSING_CREDENTIAL: llm-deepseek: no API key for provider route "deepseek-official"`;
  `DEEPSEEK_API_KEY` не выставлен. Веб-сервер не запущен: PID в
  `/run/user/1000/dsh-web.pid` устарел, порт не слушается. Живой каталог DSH показать
  нельзя; обнаружение `.agents/skills` (ранг 200) доказано исходником
  `skill-filesystem/src/index.ts` в `docs/reference/harnesses.md`, а не E2E.
- **zcode 3.16.2 — точный пробел:** headless-режима нет: `zcode --help` поднимает GUI,
  печатает логи запуска и не выводит справку; живого workspace-каталога скиллов
  получить не удалось. Файловая раскладка `.agents/skills` на месте, оба
  workspace-корня (`.zcode/skills`, `.agents/skills`) доказаны
  `resolveAncestorWorkspaceRoots` в `app.asar` (там же).
- **Документы:** `docs/ops/continue.md` переписан под `.agents/skills`, 168 тестов,
  Qoder-проверку и пробелы DSH/zcode; `docs/plans/core-kb.md` получил пометку о
  замене только корня установки; `harness-agnostic.md` помечен завершённым;
  `docs/plans/README.md`, `docs/README.md`, `docs/reference/README.md` и
  `tickets/README.md` обновлены; тикеты 01–04 закрыты и сохраняют доказательства.
- **Рамки:** только project-local; в `$HOME`, `~/.agents`, `~/.dsh`, `~/.zcode` и
  `~/.qoder` ничего не писалось; старый OntoShip в zcode не удалялся — это работа
  оператора.

**Остаток:** следующего юнита нет. Открытая работа — в
[continue.md](../../docs/ops/continue.md#что-осталось-по-проекту).
