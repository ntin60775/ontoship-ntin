# Реестр зацепок юнита registry-source

P3-находки ревью-панелей и проходов; автоприёмку не блокируют. Закрытые
зацепки остаются в реестре с пометкой носителя.

## Открытые

- **Термин «flash» в живых нормах пула** (панель 01, `reviewer-spec`;
  расширено панелью 02, `reviewer-kb`): пул — три различных модели,
  `glm-5.3` не flash. Термин живёт в каноне
  (`docs/decisions/ontoship-core.md`), зеркале
  (`skills/ship/references/method-phases.md`), справочнике
  (`docs/reference/harnesses.md`), описании и теле скилла `critic` и
  его контракте `tests/test_skill_critic.py`; якорь `METHOD_ANCHORS` в
  `tests/test_canon_sync.py` держит фразу дословно. Канон правится
  решением оператора; правка всех носителей — одним изменением. В
  абзаце init термин снят. Место: перечисленные носители.

## Закрытые

- **`docs/plans/README.md` говорил «нарезка впереди» и `updated:
  2026-11-24`** (панель 01, `reviewer-kb`; панель 02, `reviewer-kb`):
  закрыто закрытием юнита — обе открытые записи (`registry-source`,
  `review-output`) назвали состояние, `updated` — 2026-11-25. Носитель:
  `docs/plans/README.md`.
- **Значения пула в решении 2 спеки** (панель 01, `reviewer-spec`;
  панель 02, `reviewer-code`): `docs/plans/registry-source.md` решение 2
  переписано без литералов, «значения — проектное, носитель config»;
  «Готово» исправлено раньше. Носитель: `docs/plans/registry-source.md`.