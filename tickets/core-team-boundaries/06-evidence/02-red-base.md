# Базовые факты красной пробы (тикет 06)

База нарезки — `88c8825` (историческая); исполнение — от main
`d41dd87` (после приёмки 05 и 07).

## Критерий 1: тега v0.7.0 нет

```
git tag -l v0.7.0                      # пусто
git ls-remote origin v0.7.0            # пусто (origin: v0.6.0 = 33a4122)
```

## Критерий 2: на базе нарезки состав 11 бандлов (с chain)

```
git show 88c8825:scripts/install.sh | grep SKILLS=
readonly SKILLS=(kb-search kb-curate init grilling to-tickets ship testing critic onto-doc pack chain)
```

Текущий main несёт 10 бандлов (chain снят тикетом 03); чистая
установка релиза доказывает состав 10 и check: ok (лог — после
тегирования, 03-checks.md).

## Критерий 3: на базе нарезки блок AGENTS.md несёт chain-команды

```
git show 88c8825:AGENTS.md | grep -n "цепочка\|орк-промт"
119:  `/ship` или «исполняй тикет N»; «цепочка» — автономная цепочка
120:  в чистой сессии, скилл `chain`; «орк-промт» — инициирующий промпт
```

Тест `test_repo_managed_block_matches_the_init_block` — паритетный
инвариант (зелёный и на базе нарезки): краснота критерия 3 держится
на grep chain-команд блока, не на этом тесте. Стражи снятия chain:
`test_block_carries_no_chain_vocabulary` (test_skill_init.py) и
`test_chain_is_retired_from_the_core` (test_install.py) — зелёные
на текущем main. Selfhost-блок в паритете с тикета 03; повторный
init релиза доказывает идемпотентность (diff 0 — 03-checks.md,
post-tag).

## Критерии 4/5: записей отсрочки team и стека в тикете нет

База записей — `d41dd87` (тикета 06 на базе нарезки `88c8825` нет,
он опубликован позже):

```
git show d41dd87:tickets/core-team-boundaries/06-core-release.md | grep -n "## Записи"
# пусто (до правки тикета срезом 06)
```
