# Каталог моделей — вывод list_subagent_models (как есть)

Источник: фактические результаты инструмента list_subagent_models в логе
сессии e4f84618 (проба ctb04), 2026-11-17. Все три вида вызова:
без аргументов (провайдеры), с провайдером (модели), с провайдером и моделью (уровни).
Текст результатов приведён дословно, без пересказа.

## Вызов 1: `{}`

```text
deepseek-account — DeepSeek Account
qwen-token-plan — qwen-token-plan
qwen-token-plan-max — qwen-token-plan-max
qwen-token-plan-deepseek — qwen-token-plan-deepseek
```

## Вызов 2: `{"provider": "qwen-token-plan-deepseek"}`

```text
qwen-token-plan-deepseek/deepseek-v4.1-flash-1017 — DeepSeek V4.1 Flash 1017
```

## Вызов 3: `{"provider": "qwen-token-plan-max"}`

```text
qwen-token-plan-max/qwen4-max-preview — Qwen4 Max preview
```

## Вызов 4: `{"provider": "deepseek-account"}`

```text
deepseek-account/deepseek-flash — DeepSeek-V4.1-Flash
```

## Вызов 5: `{"provider": "qwen-token-plan"}`

```text
qwen-token-plan/qwen3.8-flash — Qwen3.8 Flash
```

## Вызов 6: `{"provider": "qwen-token-plan-deepseek", "model": "deepseek-v4.1-flash-1017"}`

```text
qwen-token-plan-deepseek/deepseek-v4.1-flash-1017 — DeepSeek V4.1 Flash 1017
Reasoning efforts:
high (default) — High
max — Max
```

## Вызов 7: `{"provider": "qwen-token-plan-max", "model": "qwen4-max-preview"}`

```text
qwen-token-plan-max/qwen4-max-preview — Qwen4 Max preview
Reasoning efforts:
medium (default) — Medium
xhigh — Xhigh
```

## Вызов 8: `{"provider": "deepseek-account", "model": "deepseek-flash"}`

```text
deepseek-account/deepseek-flash — DeepSeek-V4.1-Flash
Reasoning efforts:
off — Off: Use for simple tasks that do not need reasoning.
low — Low: Prefer for routine or latency-sensitive tasks.
high (default) — High: The default balance for most tasks.
max — Max: Reserve for the hardest quality-first tasks.
```

## Вызов 9: `{"provider": "qwen-token-plan", "model": "qwen3.8-flash"}`

```text
qwen-token-plan/qwen3.8-flash — Qwen3.8 Flash
Reasoning efforts:
medium — Medium
xhigh (default) — Xhigh
```
