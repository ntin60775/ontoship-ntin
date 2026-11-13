---
node_type: reference
title: Динамический allowlist пресетов DSH — проба
service: _platform
status: active
updated: 2026-11-13
tags: [dsh, presets, subagent, allowlist, probe, routing]
links:
  part_of: [README.md]
  relates_to: [harnesses.md, ../plans/team-profiles.md, ../ops/continue.md]
---

# Динамический allowlist пресетов DSH

Проба 2026-11-13 на DSH 0.2.2-rc.2, профиль `web`: можно ли собрать
`allowedAgentPresets` инструмента `dsh-tool-subagent` динамически, чтобы
стек-бандл добавлял исполнителя без оверрайда пресета оркестратора.
Временный бандл `@probe/dsh-dyn-allowlist` снят после пробы; файлы профиля
совпали со снимком до неё (sha256).

## Механика

- `!!js` в `config` вычисляется рекурсивно
  (`vendor/loader/src/config/utils.ts`): массивы и вложенные объекты;
  область выражения — `with (ctx)` плюс глобальная.
- `process` доступен, `require` — нет (Host ESM): `typeof require` даёт
  `"undefined"`.
- `ctx.get(name)` доступен; provide-значение можно вызвать.
- Композиции пресетов активируются сразу на старте; выражение
  вычисляется один раз при монтировании.
- В flow-последовательности YAML запятая внутри выражения ломает парсер
  (`missed comma between flow collection entries`) — выражение берётся
  в кавычки.

## Результаты

| Проверка | Результат |
|---|---|
| массив из `process.env` | `["executor","1c-executor","1c-reviewer"]` |
| `!!js` в `allowedAgentPresets` из сервиса | пресет смонтирован, `broken: null`; allowlist `["probe-child","1c-executor"]`; неизвестный id допустим до вызова |
| `inspectCompositions()` в выражении | пустой массив и отказ схемы `expected array length >= 1`; и до, и после дочернего пресета |
| чтение файла из выражения | невозможно: `require` нет |

## Механизм

Хост-плагин реестра исполнителей в team-бандле, строка **до** деклараций
пресетов: при apply читает манифест `executors.json` и отдаёт синхронный
`executors()`. Пресет оркестратора (тикет 03, `scout` — литерал, потому
что общий сборщик контекста доступен и на дефолтном реестре):

```yaml
allowedAgentPresets: !!js "[...new Set([...ctx.get('ontoshipExecutors').executors(), 'scout'])]"
agentPreset: executor
```

У `architect` и `executor` тот же allowlist без `agentPreset`: ребёнок без
явного `agent_preset` наследует пресет родителя (панель ship).
Стеки и контурный раннер обновляют манифест, не пресет. Ограничения:
строка реестра обязана быть раньше пресетов в том же слое; ошибка чтения
манифеста — дефолт `["executor"]` и запись в лог; неизвестный id в
allowlist допустим, отказ — при вызове.

## Альтернатива

Опущенный `agentPreset` наследует пресет родителя: сессия оркестратора под
пресетом стека даёт стековых детей без allowlist. Цена — пресет стека
копирует весь composition и вручную сверяется с апстримом (так живёт
`1c`-пресет бандла `dsh-1c-contour`).