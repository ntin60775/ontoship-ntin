# Реестр зацепок юнита registry-source

P3-находки ревью-панелей и проходов; автоприёмку не блокируют. Закрытые
зацепки остаются в реестре с пометкой носителя.

## Открытые

Открытых зацепок нет.

## Закрытые

- **Термин «flash» в живых нормах пула** (панель 01, `reviewer-spec`;
  панель 02, `reviewer-kb`): снят решением оператора 2026-11-25 одним
  изменением — канон `docs/decisions/ontoship-core.md`, зеркало
  `skills/ship/references/method-phases.md`,
  `docs/reference/harnesses.md`, скилл `critic` (описание и §Пул и
  маршруты) и контракты `test_canon_sync`, `test_kb_flow`,
  `test_skill_critic`. Проба снятой фразы «Смысловые срезы на
  flash-пуле» — исторический маркер регрессии, остаётся. Sync: main.
- **`docs/plans/README.md` говорил «нарезка впереди» и `updated:
  2026-11-24`** (панель 01, `reviewer-kb`; панель 02, `reviewer-kb`):
  закрыто закрытием юнита — обе открытые записи (`registry-source`,
  `review-output`) назвали состояние, `updated` — 2026-11-25. Носитель:
  `docs/plans/README.md`.
- **Значения пула в решении 2 спеки** (панель 01, `reviewer-spec`;
  панель 02, `reviewer-code`): `docs/plans/registry-source.md` решение 2
  переписано без литералов, «значения — проектное, носитель config»;
  «Готово» исправлено раньше. Носитель: `docs/plans/registry-source.md`.
