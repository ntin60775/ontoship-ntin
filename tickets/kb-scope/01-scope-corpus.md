# 01: scope-ридер в `iter_md` и отказ на битом конфиге

**Спека:** [docs/plans/kb-scope.md](../../docs/plans/kb-scope.md)

**Что построить:** `gitmark.scope.json` в корне проекта с единственным ключом
`exclude_prefixes`; фильтр врезается в `iter_md`
(`skills/kb-search/gitmark.py`) до развилки `git_md_files` /
`iter_md_fallback`, поэтому `index`, `search`, `stat`, `map` и `lint` берут
один корпус; строгий отказ (stderr, exit 2, пустой stdout) на битый JSON,
`exclude_prefixes` не список, элемент не строка, незнакомый ключ и префикс без
завершающего `/`, не по существующему файлу (решение 16) — тем же
контуром, что `LintPathError`; строка `scope: <N> файлов исключено по <K>
префиксам` при ненулевом excludes.

**Блокируется:** нет.
**Предусловие:** решения 1–4, 8, 9 спеки (ask 2026-11-10); поля версии схемы
нет (решение 3); `EXCLUDE_DIRS` не растёт чужой политикой.

**Демо-путь:** временной git-репозиторий с `docs/a.md`, `snapshots/b.md` и
`gitmark.scope.json` = `{"exclude_prefixes": ["snapshots/"]}`: `lint` больше не
считает `snapshots/b.md` в `checked`, `stat --json` не даёт его в `files`,
`search` его не находит, `map` его не рисует; stdout `lint` несёт строку
`scope: 1 файлов исключено по 1 префиксам`; без файла корпус прежний;
битый JSON даёт stderr, exit 2 и пустой stdout. Новые тесты краснеют на
базовом коммите и зеленеют на срезе.

**Критерии приёмки**:

- [x] корпус режется — артефакт: `tests/test_scope.py`, `tests/conftest.py`
      (фикстура временного git-репозитория появляется этим тикетом: сегодня
      `git init` повторяется инлайн в `tests/test_engine.py`) и вывод `lint`,
      `stat --json`, `search` на фикстуре; ожидание: markdown под префиксом из
      `exclude_prefixes` отсутствует в `checked`, в `files`, в hits `search` и
      в корпусе `map`; файла `gitmark.scope.json` нет — те же файлы в корпусе
      (спека «Готово» 1)
- [x] один корпус у всех команд — артефакт: `tests/test_scope.py`;
      ожидание: `iter_md` — единственное место фильтра, и `index` → `stat` →
      `search` → `lint` → `map` называют одно число файлов
      (спека «Готово» 1, решение 4)
- [x] git-независимость — артефакт: `tests/test_scope.py` с
      monkeypatched `subprocess.run` (git недоступен); ожидание:
      `iter_md_fallback` исключает ровно те же файлы, что git-путь
      (спека «Готово» 2)
- [x] отказ вместо молчания — артефакт: `tests/test_scope.py` — spec-тест на
      каждую отказывающую причину (битый JSON, не список, не строка,
      незнакомый ключ, пустой, абсолютный, выходящий за корень, префикс без
      завершающего `/` не по файлу, «ожидался объект», «не читается», висящий
      симлинк, предельная вложенность) и инвариант
      `test_refusal_keeps_stdout_empty_and_exits_two` в форме существующего
      `test_cli_refusal_exit2_stderr_stdout_empty`; ожидание: exit 2, stdout
      пуст, ни одна проверка не выполнена, причина названа
      (спека «Готово» 3, решения 8 и 16)
- [x] строка об исключениях — артефакт: stdout `lint`; ожидание: литерал
      `scope: <N> файлов исключено по <K> префиксам` при ненулевом excludes и
      отсутствие строки при пустом или отсутствующем scope
      (спека «Готово» 4, решение 9)
- [x] формат префикса — артефакт: `tests/test_scope.py`; ожидание:
      `snapshots` без завершающего `/` и префикс, не ведущий к существующему
      файлу, дают отказ; `snapshots/` матчит только поддерево, `snapshots-notes/`
      остаётся в корпусе (спека «Готово» 3, решение 16)
- [x] существующий набор цел — артефакт: вывод pytest полного набора;
      ожидание: `tests/test_lint_paths.py` и `tests/test_engine.py` проходят
      без правки, включая инвариант «обратная совместимость без scope-файла»
      (спека «Ограничения», решение 6)

## Доказательства

**Срез.** worktree `.scratch/worktrees/kb-scope-01`, ветка `kb-scope-01` от
базового коммита `db889ac`. Коммиты: `575928d` — тесты первыми и реализация,
`6b96837` — правки по ревью-панели, `c1de496` — сокращение прозы кода под
планку. `create_worktree` в этой DSH-сессии упал («command "node" was not
found on PATH»), срез отделён запасным путём — `git worktree add -b
kb-scope-01 .scratch/worktrees/kb-scope-01 db889ac` (скилл ship: «`create_worktree`,
когда инструмент есть, иначе `git worktree`); `.scratch/` — в gitignore,
сносится `git worktree remove`.

**Красная проба на базовом коммите: 17 failed / 6 passed** (команда: `git
archive db889ac` в /tmp, поверх — новые `tests/` и `pytest.ini`, затем
`python3 -m pytest tests/test_scope.py -q`; повторено независимо ролями
`reviewer-tests` и `reviewer-kb`). Шесть зелёных на базе — контролируемые
охранники, они не могли падать по построению: `test_scope_absent_keeps_todays_corpus`,
`test_one_corpus_number_for_all_commands`, `test_slashed_prefix_may_name_an_absent_folder`,
`test_valid_scope_does_not_refuse`, `test_no_scope_line_without_a_scope_file`,
`test_empty_scope_list_still_prints_no_counts` (спека «Готово» 1 вторая
половина и «Готово» 4 молчаливый случай).

**Мутационные пробы (роль `reviewer-tests`).** Снятие фильтра (`kept = files`
в `iter_corpus`) → 7 failed, включая `test_filter_removal_puts_files_back`.
Снятие pre-flight `read_scope` в `main` (отказ только в `lint`) → поймано
`test_refusal_keeps_stdout_empty_and_exits_two` на `index`/`map`/`search`/`stat`.

**Демо-путь живьём** (временный git-репозиторий: `docs/README.md`,
`docs/keep.md`, `snapshots/excl.md`, `snapshots-notes/keep2.md`,
`apps/web/tests/expected/shot.md`):

```console
$ gitmark lint | tail -1                       # без scope-файла
✓ чисто  (5 файлов · —)
$ printf '{"exclude_prefixes":["snapshots/","apps/web/tests/expected/"]}' > gitmark.scope.json
$ gitmark lint
scope: 2 файлов исключено по 2 префиксам
✓ чисто  (3 файлов · —)
$ gitmark index | tail -1 ; gitmark stat --json
✓ index: 3 файлов · 3 чанков · 0 ссылок · trigram=on → .gitmark/index.db
{"indexed": true, "files": 3, ...}
$ gitmark search "QUARTZ ONYX"
ничего не найдено
$ printf '{oops' > gitmark.scope.json
$ gitmark lint --strict > out 2> err ; echo $?; wc -c < out
2
0
gitmark: gitmark.scope.json: не JSON — Expecting property name enclosed in
double quotes: line 1 column 2 (char 1)
$ gitmark index  # тот же отказ, корпус не тронут
rc=2, .gitmark/index.db не создан, m.html не создан
```

**Ревью-панель (один прогон, 2026-11-10).** Роли из `.agents/config.toml`,
маршрут `qwen-token-plan/qwen3.8-flash`, уровень `xhigh` (сверен
`list_subagent_models`), запуск `subagent`-spawn в одном сообщении:
`reviewer-spec` — `ready`, 4 P3; `reviewer-tests` — принять, 1 P2, 6 P3;
`reviewer-code` — принято с наследством тикету 03, 2 P2, 11 P3;
`reviewer-kb` — принять с правками, 1 P1, 3 P2, 7 P3. Закрыто в срезе
(`6b96837`, `c1de496`): P1 планки (движок 1397 вместо 1419 — сокращена
проза docstring'ов, не норма), P2 якоря `len(KEEP)`, P2 причины отказа
(непокрытые «ожидался объект», «не читается», висящий симлинк, рекурсивный
JSON), P2 строка `scope:` и её порядок (итог остаётся последней строкой,
рецепт `lint | tail -1` жив), P3 durable-якорь `#готово-2`, P3 «отказ не
пишет файлы», P3 формулировки docstring'ов. Вынесено решениями оператора:
I10 и рёбра графа → тикет 04; окно «scope изменён, индекс не пересобран» →
нормативная обязанность `index` (носитель — AGENTS.md «Сопровождение» и
SKILL.md, тикет 03).

**Проверки dev и prod.** Набор — **469 passed** (440 на базе + 29 новых
проверок). Prod-проверка обратимости на этом репозитории (scope-файла ещё
нет — догфуд у тикета 03): `index` → 106 файлов, `lint --strict` → `✓ чисто`
(106 файлов, exit 0), `map` → 0 вне индекса; `cmd_lint` — 32 строки против
планки ≤ 80; новых импортов нет (stdlib).

**Разбор расхождений ожидание/факт** (правило testing-бандла):

- ожидание — спека «Готово» 3 говорила «пять spec-теста (по одному на случай)»;
  факт — 12 отказывающих причин, две из них панель показала непокрытыми
  («ожидался объект», «не читается»). Поведение верно, число в норме устарело:
  закрыто правкой спеки 2026-11-11 — решение оператора «формулировка
  нейтральная по количеству»; покрыто 12 тестами;
- ожидание — `tests/conftest.py` уже даёт временный git-репозиторий (первая
  редакция спеки); факт — общей фикстуры не было, `git init` повторялся
  инлайн в трёх местах `tests/test_engine.py`. Фикстура `make_git_repo`
  заведена этим срезом; три инлайн-места не убраны (тикеты 01 это не
  требовало; уборка — кандидат на следующее касание `test_engine.py`),
  docstring фикстуры переформулирован в настоящем времени;
- ожидание — формулировка тикета «фильтр врезается в `iter_md`»; факт —
  фильтр в `iter_corpus`, `iter_md` остался фасадом (иначе живые вызовы
  `index`/`map` обошли бы корпус). Существенно по «Готово» 2 (до развилки,
  одно место); носитель правила в тикете 03 обязан назвать `iter_corpus`;
- ожидание — scope дотягивает до глобальных проверок («✓ чисто» = чисто в
  KB); факт — `index_chain_issues` (I10) ходит по `docs/` мимо корпуса, а
  рёбра графа строятся по корпусу, поэтому срез может оставить `ERR I10` и
  создать `WARN I3` на KB-файле. Не дефект критериев тикета 01 (он их не
  обещал), а незакрытая норма → тикет 04 по решению оператора;
- ожидание — «новые тесты краснеют на базовом коммите» (формулировка тикета);
  факт — краснеют 17 из 23, шесть обязаны быть зелёными по построению.
  Состав зелёных перечислен выше, расхождение снято записью, а не правкой;
- остальных расхождений ожидание/факт не было.

**Приёмка:** тикет принят оператором 2026-11-11 (ask, вариант «принять»). Ишью #1 сознательно остаётся OPEN до тикета 03 — закрытие по рамкам спеки требует живого consumer-прогона (`✓ чисто`, exit 0).
