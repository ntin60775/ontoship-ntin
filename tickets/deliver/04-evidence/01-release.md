# Карта релиза v0.8.0 / v0.3.0 (тикет 04)

Срез несёт карту релиза и красную базу; тег, проверки и закрытие
юнита исполняются после merge среза, артефакты вносит post-tag коммит
main (хроника релиза). Порядок тот же, что в ctb06: срез-план →
merge → тег → пробы → post-tag запись; преждевременного закрытия
в дереве тега нет.

## Релиз ядра

- Тег `v0.8.0` — tip main после ff-merge среза тикета 04; push origin
  по SSH (`git@github.com:ntin60775/ontoship-ntin.git`), main и тег
  одним push; сверка
  `git ls-remote origin refs/heads/main refs/tags/v0.8.0` — оба ведут
  на merge-коммит (критерий 1, G-17).
- Тег ставится после merge; тег на origin до merge запрещён
  («Ограничения» тикета).
- Чистая установка из дерева тега: `git archive v0.8.0` в
  `/tmp/dlv04-tag-kernel`, `install.sh --copy` в свежий temp-проект,
  затем `--check`: ожидание 11 бандлов, `check: ok`, deliver в
  составе (критерий 3). Лог — post-tag коммит.

## Релиз реестра

- Коммиты реестра `cd88564` и `b276e3c` до этого тикета локальные;
  публикация здесь: push origin main, тег `v0.3.0` на tip main, push
  тега, сверка `ls-remote` main ↔ tag (критерий 2). Remote —
  `git@github.com:ntin60775/consumer-registry.git`.
- Чистая установка из дерева тега: `git archive v0.3.0`, `install.sh
  --copy` в temp-проект, `--check`: один бандл `consumer-registry`,
  `check: ok`; `grep .zcode` по содержимому бандла пуст (критерий 3).

## Критерий 4: описание deliver

Срез, на котором шла проба маршрутизации, — `8c7bd4d`. Diff
`skills/deliver/SKILL.md` между `8c7bd4d` и деревом тега по строкам
`name`/`description` — ожидание пусто: повторная проба не требуется.
Лог — `description-diff.log` (post-tag коммит). Правки norm-fixes
после пробы трогали протокол и контракт акта, не description.

## Пробы контура

- Набор ядра и `lint --strict` — на срезе до merge (`core-suite.log`,
  `lint.log`) и повторно на main после релиза (post-tag коммит).
- Тесты реестра `tests/test_registry.py` — `registry-tests.log`.
- Selfhost `check: ok` — на main до и после релиза (post-tag коммит).

## Закрытие юнита (post-tag запись)

Закрытие вносит post-tag коммит main:

- `docs/ops/continue.md` — абзац юнита (факты тикетов, релизы,
  названные пробелы) и хроника тикета 04;
- `tickets/README.md` — секция юнита с таблицей и закрытием;
- `docs/plans/README.md` — строка юнита «завершена»;
- статусы тикетов 01–04 «сделан, влит и принят» с evidence.

В дереве тега закрытия нет — носитель факта main после тега. Пробелы,
называемые в закрытии: ask-ноги протокола в пробе не исполнены;
`acceptance[]` deliver не заполняет; legacy-парк вне пробы; бэкап
реестра вне v1; selfhost-реестр в ntin и backfill парка — первый
реальный rollout после юнита.