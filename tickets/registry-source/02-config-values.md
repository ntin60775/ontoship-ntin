# Тикет 02 — значения конфига flash-1017 и живость каталога

Юнит: registry-source. Спека: [docs/plans/registry-source.md](../../docs/plans/registry-source.md).
Блокеры: тикет 01 (тесты-потребители готовы).

## Демо-путь

Конфиг `[validation]` изменён на flash-1017/max + qwen3.8-flash/xhigh +
glm-5.3/max; `pytest tests/ -q` остаётся зелёным (инвариант цел) — это
доказательство single-source; вывод живого каталога в отчёте. Показываю:
diff конфига, зелёный pytest, вывод `list_subagent_models`.

## Что делает

- `.agents/config.toml` `[validation]`: пул
  `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`,
  `qwen-token-plan/qwen3.8-flash`/`xhigh`,
  `qwen-token-plan-glm/glm-5.3`/`max`.
- Вывод живого `list_subagent_models` по парам пула и председателя,
  дата — в отчёт исполнения (носитель живости; CI-пробел pytest
  оффлайн назван в спеке).

## Критерии приёмки

- Конфиг несёт новые значения пула. Артефакт: `.agents/config.toml`.
  Ожидание: три пары flash-1017/max, qwen3.8-flash/xhigh, glm-5.3/max.
- Смена конфига не краснит тесты (single-source). Артефакт: вывод
  `pytest tests/ -q`. Ожидание: зелёный после смены значений
  (инвариант 3 различных цел).
- Живость пар пула и председателя подтверждена. Артефакт: вывод
  `list_subagent_models` в отчёте исполнения, дата. Ожидание: все
  пары живы, уровни допустимы.
- `gitmark.py lint --strict` чист. Артефакт: вывод lint.

## Рёбра

Блокер: тикет 01. Замыкает юнит; после приёмки — самопроверка нарезки
и закрытие юнита.