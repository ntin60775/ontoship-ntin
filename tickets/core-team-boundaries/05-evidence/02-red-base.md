# Базовые факты красной пробы (база 9fc1c21, до переноса)

## Критерий 1: файлов спеки и тикетов 07/08 в team нет
```
ls: невозможно получить доступ к '/home/prog7/home/dev/contrib/forks/ontoship-team/docs/plans/team-profiles.md': Нет такого файла или каталога
ls: невозможно получить доступ к '/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/07-live-proof.md': Нет такого файла или каталога
ls: невозможно получить доступ к '/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/08-suite-kb-08-protocol.md': Нет такого файла или каталога
ls: невозможно получить доступ к '/home/prog7/home/dev/contrib/forks/ontoship-team/tickets': Нет такого файла или каталога
```

## Критерий 3: маркеры ядра на перенесённую спеку (grep)
```
tests/test_skill_grilling.py:702:    """spec: docs/plans/team-profiles.md#готово — решение 23 (тикет 14):
tests/test_skill_init.py:1242:    """spec: docs/plans/team-profiles.md#готово — «Готово» 6 (тикет 04);
tests/test_skill_init.py:1252:    """spec: docs/plans/team-profiles.md#готово — «Готово» 6 (тикет 04);
tests/test_canon_sync.py:548:    """spec: docs/plans/team-profiles.md#готово — решение 23 (тикет 14):
```

## Критерий 4: виды ядра содержат 07/08 как открытые
```
19:  T07["07 живая проба universal fin-agent"]
20:  T08["08 набор, KB и протокол 08"]
37:  T06 --> T07
41:  T13 --> T07
42:  T14 --> T07
43:  T07 --> T08
51:  class T07 pending;
52:  class T08 waiting;
19:| 07 | живая проба на fin-agent (universal) | 06, 10, 11, 12, 13, 14 | — | ready | да |
20:| 08 | набор, KB и протокол 08 | 07 | 07 | blocked | нет |
```

## Критерий 2: промежуточная красная проба — перенос без правки линков

Состояние: файлы спеки и тикетов 07/08 сняты из ядра (git rm), носители
ещё не правлены. Команда: python3 skills/kb-search/gitmark.py lint --strict
```
ERR I4 docs/ops/continue.md — битая ссылка → ../plans/team-profiles.md
ERR I4 docs/ops/continue.md — битая ссылка → ../plans/team-profiles.md
ERR I4 docs/plans/README.md — битая ссылка → team-profiles.md
ERR I4 docs/plans/README.md — битая frontmatter-ссылка relates_to: team-profiles.md
ERR I4 docs/plans/core-team-boundaries.md — битая frontmatter-ссылка relates_to: team-profiles.md
ERR I4 docs/plans/standards-autoship.md — битая ссылка → team-profiles.md
ERR I4 docs/plans/standards-autoship.md — битая ссылка → team-profiles.md

scope: 134 файлов исключено по 1 префиксам
7 ERR · 0 WARN  (57 файлов · I4×7)
exit code: 1
```

## Критерий 3: промежуточная красная проба — маркеры на перенесённый путь

Команда: python3 -m pytest tests/test_traceability.py -q
```
            failures.extend(f"{path.name}: {error}" for error in errors)
>       assert not failures, "\n".join(failures)
E       AssertionError: test_canon_sync.py: spec: missing file 'docs/plans/team-profiles.md'
E         test_skill_grilling.py: spec: missing file 'docs/plans/team-profiles.md'
E         test_skill_init.py: spec: missing file 'docs/plans/team-profiles.md'
E         test_skill_init.py: spec: missing file 'docs/plans/team-profiles.md'
E       assert not ["test_canon_sync.py: spec: missing file 'docs/plans/team-profiles.md'", "test_skill_grilling.py: spec: missing file '...c: missing file 'docs/plans/team-profiles.md'", "test_skill_init.py: spec: missing file 'docs/plans/team-profiles.md'"]

tests/test_traceability.py:102: AssertionError
=========================== short test summary info ============================
FAILED tests/test_traceability.py::test_every_test_marker_resolves_to_a_durable_source
1 failed, 1 passed in 0.04s
```
