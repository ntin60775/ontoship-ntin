---
node_type: plan
title: toy-readme — правка опечатки README
service: _platform
status: active
updated: 2026-11-16
tags: [plan, toy, probe]
links:
  part_of: [../README.md]
---

# toy-readme — правка опечатки README

Игрушечная спека пробы самодостаточности ядра (core-team-boundaries,
тикет 04). Написана заранее: grilling и нарезка в пробу не входят
(решение 4 спеки юнита, триаж G8).

## Готово

1. README проекта несёт слово «self-sufficient»; опечатки
   «self-sufficent» в README нет. Доказательство: spec-тест
   `tests/test_readme.py` читает README и сверяет оба условия;
   на базовом коммите тест красный.

## Рамки

- Правится только README; иных изменений нет.

## Ограничения

- Проба идёт без team-бандла; цепочки не запускаются.