# 05: документы, матрица и legacy-регрессия

**Спека:** [docs/plans/dsh-adaptation.md](../../docs/plans/dsh-adaptation.md)

**Что построить:** последний срез юнита — DSH первым классом в
`docs/reference/harnesses.md` (скиллы, панель, онто-док; без «DSH вне
плана»), запись живых проб в `docs/ops/continue.md`, приписки в
`docs/plans/review-config.md` (решение 6 — для ZCode) и
`docs/plans/onto-doc.md` (DSH-прогон через `subagent`), обновление
`README.md`, `skills/README.md`, `docs/README.md`,
`docs/reference/README.md` и `docs/plans/README.md`; проверка, что
`gen_agents.py`, `.zcode/agents/`, `.zcode/workflows/` и `deploy.json`
не сломаны, а DSH-бандла и глобальной установки нет. Старые записи о DSH
в runbook получают приписку «снято» — история не стирается.

**Блокируется:** 01, 02, 03, 04.

**Демо-путь:** открыть `docs/reference/harnesses.md` и
`docs/ops/continue.md` — DSH назван первым классом, живые пробы
записаны; `grep -n "DSH — пробел окружения" docs/reference/harnesses.md`
пуст, `grep -n "DSH и Qoder — вне плана"` по `harnesses.md`,
`review-panel.md`, `ontodoc-run.md` пуст для DSH; `pytest` и
`lint --strict` зелёные; `git diff` по ZCode-файлам пуст; DSH-бандла и
следов установки в `~/.dsh`/`~/.agents` нет.

**Критерии приёмки**:

- [ ] матрица — артефакт: `docs/reference/harnesses.md`,
      `tests/test_review_roles.py`; ожидание: DSH первый класс для
      скиллов, панели и онто-дока; в матрице, справочнике панели и прогоне
      онто-дока фраз «DSH вне плана» и «пробел окружения» для DSH нет;
      Qoder остаётся названным пробелом;
      строка о безусловном запуске генератора под DSH исправлена —
      DSH-ветка генератор не зовёт; ZCode-разделы сохранены; сторож
      DSH-пробела обновлён, мутации краснеют (спека, «Готово» 1)
- [ ] runbook — артефакт: `docs/ops/continue.md`, выписка каталога
      DSH-сессии; ожидание: живой каталог (восемь модельных скиллов,
      `ship` user-invocable), `/ship`, `install.sh --check`, базовая
      цифра 452 passed (2026-11-06) и текущая цифра среза, маршруты
      живых проб, пути артефактов; старые записи о DSH помечены «снято»
      (спека, «Готово» 1, 9)
- [ ] legacy-поправки — артефакт: `docs/plans/review-config.md`,
      `docs/plans/onto-doc.md`; ожидание: приписки про ZCode-legacy и
      DSH-прогон через `subagent` на месте, история не переписана
      (спека, «Решения», техническое следствие 7)
- [ ] индексы — артефакт: `README.md`, `skills/README.md`,
      `docs/README.md`, `docs/reference/README.md`,
      `docs/plans/README.md`; ожидание: DSH-первый-класс и юнит
      названы, спека связана, сирот нет, `gitmark.py lint --strict`
      чист (спека, «Готово» 7)
- [ ] ZCode legacy — артефакт: `git diff` по
      `skills/init/gen_agents.py`, `.zcode/workflows/`, `deploy.json`;
      прогон генератора на временном ZCode-конфиге;
      `tests/test_gen_agents.py`, `tests/test_workflow_onto_doc.py`;
      ожидание: diff по отслеживаемым файлам пуст, генератор пишет шесть
      определений на ZCode-маршрутах (`.zcode/agents/` в `.gitignore`,
      `git diff` по нему вакуумен), тесты зелёные (спека, «Готово» 6)
- [ ] без плагина — артефакт: дерево файлов, `git status`, listing
      `~/.dsh` и `~/.agents/skills` с именами; ожидание: нет
      `cordis.patch.yml`/DSH-бандла; в реестре бандлов профиля нет
      OntoShip-бандла; в `~/.agents/skills` — ровно предсуществующие
      `bruno-api`, `llm-wiki`, `logika`, `neuraldeep-api`,
      `neuraldeep-speech`, `screenshotting-gui`, скиллов OntoShip нет;
      маршрут, добавленный оператором, — не след юнита; `--check` — 0
      (спека, «Готово» 8)
- [ ] охранник — артефакт: `python3 -m pytest tests/ -q`,
      `python3 skills/kb-search/gitmark.py lint --strict`,
      `gitmark.py index`; ожидание: зелёные, индекс пересобран, поиск
      находит DSH-раздел (спека, «Готово» 7, 9)

## Доказательства

Срез: worktree `ontoship-ntin-wt-dsh05`, ветка `dsh05-docs` от базового
коммита `505ec86`. Тесты первыми: `25cee98` — красная проба, `866b6af` —
реализация. `create_worktree` снова упал («node» нет в PATH), worktree
создан `git worktree` (спека, следствие 6).

**Красная проба на базовом коммите** (worktree `/tmp/dsh05-red2` на
`505ec86` с финальным `tests/test_review_roles.py`):

```text
$ git worktree add --detach /tmp/dsh05-red2 505ec86
$ cp tests/test_review_roles.py /tmp/dsh05-red2/tests/
$ cd /tmp/dsh05-red2 && python3 -m pytest tests/ -q
4 failed, 484 passed in 5.77s
```

Падения — контракты среза: старый DSH-пробел в матрице, безусловный
генератор, снятые фразы в носителях и две can-fail пробы. Проба-worktree
снят.

**Разбор расхождений ожидание/факт:** ожидание — `create_worktree` создаёт
worktree; факт — падает на `node` в PATH, использован `git worktree`
(разрешено спекой); остальных расхождений не было.

**Реализация.**

- `docs/reference/harnesses.md`: DSH — рабочий способ панели (`subagent`,
  `provider`/`model`/`reasoning_effort`, живой `list_subagent_models`,
  фолбэк с пометкой) и онто-дока (fan-out, JSON-строка, сверка с diff);
  Qoder — отдельные названные пробелы; строка генератора: DSH-ветка
  генератор не зовёт, ZCode сохраняет; в «Доказательства» добавлен живой
  каталог DSH 2026-11-06.
- `docs/plans/review-config.md` — приписка к решению 6: DSH первый класс;
  `docs/plans/onto-doc.md` — приписка: DSH-прогон через `subagent`, файл
  `.dwf.ts` остаётся ZCode.
- `docs/ops/continue.md`: запись «Живые пробы `dsh-adaptation`» (каталог,
  `/ship`, `install.sh --check`, 452→488 passed, маршруты, артефакты);
  старые записи о DSH помечены «снято» (каталог, `MISSING_CREDENTIAL`,
  «вне плана»); «Факты окружения» обновлены.
- `README.md`, `skills/README.md`, `docs/README.md`,
  `docs/reference/README.md`, `docs/plans/README.md`: DSH первым классом,
  `init` — два харнесса, тикеты 01–04 приняты, 05 в работе.
- `tests/test_review_roles.py`: DSH-способ и Qoder-пробел в контракте
  матрицы; запрет снятых фраз в трёх носителях; can-fail пробы.

**Проверка матрицы.**

```text
$ grep -rn "DSH — пробел окружения\|DSH и Qoder — вне плана\|DSH вне плана" \
    docs/reference/harnesses.md skills/ship/references/review-panel.md \
    skills/onto-doc/references/ontodoc-run.md
пусто
```

`grep -n "пробел" docs/reference/harnesses.md` — пять вхождений: четыре
строки Qoder (заголовки и тела двух пробелов) и общее правило проверки;
DSH-строки среди них нет.

**Init и ZCode legacy.** `bash scripts/install.sh --check .` — девять
`ok ... (link)` и `check: ok`, exit 0. Генератор на временном ZCode-конфиге
`/tmp/dsh05-zcode`: ревьюеры — `qwen-token-plan/qwen3.8-flash` с `xhigh`,
критик — `deepseek-account/deepseek-flash` с `max`, куратор — с `low`:

```text
$ python3 skills/init/gen_agents.py /tmp/dsh05-zcode
6 role(s) in sync
$ ls /tmp/dsh05-zcode/.zcode/agents/*.md | wc -l
6
$ grep -h "model:\|thoughtLevel:" /tmp/dsh05-zcode/.zcode/agents/*.md | sort | uniq -c
      2 model: "deepseek-account/deepseek-flash"
      4 model: "qwen-token-plan/qwen3.8-flash"
      1 thoughtLevel: low
      1 thoughtLevel: max
      4 thoughtLevel: xhigh
```

Дифф по отслеживаемым ZCode-файлам пуст:
`git diff --stat 505ec86 -- skills/init/gen_agents.py .zcode/workflows/
deploy.json` — пусто; `.zcode/agents/probe.md` ignored
(`git check-ignore -q`). `tests/test_gen_agents.py` и
`tests/test_workflow_onto_doc.py` — 40 passed.

**Без плагина.** Бандлы профиля `~/.dsh/profiles/web` (package.json):
`@local/dsh-omp-demo-panel`, `@local/dsh-omp-theme`,
`@local/dsh-ui-refinement`, `dsh-1c-contour` — OntoShip-бандла нет;
`grep -rIl "ontoship" ~/.dsh/profiles` пуст. В `~/.agents/skills` ровно
шесть предсуществующих: `bruno-api`, `llm-wiki`, `logika`,
`neuraldeep-api`, `neuraldeep-speech`, `screenshotting-gui`; скиллов
OntoShip нет. Маршрут, добавленный оператором в профиль, — не след юнита.

**Индекс и поиск.** `python3 skills/kb-search/gitmark.py index` —
`102 файлов · 477 чанков · 251 ссылок`; `search "DSH первый класс"`
находит `docs/reference/README.md`, `README.md`, `docs/README.md`,
`docs/plans/dsh-adaptation.md`; `lint --strict` — «чисто (102 файлов)».

**Зелёный счёт.** `python3 -m pytest tests/ -q` — **488 passed = 486 + 2**
(контракт DSH-способа с запретом снятых фраз и can-fail проба).

**Ревью (2026-11-09).** Проверены четыре контракта: спецификация, тесты,
реализация и документация. Найдено 8 (5 P2 / 3 P3), правка `da1c1de`
закрыла все:

- P2 — `docs/README.md` потерял маркер списка у строки `dsh-adaptation` и
  склеивался с предыдущим пунктом;
- P2 — шапка `tests/test_review_roles.py` и spec-маркер описывали DSH как
  пробел;
- P2 — счётчики набора разъехались: стартовый промпт и запись «живых
  проб» держали 486/489 при финальных 488;
- P2 — дубль контрактной проверки матрицы и устаревшие комментарии о
  «пробеле»;
- P2 — запись о нетронутых DSH-носителях не отмечала их закрытие тикетом
  05;
- P3 — даты `updated` в трёх индексах не совпадали с правкой;
- P3 — две добавленные строки прозы были длиннее 80 символов;
- P3 — описание падения красной пробы называло снятую общую строку,
  которой на базе не было.

Повторного прогона нет.
