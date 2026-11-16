# 14 — артефакты тикета «Фильтр тривиальности»

Проход 2026-11-16, база `d4194cb` (публикация 14), worktree
`ontoship-ntin-wt-tp14` (ветка `tp14-triviality`), исполнитель-9.

- `01-red-on-base.log` — красная проба на базе: 5 новых тестов + 8 новых
  якорных случаев `method-phases` падают, старые 23 якоря зелены.
- `02-target-tests.log` — три контрактных файла: 136 passed.
- `03-full-pytest.log` — полный набор: 789 passed.
- `04-lint.log` — `gitmark.py lint --strict`: чисто.
- `05-install-check.log` — `install.sh --copy` + `--check` в temp-проекте:
  ok.
- `05-carriers-check.md` — проверка носителей: канон/зеркало/grilling/
  chain; `harnesses.md` принципа не несёт; `methodContract` 2 без bump,
  team/stack/1C-DSH не тронуты.
- `06-dev-checks.md` — dev-контур и разбор расхождений ожидание/факт.
- `09-panel.md` — вердикты панели, инцидент задержки и повторной пробы,
  судьба находок.
- `10-prod-checks.md` — prod-проверки после merge.
