# 03: онто-док DSH

**Спека:** [docs/plans/dsh-adaptation.md](../../docs/plans/dsh-adaptation.md)

**Что построить:** DSH-прогон онто-дока одним срезом — раздел в
`skills/onto-doc/references/ontodoc-run.md` и ветка в
`skills/onto-doc/SKILL.md`: fan-out через `subagent` (spawn) с
`provider`, `model`, `reasoning_effort` из `[agents.curator]`, все
кураторы в одном сообщении, каждый пишет только внутри корня KB и
возвращает JSON-строку `path/curator/files/refusal`, родитель
агрегирует строки и сверяет их с `git diff`. ZCode-файл
`.zcode/workflows/onto-doc.dwf.ts` остаётся и не переписывается.
Временная KB — git-проект в temp; прогон идёт из этого репозитория —
конфиг и скиллы здешние, `init` во временном проекте не нужен.

**Блокируется:** 01 (маршрут куратора и панель для ship). 02 не
требуется: временная KB ставится установщиком, конфиг берётся из
репозитория.

**Демо-путь:** живой прогон во временной KB с двумя областями: git-проект
в temp, прогон из этого репозитория, `[agents.curator]` — из здешнего
конфига; на каждую область — строка куратора, файлы в diff совпадают
со строками, запись вне корня KB отсутствует; контрактный тест краснеет
на базовом коммите и зеленеет на срезе; ZCode-тест `.dwf.ts` остаётся
зелёным.

**Критерии приёмки**:

- [ ] DSH-процедура — артефакт: `skills/onto-doc/SKILL.md`,
      `skills/onto-doc/references/ontodoc-run.md`; ожидание: DSH-ветка
      идёт через `subagent` (не через `workflow` и не через `.dwf.ts`),
      маршрут и уровень из `[agents.curator]`, проверки `<root>` и
      плана на месте, ответ куратора — JSON-строка с четырьмя полями,
      родитель сверяет её с diff; старая строка «DSH и Qoder — вне
      плана» заменена DSH-процедурой, Qoder остаётся пробелом
      (спека, «Готово» 5)
- [ ] живой прогон — артефакт: временная KB с двумя областями, отчёт и
      `git diff --name-only`; ожидание: по строке на область, файлы
      строк совпадают с diff, записей вне корня нет (спека, «Готово» 5)
- [ ] ZCode legacy — артефакт: `.zcode/workflows/onto-doc.dwf.ts`,
      `tests/test_workflow_onto_doc.py`; ожидание: файл не переписан,
      тест зелёный (спека, «Готово» 6)
- [ ] контракт — артефакт: `tests/test_skill_onto_doc.py`,
      `tests/test_bundle_references.py`; ожидание: новые DSH-проверки
      краснеют на базовом коммите и зелены на срезе; пин шага
      «2. Запусти сохранённый workflow» сохранён для ZCode или
      перевешен вместе с текстом; существующие ZCode-проверки не рваны
      (спека, «Готово» 5)
- [ ] охранник — артефакт: `python3 -m pytest tests/ -q`,
      `python3 skills/kb-search/gitmark.py lint --strict`; ожидание:
      зелёные после среза (спека, «Готово» 9)

## Доказательства

Срез: worktree `ontoship-ntin-wt-dsh03`, ветка `dsh03-onto-doc` от базового
коммита `33ea618`. Тесты первыми: `3ef11c6` — красная проба, `af6c552` —
реализация. `create_worktree` снова упал («node» нет в PATH), worktree
создан `git worktree` (спека, следствие 6).

**Красная проба на базовом коммите** (отдельный worktree `/tmp/dsh03-red`
на `33ea618` с финальными `tests/test_skill_onto_doc.py` и
`tests/test_bundle_references.py`):

```text
$ git worktree add --detach /tmp/dsh03-red 33ea618
$ cp tests/test_skill_onto_doc.py tests/test_bundle_references.py /tmp/dsh03-red/tests/
$ cd /tmp/dsh03-red && python3 -m pytest tests/ -q
11 failed, 457 passed in 4.92s
```

Проба-worktree после прогона снят, лог остаётся здесь. Падения — только
контракты среза: шесть новых DSH-проверок (`test_dsh_run_procedure_is_named`,
`test_dsh_skill_branch_is_named`, их can-fail пробы и две проверки
DSH-раздела в `tests/test_bundle_references.py`) и пять обновлённых
контрактных случаев (новые обязательные фразы, `транспортом харнесса`,
`git diff --cached --name-only`). Остальные 457 зелены.

**Разбор расхождений ожидание/факт:**

- ожидание — `create_worktree` создаёт worktree; факт — падает на `node`
  в PATH, использован `git worktree` (разрешено спекой);
- ожидание — в temp-проекте `git diff` показывает только файлы кураторов;
  факт первого прогона — куратор пересобрал индекс (`kb-curate` велит), и
  `git add -A` добавил производное `.gitmark/index.db`:

  ```text
  $ cd /tmp/dsh03-live-kb && git add -A && git diff --cached --name-only
  docs/reference/auth.md
  docs/reference/README.md
  docs/services/billing/README.md
  docs/services/README.md
  .gitmark/index.db
  ```

  Причина — в temp-проекте не было `.gitignore` (`init` там не
  запускался). Разбор: дефект среды прогона, не процедуры. Каталог после
  разбора нормализован (`.gitignore` добавлен, `.gitmark` убран из
  индекса), поэтому исходную индексацию он уже не воспроизводит — запись
  инцидента здесь, логом. Чистый прогон пошёл в проекте с `.gitignore` из
  набора DSH в стартовом коммите (`.gitmark/`, `*-map.html`, `.scratch/`,
  `.agents/skills/`), и `diff` совпал со строками;
- остальных расхождений не было.

**Реализация.**

- `skills/onto-doc/SKILL.md`: шаг 1 сверяет маршрут и уровень с каталогом
  харнесса — в DSH `list_subagent_models`, в ZCode `ListModels`; при
  отсутствии `level` DSH берёт штатный дефолт модели с пометкой в отчёте,
  ZCode — максимум из доступных; шаг 2 сохраняет ZCode-пин (сохранённый
  workflow, три аргумента `root`, `plan`, `model`) и добавляет DSH-ветку:
  fan-out `subagent` (spawn, не `subagent_fork`), все кураторы в одном
  сообщении, `provider`, `model` и `reasoning_effort` из
  `[agents.curator]`, `workflow` не используется (его `agent()` не несёт
  `effort`); план проверяет родитель до fan-out (относительный путь, без
  `..` и начального `/`, без повторов, пустой план — стоп); ответ
  куратора — JSON-строка `path`, `curator`, `files`, `refusal`, ответ не
  по схеме — именованный отказ строки; шаг 3 «Шаги» называет транспорт
  харнесса, а не workflow-транспорт. Guard-фраза на
  `references/ontodoc-run.md` и сверка карточки сохранены: индексация
  `git add -A`, затем `git diff --cached --name-only`, пустой `files` при
  непустом diff и лишний `files` — расхождение.
- `skills/onto-doc/references/ontodoc-run.md`: общий контракт обезличен
  (прогон — workflow или fan-out, строка отчёта — четыре поля);
  ZCode-раздел не тронут; новый раздел `## dsh — прогон онто-дока`:
  маршрут `<provider>/<model>` и `reasoning_effort`, живая сверка
  `list_subagent_models`, проверки плана и корня, срез по `kb-curate`,
  `cwd` субагента — чекаут сессии и сверка `git status` на запись мимо
  `root`, JSON-строка и отказ по схеме, `git add -A` и
  `git diff --cached --name-only` (без индексации новые файлы в diff не
  видны), пустой `files` при непустом diff и лишний `files` —
  расхождение; общая строка «DSH и Qoder — вне плана» заменена отдельным
  Qoder-пробелом.
- `tests/test_skill_onto_doc.py`, `tests/test_bundle_references.py`:
  DSH-контракты с секционным срезом и can-fail пробами; составные якоря
  привязывают аргументы спавна к `provider`/`model`/`reasoning_effort`, а
  поля строки — к `path`/`files`, поэтому выпадение токена не прячется за
  соседним предложением. ZCode-пины (`сохранённый workflow`, `тремя
  аргументами`) — в `SKILL.md` и `tests/test_bundle_references.py`; сам
  `.dwf.ts` — в `tests/test_workflow_onto_doc.py`.

**Живой прогон.** Временная KB `/tmp/dsh03-live-kb2` — git-проект:
`.gitignore` из набора DSH, `README.md`, `src/auth.py`, `src/billing.py`;
стартовый коммит `a11ecb1`. Живой каталог маршрута:
`list_subagent_models(provider=deepseek-account, model=deepseek-flash)` —
уровни `off`, `low`, `high (default)`, `max`; `[agents.curator]` —
`deepseek-account/deepseek-flash` и `level = "low"`, пара доступна. Два
куратора запущены одним сообщением через `subagent` (spawn, не
`subagent_fork`) с cwd — worktree среза и `provider` `deepseek-account`,
`model` `deepseek-flash`, `reasoning_effort` `low`; корень KB — в промпте.
Строки из закрывающих сообщений субагентов:

```json
{"path": "docs/reference", "curator": "куратор-1-docs/reference", "files": ["docs/reference/auth.md", "docs/reference/README.md"], "refusal": ""}
{"path": "docs/services", "curator": "куратор-2-docs/services", "files": ["docs/services/billing/README.md", "docs/services/README.md"], "refusal": ""}
```

Сверка родителя в корне прогона:

```text
$ git add -A && git diff --cached --name-only | sort
docs/reference/README.md
docs/reference/auth.md
docs/services/README.md
docs/services/billing/README.md
```

Объединение `files` двух строк — те же четыре файла; `refusal` пуст в
обеих; производное `.gitmark/` осталось ignored. Содержимое строк живое,
не пустое: у документов frontmatter (`node_type: reference`/`service`),
типизированные ссылки `documents: [../../src/auth.py]` и
`documents: [../../../src/billing.py]`, индексы `docs/reference` и
`docs/services`. Записей вне корня нет: `git status` worktree на момент
сверки — одна строка `M skills/onto-doc/references/ontodoc-run.md`
(незакоммиченная правка про `git add -A`, вошла в `af6c552` амендом),
правки `SKILL.md` уже были в коммите среза; `git status` основного
чекаута пуст. Поиск строки `Биллинг — счета и списания` по `/tmp` и
форкам (`grep -rl --include=*.md`) находит файлы только в двух каталогах
проб — в чекаутах и домашних доках записи нет.

**ZCode legacy.** `.zcode/workflows/onto-doc.dwf.ts` не переписан:
`git diff 33ea618..HEAD -- .zcode/` пуст. Тест:

```text
$ python3 -m pytest tests/test_workflow_onto_doc.py -q
......                                                                   [100%]
6 passed in 0.01s
```

**Зелёный счёт.** `python3 -m pytest tests/ -q` — **468 passed = 462 + 6**
(четыре проверки DSH-ветки в `test_skill_onto_doc.py`, две — в
`test_bundle_references.py`); `python3 skills/kb-search/gitmark.py
lint --strict` — «чисто (102 файлов)».

**Панель (живой прогон, 2026-11-09).** Четыре роли через `subagent` с
`provider` `deepseek-account`, `model` `deepseek-flash` и
`reasoning_effort` `max` из конфига; фолбэков нет. Вердикты:
reviewer-spec — «принять с находками» (1 P2 / 2 P3), reviewer-tests —
«принять с находками» (3 P2 / 3 P3), reviewer-code — «отклонить»
(1 P1 / 3 P2 / 6 P3), reviewer-kb — «принять с находками»
(1 P1 / 2 P2 / 2 P3). Сырых 24 (2 P1 / 9 P2 / 13 P3), после
дедупликации 16 (1 P1 / 6 P2 / 9 P3). Правка `264b7f0` закрыла 15:
P1 — после `git add -A` сверка идёт `git diff --cached --name-only`
(в скилле, справочнике и пинах), а не пустой unstaged-diff; P2 —
составные якоря тестов привязывают аргументы спавна к
`provider`/`model`/`reasoning_effort`, а поля строки к `path`/`files`;
разведение `level` DSH/ZCode (DSH — дефолт модели с пометкой);
шаг 3 «Шаги» — транспорт харнесса, без workflow-противоречия;
запись инцидента — логом, без ложного «каталог хранит состояние»;
красная проба — командами и выводом; P3 — пустой DSH-раздел краснеет,
`_drop_phrase` вместо хрупких замен, проверка плана полнее
(`без начального /`), `cwd` и `git status` за записью мимо `root`,
сверка `files` в обе стороны, ZCode-команда и адреса пинов в
доказательствах. Оставлена одна P3 — резюме DSH-правил в `SKILL.md`
дублирует справочник: полный текст живёт в `references/ontodoc-run.md`,
резюме сторожится контрактом, проектное переопределение справочника
правит резюме вместе с ним. Повторного прогона нет — один прогон на
проход.

**Приёмка:** тикет принят оператором 2026-11-09 (ask, вариант «принять»).
