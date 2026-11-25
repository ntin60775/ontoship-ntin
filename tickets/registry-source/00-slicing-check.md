# Самопроверка нарезки — registry-source

Спека: [docs/plans/registry-source.md](../../docs/plans/registry-source.md).
Тикеты: [01-consumers.md](01-consumers.md), [02-config-values.md](02-config-values.md).

## Покрытость «Готово» по носителям

| пункт «Готово» | тикет | носитель |
|---|---|---|
| 1. config значения пула | 02 | .agents/config.toml |
| 2. test_role_registry читает конфиг + инвариант | 01 | test_role_registry.py |
| 3. test_skill_critic POOL_MODELS из конфига | 01 | test_skill_critic.py |
| 4. init структура + выбор, test_skill_init | 01 | skills/init/SKILL.md, test_skill_init.py |
| 5. приписка critic-consilium | 01 | critic-consilium.md |
| 6. живость каталога | 02 | отчёт исполнения, list_subagent_models |
| 7. single-source proof | 01+02 | мутационные пробы, зелёный pytest после смены |
| 8. pytest зелёный, lint чист | 01+02 | вывод pytest, lint |

Все пункты закрыты тикетами.

## Рёбра и демо-пути

- Блокер 02 — 01: реальная зависимость (потребители первыми, значения
  после — решение 7, иначе config-first краснит контур).
- Демо 01: pytest зелёный, структурные мутации красные, зелёная проба
  замены зелена.
- Демо 02: config изменён, pytest зелёный (single-source), каталог жив.
- Критерий 01 «зелёная проба замены» красный на базе (хардкод
  STANDARD_POOL ловит смену) → зелёный после правки; структурные
  мутации краснят на нарушении инварианта.

## Что не вошло в срезы

Материального нет. Якорей file:line нет — место названо файлом и
символом. CI-пробел живости (pytest оффлайн) назван в спеке и тикете 02.

## Расхождение

Нет. Нарезка готова к ship (исполнение — `/ship`, один тикет за запуск).