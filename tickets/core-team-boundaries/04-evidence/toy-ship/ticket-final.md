# Тикет 01 — Опечатка README

Блокируется: нет
Блокирует: нет

Спека: [toy-readme.md](../../docs/plans/toy-readme.md), «Готово» 1.
База: `79d8e5d`.

## Задумка

Правка опечатки в README проекта: «self-sufficent» →
«self-sufficient».

## Демо-путь

`grep self-sufficient README.md` находит слово; spec-тест зелёный.

## Критерии приёмки

1. README несёт «self-sufficient», опечатки «self-sufficent» нет.
   Артефакт: `tests/test_readme.py` + вывод прогона. Ожидание:
   спека «Готово» 1. На базе падает: опечатка присутствует.
   Команда прогона: `python3 -m pytest tests/ -v`.
   Логи: [01-evidence/01-red-base.log](01-evidence/01-red-base.log)
   (красный на базе `79d8e5d`, 2 failed),
   [01-evidence/02-green-suite.log](01-evidence/02-green-suite.log)
   (зелёный набор, 2 passed, и демо-путь).

## Разбор расхождений

Не было: ожидание спеки «Готово» 1 и факт после правки совпали
(README несёт «self-sufficient», опечатки нет). Красным был только
базовый прогон на `79d8e5d` — обещанная краснота критерия, не расхождение.