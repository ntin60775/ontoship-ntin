# Evidence — тикет 01 юнита deliver (бандл deliver и строка входа)

База среза: main `5bffe02` (потомок `cf479db`, хэндофф-коммит).
База красной пробы: `40c0dc6`. Worktree `ontoship-ntin-wt-dlv01`,
ветка `dlv01-deliver-bundle`.

## Индекс

- [red-probe-base-40c0dc6.log](red-probe-base-40c0dc6.log) — красная
  проба критериев 1–4 финальным набором на базе: 33 failed / 31 passed,
  exit 1. Причины — по существу: паритет 11 против 10 (кортеж несёт
  deliver, базовый массив и usage — нет), отсутствие бандла
  `skills/deliver/SKILL.md`, отсутствие строки deliver в шаблоне блока
  и в блоке AGENTS.md базы.
- [criterion-tests-green.log](criterion-tests-green.log) — прогон
  критериев на срезе: `pytest tests/test_install.py
  tests/test_skill_init.py tests/test_skill_deliver.py` — 64 passed,
  exit 0.
- [selfhost-check.log](selfhost-check.log) — `install.sh --check .`
  после selfhost-установки: 11 бандлов ok (link), `check: ok`, exit 0.
- [init-block.diff](init-block.diff) — diff AGENTS.md после повторного
  init: только строка команды внутри маркеров (2 insertions,
  1 deletion); вне маркеров байты целы.

## Selfhost-порядок (триаж G-26)

Носители (SKILLS/usage/кортеж/README/шаблон/пины/бандл) →
`scripts/install.sh .` (link) → `--check` — `check: ok`.

Вывод установки (первый прогон, worktree):

```text
linked kb-search -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/kb-search
linked kb-curate -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/kb-curate
linked init -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/init
linked grilling -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/grilling
linked to-tickets -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/to-tickets
linked ship -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/ship
linked testing -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/testing
linked critic -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/critic
linked onto-doc -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/onto-doc
linked pack -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/pack
linked deliver -> /home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv01/skills/deliver
```

## Каталог скиллов текущей сессии (триаж G-15)

Каталог DSH обновляется в сессии: после selfhost-установки провайдер
переопубликовал каталог, и `deliver` появился в списке доступных
скиллов этой сессии (2026-11-17 ~17:01, Europe/Kaliningrad) вместе с
остальными бандлами ядра. Запись каталога:

```text
- `deliver`: Поставка и обновление OntoShip в проекте: полный протокол —
  источник установки, поиск проекта, состояние через --check, канал
  link/copy, установка или обновление, init, акт rollout в реестре
  потребителей с absence-поведением, отчёт фактами. Используй, когда
  просят поставить OntoShip в проект, обновить установку или выполнить
  деплой и обновление [имя_проекта].
```

До установки каталог сессии в worktree не нёс проектных скиллов
(`.agents/skills` отсутствовал) — факт переопубликации наблюдался
дважды: снятие при смене cwd и возврат с deliver после установки.

## Повторный init (критерий 4)

Случай контракта init: один BEGIN/END, внутренний текст отличается →
замена только внутреннего текста, `[WARN]`. Итоги по файлам:
`AGENTS.md` — updated inside markers; `.gitignore` — unchanged (пять
строк на месте); `.agents/config.toml` — unchanged (шесть ролей ядра и
`[validation]` на месте); `docs/ops/continue.md` — unchanged (файл
существует, init его не открывает); паков нет — шаг молчит; team-бандл
`ontoship-team` установлен (плагины executors/contract/chain-skill/
names; версия инструментом не выдаётся).

Идемпотентность: блок после замены байт-в-байт равен шаблону
(`block == template: True`), второй прогон init — случай «внутренний
текст равен шаблону», изменений нет (`git diff` пуст после).