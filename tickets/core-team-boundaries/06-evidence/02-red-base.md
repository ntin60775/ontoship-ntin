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

Текущий selfhost-блок в паритете с init (chain-команд нет, тест
`test_repo_managed_block_matches_the_init_block` зелёный на main);
повторный init релиза доказывает идемпотентность (diff — 03-checks.md).

## Критерии 4/5: записей отсрочки team и стека в тикете нет

```
grep -n "Записи\|Отсрочка\|Стек" tickets/core-team-boundaries/06-core-release.md
# пусто (до правки тикета этим срезом)
```