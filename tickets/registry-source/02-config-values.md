# Тикет 02 — значения пула и живость каталога

Юнит: registry-source. Спека: [docs/plans/registry-source.md](../../docs/plans/registry-source.md).
Блокеры: тикет 01 (тесты-потребители готовы).

## Демо-путь

`git diff <базовый коммит>..HEAD -- .agents/config.toml` — одна строка
пула; `pytest tests/ -q` зелёный; вывод живого каталога по четырём парам —
в evidence. Показываю: diff, вывод pytest, сохранённый вывод
`list_subagent_models`.

## Что делает

- `.agents/config.toml` `[validation]`: первая пара
  `deepseek-account/deepseek-flash`/`max` → 
  `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`; две другие
  пары (`qwen-token-plan/qwen3.8-flash`/`xhigh`,
  `qwen-token-plan-glm/glm-5.3`/`max`) не меняются.
- Живость: `list_subagent_models` по трём парам пула и маршруту
  председателя `[agents.critic]`; вывод — `02-evidence/catalog.txt`,
  дата — там же.
- Сверка каталога — не панельный прогон: порядок «панельный прогон на
  flash-1017 после review-output» из Рамок спеки на неё не
  распространяется.

## Критерии приёмки

- diff конфига — только секция `[validation]` и только первая пара.
  Артефакт: `git diff <базовый коммит>..HEAD -- .agents/config.toml`.
  Ожидание: одна строка пула; роли и `[agents.critic]` не тронуты.
- Пул — flash-1017/max, qwen3.8-flash/xhigh, glm-5.3/max. Артефакт:
  файл конфига и `tickets/registry-source/02-evidence/values.txt` (разбор
  `tomllib`). Ожидание: три записи, model-части различны.
- Смена значения не краснит набор (single-source). Артефакт: вывод
  `pytest tests/ -q` и `tickets/registry-source/02-evidence/files.txt`
  (diff по `tests/` пуст — тесты не правились). Ожидание: 0 failed без
  правки тестов в этом тикете.
- Живость подтверждена для трёх пар пула и председателя. Артефакт:
  `tickets/registry-source/02-evidence/catalog.txt` (вывод
  `list_subagent_models`, дата). Ожидание: каждая пара с уровнем из
  конфига присутствует в каталоге, уровень — в списке модели.
- Мёртвая пара или уровень вне каталога — стоп с названной причиной и
  вариантами оператору, без тихой замены. Артефакт: ask или отчёт.
  Ожидание: конфиг не несёт неживой пары.
- `gitmark.py lint --strict` чист. Артефакт: вывод lint.

## Расхождения

Разбор ожидание/факт до merge (канон testing).

- Evidence `values.txt` сначала был собран вручную: шапка содержала
  заглушку вместо скрипта и не исполнялась при записанном `exit=0` —
  дефект, правка: скрипт `02-evidence/values.py`, реальный прогон и вывод
  (панель 02, P2).
- Остальные расхождения: не было.

## Рёбра

Блокер: тикет 01. После приёмки — закрытие юнита: запись состояния в
`docs/ops/continue.md`, факты в `tickets/README.md`, статус в
`docs/plans/README.md`; evidence — `01-evidence/`, `02-evidence/`;
открытые зацепки — `leads.md`.