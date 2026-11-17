# Проверки релиза v0.7.0 (после merge и тегирования, 2026-11-17)

Merge ff `51dc54f` (срез `a5f48aa` + правки панели), worktree
`ctb06-core-release` снесён; тег `v0.7.0` на merge-коммите,
push origin main + тега (SSH). Артефакты этой секции вносит
post-tag коммит main (хроника релиза) — в дереве тега их нет.

## Критерий 1: тег v0.7.0 на origin

```
git push origin main v0.7.0
   b7c64b5..51dc54f  main -> main
 * [new tag]         v0.7.0 -> v0.7.0
git ls-remote origin refs/heads/main refs/tags/v0.7.0
51dc54fa8c36c0661cca74bf05622d0169166e45	refs/heads/main
51dc54fa8c36c0661cca74bf05622d0169166e45	refs/tags/v0.7.0
```

Тег и main на origin ведут на merge-коммит `51dc54f`; демо-путь
тикета сомкнут. Красная база: тега не было (02-red-base.md).

## Критерий 2: чистая установка из дерева тега

Лог — [install-from-tag.log](install-from-tag.log): `git archive
v0.7.0` → `/tmp/ctb06-tag-tree`, `install.sh --copy` в свежий
`/tmp/ctb06-release-probe`, затем `--check`:

```
ok kb-search (copy) … ok pack (copy)   # 10 строк ok
check: ok, exit 0
бандлов: 10; chain: Нет такого файла или каталога
```

Ожидание спеки «Готово» 6 (10 бандлов, check: ok) выполнено;
красная база — состав 11 с chain на 88c8825.

## Критерий 3: selfhost повторный init

Лог — [selfhost-init.log](selfhost-init.log), diff AGENTS.md —
[selfhost-init.diff](selfhost-init.diff) (0 байт):

```
test_repo_managed_block_matches_the_init_block — 1 passed
.gitignore: ok .gitmark/ *-map.html .scratch/ .agents/skills/
.agents/config.toml: 6 секций ролей
docs/ops/continue.md: существует (init не правит)
git diff AGENTS.md — пусто (diff 0)
стражи chain: test_block_carries_no_chain_vocabulary +
test_chain_is_retired_from_the_core — 2 passed
```

Расхождение ожидание/факт: ожидание — полная идемпотентность;
факт — строка `.agents/packs/` отсутствовала в .gitignore (selfhost
не пере-init-лся с появления pack-канала standards-autoship).
Не дефект релиза: init по контракту добавил недостающую строку
(существующие строки, порядок и комментарии сохранены), пять
строк на месте, тесты init зелёные (26 passed). Правка
.gitignore — в этом post-tag коммите. Тест managed-block —
паритетный инвариант (зелёный и на базе нарезки); краснота
критерия 3 — grep chain-команд блока (02-red-base.md).

## Критерии 4/5: записи

В тикете («Записи»: отсрочка team-релиза v0.3.0 и активации,
стек v0.2.1/контракт 2) и хронике continue.md (post-tag коммит).
Клаузы критериев 3/4 ревизованы к спеке «Готово» 6 и evidence 04
(разбор — тикет «Расхождения»); требования не менялись.

## Контур после merge (main 51dc54f + post-tag правки)

```
python3 -m pytest -q          # 786 passed
gitmark.py lint --strict      # ✓ чисто (57 файлов)
install.sh --check .          # check: ok (selfhost)
гейты пака                    # .agents/packs/ нет — ноль
```

Факт среды: `pytest.ini` несёт `norecursedirs = vendor .scratch`
(переопределяет умолчание) — pytest main собирает тесты вложенных
worktree `.agents/worktrees/*` и краснит import mismatch (29
errors при живом worktree). Набор прогнан после сноса worktree
(практика тикетов 05/06); зацепка — в leads юнита.

Уборка проб: `/tmp/ctb06-tag-tree`, `/tmp/ctb06-release-probe`
снесены после снятия логов (SAFE, эфемерные).