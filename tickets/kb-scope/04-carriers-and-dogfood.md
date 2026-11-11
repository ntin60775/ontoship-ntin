# 04: носители правила, догфуд пакета и живой consumer-прогон

**Спека:** [docs/plans/kb-scope.md](../../docs/plans/kb-scope.md)

**Что построить:** правило и проверка доезжают до людей и живого дерева. Полный
текст про KB-корпус и `gitmark.scope.json` ложится в
`skills/kb-search/SKILL.md`; `skills/kb-curate/SKILL.md` только ссылается на
него, без пересказа (сторож — контрактный тест скиллов). В этом репозитории
появляется `gitmark.scope.json` с префиксом `tickets/`. В
`docs/plans/core-kb.md` планка размера файла движка «≤ ~1300» меняется на
измеренное «≤ ~1450» с припиской решения оператора, и планка получает проверку длины в
тестах (раньше её не сторожил никто — потому она и уплыла дважды). Отдельный артефакт — ручной прогон на
consumer-дереве (форк DSH) с тремя префиксами: `snapshots/`,
`apps/web/tests/expected/`, `docs/upgrade-guide/`.

**Блокируется:** [01](01-scope-corpus.md) — носителю правила нечего описывать без
механизма; [02](02-scope-output.md) — догфуд-критерий читает поле `scope` из
`stat --json`; [03](03-scope-over-global-checks.md) — без него consumer-прогон
не даёт `✓ чисто` на поддеревьях `docs/**` с собственными README (находка
панели, решение оператора 2026-11-10).
**Предусловие:** решения 5, 10–15 спеки (ask и план-гейт 2026-11-10); онтология
(`docs/ontology.md` и её копия в `skills/kb-curate/ontology.md`) не правится —
решение 5; замеренное ожидание consumer-прогона — `19 ERR · 119 WARN
(2345 файлов · I4×19 · I5×119)` до фикса, зафиксировано в «Контексте» спеки.

**Демо-путь:** в этом репозитории после добавления `gitmark.scope.json`:
`lint --strict` даёт exit 0 и `✓ чисто`, `stat --json` показывает корпус
ровно на столько файлов меньше, сколько `.md` лежит в `tickets/`, `search` по
слову из `tickets/**` трекер не находит, `map` его не рисует. Consumer-полигон —
форк DSH (на этой машине — `~/home/dev/contrib/forks/deepseek-harness`,
машино-локальный путь, в KB не попадает): в его корне появляется
`gitmark.scope.json` с тремя префиксами, установленная копия движка
обновляется `bash scripts/install.sh <дерево>`, после чего `lint` печатает
`✓ чисто` и строку `scope: …`, а `lint --strict` выходит 0. Скопированный вывод
обоих прогонов ложится в этот файл тикета как доказательство.

**Критерии приёмки**:

- [x] носитель правила — артефакт: `skills/kb-search/SKILL.md`;
      ожидание: раздел называет `gitmark.scope.json` в корне, единственный ключ
      `exclude_prefixes`, требование завершающего `/` (решение 16), строгий
      отказ на каждую отказывающую причину, строку об исключениях (когда scope
      объявлен — в том числе при нуле исключённых) и то, что корпус общий для
      `index`, `search`, `stat`, `map`, `lint` (спека «Готово» 8, решение 13).
      Носитель называет шов — `iter_corpus`, а не `iter_md` (фасад), и место в
      коде — символом, не строкой (спека «Ограничения», правка 2026-11-11).
      Срез 03 добавил два правила, полному тексту которых нет носителя, пока
      этот тикет не закрыт: цепочка `I10` считается по корпусу (решение 18),
      связность `I3` резолвит исходящую цель по файловой системе, а входящая
      связь из исключённого поддерева и цель за корнем репозитория сироту не
      оправдывают (решение 19). Раздел обязан назвать оба, иначе поставляемый
      скилл описывает движок, который проверяет не то, что говорит скилл
- [x] пересказа нет — артефакт: `skills/kb-curate/SKILL.md`,
      `tests/test_skill_kb_curate.py`, `tests/test_skill_kb_search.py`;
      ожидание: `kb-curate` ссылается на носитель и не дублирует правило;
      контрактный тест краснеет при разъезде носителей
      (спека «Готово» 8, решение 13)
- [x] догфуд корпуса — артефакт: `gitmark.scope.json` этого репозитория, вывод
      `lint --strict`, `stat --json` и `search` на базовом коммите тикета и на
      срезе; ожидание: exit 0 и `✓ чисто`, `files` меньше ровно на число `.md`,
      лежащих в `tickets/` на базе, `stat files` == `lint checked`, `tickets/**`
      в корпусе нет, `scope` ненулевой, `search` трекер не находит;
      тест-инвариант, что корпус пакета не содержит `tickets/`
      (спека «Готово» 7, решение 12). Абсолютные числа в критерий не входят:
      перездмер 2026-11-11 — 107 файлов корпуса и 59 `.md` в `tickets/`
- [x] планка движка — артефакт: `docs/plans/core-kb.md` и вывод команды
      `wc -l skills/kb-search/gitmark.py`; ожидание: формулировка «≤ ~1450» с припиской
      решения оператора (правка 2026-11-11 после среза 02: 1411 строка);
      фактическая длина не превышает планку (спека «Готово» 8, решение 14)
- [x] онтология не тронута — артефакт: `git diff` по `docs/ontology.md` и
      `skills/kb-curate/ontology.md`, вывод `lint`; ожидание: изменений нет,
      twin-проверка I8 проходит (спека «Готово» 8, решение 5)
- [x] consumer-кейс закрыт — артефакт: скопированный вывод `lint` и
      `lint --strict`, запущенных из consumer-полигона (форк DSH, путь в
      демо-пути; движок — установленная копия `.agents/skills/kb-search/`) с
      `gitmark.scope.json` из трёх префиксов; ожидание: `✓ чисто`, exit 0,
      ни `I4×…`, ни `I5×…` в сводке — против замера до фикса `19 ERR · 119 WARN
      (2345 файлов · I4×19 · I5×119)` (спека «Готово» 6, решения 10–11)
- [x] KB сопровождён — артефакт: вывод `gitmark.py index`, `lint --strict`,
      `map`; ожидание: индекс и карта пересобраны, `lint --strict` exit 0, спека
      видна в графе и в `search`; тикеты этого юнита после догфуда вне корпуса
      (решение 12) — в `search` и на `map` их нет
      (норма — AGENTS.md «Сопровождение»; связь с догфудом держит
      предыдущий критерий)

## Что добавила ревью-панель (решения оператора 2026-11-10)

- **Нормативная обязанность `index` после правки scope.** `stat` и `search`
  читают `.gitmark/index.db`, поэтому между правкой `gitmark.scope.json` и
  пересборкой они показывают старый корпус. Решение оператора — закрыть это
  нормой, а не механизмом: строка в AGENTS.md «Сопровождение» и в
  `skills/kb-search/SKILL.md` (тик. 04) обязывает `index` после правки scope,
  как после правки документов. Критерий ниже.
- **Условие печати строки `scope:`.** Реализация печатает, когда scope объявлен
  (`K > 0`), в том числе при нуле исключённых файлов — мёртвое правило остаётся
  видимым. Носитель обязан описать это буквально; тест зафиксирован в 01
  (`test_dead_prefix_still_reports_zero`).
- **Число случаев отказа в спеке.** Перечень отказывающих причин движка не
  сходился с формулировкой спеки («пять»). Закрыто решением оператора 2026-11-11: «Готово» 3
  сформулировано нейтрально по количеству; тикету 04 остаётся перенести ту же
  формулировку в `skills/kb-search/SKILL.md` — без чисел.

- [x] обязанность пересборки — артефакт: AGENTS.md «Сопровождение»,
      `skills/kb-search/SKILL.md`; ожидание: оба называют `gitmark.scope.json`
      правкой, после которой обязателен `index`; проверка — якорный тест
      скилла сверяет строку (решение оператора 2026-11-10 по находке панели)
- [x] планка движка — артефакт: `docs/plans/core-kb.md`#готово-4 и
      вывод `wc -l skills/kb-search/gitmark.py`; ожидание: носитель говорит
      измеренное «≤ ~1450» (решение 14 спеки в правке 2026-11-11), живой замер
      среза 03 — 1427 строк; формулировка первой редакции этого критерия
      снята тем же решением и физически недостижима, в тексте тикета
      её быть не должно
- [x] проверка длины движка — артефакт: `tests/test_engine.py` (или соседний
      движковый файл); ожидание: проверка `len(splitlines()) <= 1450` зелена на
      срезе и краснеет, если добавить в движок строки (мутационная проба
      обязана быть показана в доказательстве); независимый источник числа —
      носитель `docs/plans/core-kb.md` «Готово» 4 (спека «Готово» 8, решение 14
      в правке 2026-11-11)
- [x] число причин в спеке — артефакт: `docs/plans/kb-scope.md`, «Готово» 3;
      ожидание: норма нейтральна по количеству («spec-тест на каждую
      отказывающую причину, перечисленные — минимум, не потолок»); снято
      решением оператора 2026-11-11, правка внесена, в 03 остаётся только
      перенос формулировки в `SKILL.md`

## Доказательства

Срез — worktree `ontoship-ntin-wt-kbs04`, ветка `kbs04-carriers` от базы
`2d39f21`. Хост-инструмент `create_worktree` упал (нет `node` в PATH его
подпроцесса) — worktree создан запасным путём `git worktree` по правилу
скилла ship.

### Догфуд: замеры на базе и на срезе

База `2d39f21`, до `gitmark.scope.json`:

```console
$ python3 skills/kb-search/gitmark.py index
✓ index: 108 файлов · 492 чанков · 274 ссылок · trigram=on → .gitmark/index.db
$ python3 skills/kb-search/gitmark.py stat --json
{"indexed": true, "files": 108, "bytes": 1233836, "chunks": 492, "links": 274, "areas": 8, "trigram": true, "scope": {"excluded_files": 0, "prefix_count": 0}}
$ python3 skills/kb-search/gitmark.py lint --strict
✓ чисто  (108 файлов · —)
exit=0
$ git ls-files --cached --others --exclude-standard 'tickets/*.md' 'tickets/**/*.md' | wc -l
60
$ python3 skills/kb-search/gitmark.py search "блокер" -k 3   # первый хит:
tickets/bundle-references/04-erp-demo-acceptance.md:31 › Доказательства  [bm25]
```

Срез, `gitmark.scope.json` с `{"exclude_prefixes": ["tickets/"]}`:

```console
$ python3 skills/kb-search/gitmark.py index
✓ index: 48 файлов · 372 чанков · 127 ссылок · trigram=on → .gitmark/index.db
$ python3 skills/kb-search/gitmark.py stat --json
{"indexed": true, "files": 48, "bytes": 646920, "chunks": 372, "links": 127, "areas": 7, "trigram": true, "scope": {"excluded_files": 60, "prefix_count": 1}}
$ python3 skills/kb-search/gitmark.py lint --strict
scope: 60 файлов исключено по 1 префиксам
✓ чисто  (48 файлов · —)
exit=0
$ python3 skills/kb-search/gitmark.py search "блокер" -k 5
docs/ops/continue.md:1220 › Порядок тикетов  [bm25]
skills/to-tickets/SKILL.md:42 › Порядок  [bm25]
docs/reference/harnesses.md:141 › Вход в метод по харнессам  [fuzzy]
docs/plans/harness-agnostic.md:18 › Цель  [fuzzy]
docs/plans/entry-and-continuity.md:30 › Решения план-гейта  [fuzzy]
$ python3 skills/kb-search/gitmark.py map -o docs-map.html
✓ map: docs-map.html · 48 файлов · 127 ссылок · 0 вне индекса
```

108 − 60 = 48: корпус меньше ровно на число `.md` в `tickets/` на базе;
`stat files` == `lint checked` == 48; `scope` ненулевой; трекера в выдаче
`search` нет. Инвариант корпуса —
`tests/test_scope.py::test_package_corpus_excludes_the_tracker` (фикстура
читает реальный `gitmark.scope.json` репозитория).

### Красная проба на базе

Отдельный worktree `ontoship-ntin-wt-kbs04-red` на `2d39f21`, четыре
изменённых тестовых файла скопированы поверх базы:

```console
$ python3 -m pytest tests/test_engine.py tests/test_skill_kb_search.py \
    tests/test_skill_kb_curate.py tests/test_scope.py -q
16 failed, 123 passed in 2.84s
```

Красны все 16 новых тестов: планка длины (2), полный текст scope-правила
(1), восемь мутационных проб контракта, обязанность пересборки (2), ссылка
kb-curate без пересказа (2), догфуд-инвариант (1). Красный worktree снесён.

### Полный набор и мутация планки

```console
$ python3 -m pytest tests/ -q
505 passed in 5.62s        # 489 базы + 16 новых
$ wc -l skills/kb-search/gitmark.py
1434 skills/kb-search/gitmark.py
```

Физическая мутационная проба планки (движок +20 строк, затем откат):

```console
$ printf '# padding line\n%.0s' {1..20} >> skills/kb-search/gitmark.py
$ wc -l skills/kb-search/gitmark.py
1454 skills/kb-search/gitmark.py
$ python3 -m pytest tests/test_engine.py -k "length" -q
FAILED tests/test_engine.py::test_engine_length_stays_within_the_measured_cap
FAILED tests/test_engine.py::test_engine_length_check_can_fail
2 failed, 53 deselected in 0.06s
$ git checkout -- skills/kb-search/gitmark.py
$ python3 -m pytest tests/test_engine.py -k "length" -q
2 passed, 53 deselected in 0.03s
```

Независимый источник числа планки — носитель `docs/plans/core-kb.md`
«Готово» 4 («≤ ~1450 строк — измеренная планка решения 14 юнита kb-scope,
сторожится тестом длины»); тест читает планку из носителя, не из движка.

### Онтология не тронута

```console
$ git diff --stat -- docs/ontology.md skills/kb-curate/ontology.md
(пусто)
```

Twin-проверка I8 зелёная в полном наборе
(`test_project_and_shipped_ontology_bodies_agree`).

### Consumer-прогон (форк DSH)

Полигон — `~/home/dev/contrib/forks/deepseek-harness` (машино-локальный
путь, в KB не попадает). Замер до фикса установленной копией движка:

```console
$ python3 .agents/skills/kb-search/gitmark.py lint | tail -1
19 ERR · 119 WARN  (2345 файлов · I4×19 · I5×119)
```

Совпал с замером спеки 2026-11-10. Установка обновлена из среза:

```console
$ bash scripts/install.sh /home/prog7/home/dev/contrib/forks/deepseek-harness
linked kb-search -> …/ontoship-ntin-wt-kbs04/skills/kb-search
linked kb-curate -> …/ontoship-ntin-wt-kbs04/skills/kb-curate
linked init -> …/ontoship-ntin-wt-kbs04/skills/init
linked grilling -> …/ontoship-ntin-wt-kbs04/skills/grilling
linked to-tickets -> …/ontoship-ntin-wt-kbs04/skills/to-tickets
linked ship -> …/ontoship-ntin-wt-kbs04/skills/ship
linked testing -> …/ontoship-ntin-wt-kbs04/skills/testing
linked critic -> …/ontoship-ntin-wt-kbs04/skills/critic
linked onto-doc -> …/ontoship-ntin-wt-kbs04/skills/onto-doc
```

В корне полигона — `gitmark.scope.json` с тремя префиксами
`snapshots/`, `apps/web/tests/expected/`, `docs/upgrade-guide/`:

```console
$ python3 .agents/skills/kb-search/gitmark.py lint
scope: 836 файлов исключено по 3 префиксам
✓ чисто  (1509 файлов · —)
lint exit=0
$ python3 .agents/skills/kb-search/gitmark.py lint --strict
scope: 836 файлов исключено по 3 префиксам
✓ чисто  (1509 файлов · —)
strict exit=0
```

2345 − 836 = 1509; ни `I4×…`, ни `I5×…` в сводке нет — против `19 ERR ·
119 WARN` до фикса. После merge — восстановить линки полигона на main
checkout тем же установщиком и внести запись в runbook: снос worktree без
восстановления оставил бы полигон с висячими линками движка.

### KB сопровождён

```console
$ python3 skills/kb-search/gitmark.py index
✓ index: 48 файлов · 377 чанков · 128 ссылок · trigram=on → .gitmark/index.db
$ python3 skills/kb-search/gitmark.py lint --strict
scope: 60 файлов исключено по 1 префиксам
✓ чисто  (48 файлов · —)
exit=0
$ python3 skills/kb-search/gitmark.py map -o docs-map.html
✓ map: docs-map.html · 48 файлов · 128 ссылок · 0 вне индекса
$ python3 skills/kb-search/gitmark.py search "настраиваемый корпус" -k 3
docs/plans/kb-scope.md:12 › kb-scope — настраиваемый корпус KB в движке GitMark  [bm25]
```

Спека видна в графе и в `search`; тикеты юнита вне корпуса — в `search` и
на `map` их нет.

### Разбор расхождений

- **`.md` в `tickets/` — 60, а не 59 из перездмера спеки.** Трекер drift'ит
  (добавлен тикет `cli-utf8`); абсолютные числа в критерий не входят,
  ожидание «ровно на число `.md` в `tickets/` на базе» выполнено: 108 − 60
  = 48.
- **Строка `tickets/` встречается в `docs-map.html` (1 совпадение grep).**
  Это тело KB-документов: код-блок «Раскладка» AGENTS.md и ссылки
  continue.md на `tickets/README.md` в прозе. Узлов трекера в карте нет:
  `map` рисует 48 файлов корпуса, 0 вне индекса. Критерий «map его не
  рисует» про узлы, не про цитаты в теле KB.
- **Иных расхождений ожидание/факт не было.**
