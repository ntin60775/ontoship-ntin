# Evidence — тикет 04 «Релизы и закрытие юнита»

Юнит `deliver`, спека [deliver.md](../../../docs/plans/deliver.md),
«Готово» 7–8, решение 5; критерии 1–6 тикета
[04-releases-closure.md](../04-releases-closure.md). База нарезки:
ядро `40c0dc6`, реестр `v0.2.0` (`f7c479e`). Порядок — как в ctb06:
срез-план → merge → тег → пробы → post-tag запись.

## Существуют в срезе

- [01-release.md](01-release.md) — карта релиза: теги, push, пробы,
  порядок закрытия юнита (post-tag).
- [02-red-base.md](02-red-base.md) — красная база: тегов и записей
  закрытия нет; индекс красных логов тикетов 01–03.
- [red-base.log](red-base.log) — вывод команд красной пробы.
- [core-suite.log](core-suite.log) — полный набор ядра на срезе.
- [lint.log](lint.log) — `lint --strict` на срезе.
- [registry-tests.log](registry-tests.log) — тесты реестра.
- [04-panel.md](04-panel.md) — отчёт ревью-панели (один прогон).

## Внёс post-tag коммит main

В дереве тега отсутствуют: закрытие юнита и проверки релиза.

- [03-checks.md](03-checks.md) — проверки релиза: ls-remote ядра и
  реестра, чистые установки из деревьев тегов, diff description,
  набор и lint на main после тега.
- `ls-remote-kernel.log`, `ls-remote-registry.log`,
  `install-from-tag-kernel.log`, `install-from-tag-registry.log`,
  `description-diff.log`, `core-suite-main.log`, `lint-main.log`,
  `selfhost-check.log` — логи проверок.

## Закрытие

Носители: хроника `docs/ops/continue.md`, секция юнита в
[tickets/README.md](../../README.md), строка в
[docs/plans/README.md](../../../docs/plans/README.md), заголовки
тикетов 01–04.