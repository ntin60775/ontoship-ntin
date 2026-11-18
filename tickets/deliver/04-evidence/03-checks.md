# Проверки релиза (post-tag коммит, 2026-11-18)

Релиз исполнен после ff-merge среза `82dad3c` в main и push по SSH;
этот файл и закрытие юнита внесены коммитом main после тега. В дереве
тега их нет — порядок «срез-план → merge → тег → пробы → post-tag
запись» соблюдён (прецедент ctb06).

## Критерий 1 — ядро v0.8.0

- Merge: срезы тикетов 01/03 влиты раньше (`0c8beec`, `1351377`,
  `8c7bd4d`); этот проход ff-мержит срез 04: main `29cb052` →
  `82dad3c`, merge-коммита ff не создаёт — формулировка
  триажа G-17 «тег = tip main».
- `git tag v0.8.0` → `82dad3cb8eaa138991a0cd79a2623352acb7f296`;
  push: `git push origin main v0.8.0` — `29cb052..82dad3c  main ->
  main`, `[new tag] v0.8.0` ([push-kernel.log](push-kernel.log)).
- `git ls-remote origin refs/heads/main refs/tags/v0.8.0` — оба
  адреса ведут на `82dad3c` ([ls-remote-kernel.log](ls-remote-kernel.log),
  [git-log-main.log](git-log-main.log)).
- После тега main уходит вперёд docs-only коммитом закрытия: на
  момент push SHA main и тега совпадали; тег остаётся на релизном
  коммите.

## Критерий 2 — реестр v0.3.0

- Локальные коммиты `cd88564`, `b276e3c` опубликованы: push
  `f7c479e..b276e3c  main -> main`; тег `v0.3.0` на tip main, push
  тега ([push-registry.log](push-registry.log)).
- `ls-remote`: main и `v0.3.0` — `b276e3ca3fdd…` оба
  ([ls-remote-registry.log](ls-remote-registry.log)).

## Критерий 3 — чистые установки из деревьев тегов

- Ядро: `git archive v0.8.0` → `/tmp/dlv04-tag-kernel`, установка
  `install.sh` дерева тега (не main-чекаута) `--copy` в
  `/tmp/dlv04-proj-kernel`, затем `--check`: 11 бандлов, deliver в
  составе, `check: ok` ([install-from-tag-kernel.log](install-from-tag-kernel.log)).
- Реестр: `git archive v0.3.0` → `/tmp/dlv04-tag-registry`,
  `install.sh` дерева тега `--copy`/`--check`: один бандл
  `consumer-registry`, `check: ok`, `grep -ri zcode` — 0,
  валидатор шаблона OK ([install-from-tag-registry.log](install-from-tag-registry.log)).

## Критерий 4 — описание deliver

Description и name не менялись с среза пробы `8c7bd4d`
([description-diff.log](description-diff.log)): grep по строкам
`name`/`description` пуст (exit 1 — совпадений нет). Правки norm-fixes
после пробы трогали протокол и контракт акта, не frontmatter.
Повторная проба маршрутизации не требуется; пробел не заводится.

## Критерий 5 — закрытие юнита

Внесено этим же коммитом: абзац юнита и хроника тикета 04 в
`docs/ops/continue.md`; секция юнита в `tickets/README.md`; строка
«завершена» в `docs/plans/README.md`; статусы тикетов 03 (срез) и 04
(post-tag) с evidence.

## Критерий 6 — контур зелёный

- Набор ядра на main после тега: **805 passed**
  ([core-suite-main.log](core-suite-main.log)).
- `lint --strict` чисто, 60 файлов ([lint-main.log](lint-main.log)).
- Selfhost `check: ok`, 11 бандлов
  ([selfhost-check.log](selfhost-check.log)); на срезе —
  [selfhost-check-slice.log](selfhost-check-slice.log).
- Тесты реестра **6/6** ([registry-tests.log](registry-tests.log)).
- Красные логи тикетов 01–03 собраны индексом в
  [02-red-base.md](02-red-base.md).

## Расхождения ожидание/факт

Не было: все критерии закрылись ожидаемыми фактами. Отмечено
формой записи, а не расхождением: (1) критерий 1 тикета говорит о
merge срезов 01/03 — их merge исполнен тикетами 01/03, этот проход
мержит срез 04 и тегирует tip; (2) main уходит вперёд тега docs-only
коммитом закрытия — достоинство тега как снимка релиза не меняется.