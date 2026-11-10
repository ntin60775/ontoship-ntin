---
node_type: index
title: Скиллы — бандлы метода
service: _platform
status: active
updated: 2026-11-10
tags: [index, skills, bundles]
links:
  part_of: [../README.md]
  relates_to: [../docs/ops/continue.md]
---

# Скиллы

Состав скиллов ведёт один машинный носитель — массив `SKILLS` установщика
`scripts/install.sh`; канал один — `<project>/.agents/skills`. Ядро KB — `kb-search`,
`kb-curate`, `init`; фазы метода — `grilling`, `to-tickets`, `ship`;
правило качества — `testing`; ревью плана — `critic`; док-часть — `onto-doc`.

- [kb-search/](kb-search/SKILL.md) — движок GitMark и поиск по KB.
- [kb-curate/](kb-curate/SKILL.md) — CREATE, UPDATE, DEPRECATE, LINK,
  REINDEX; модель онтологии.
- [init/](init/SKILL.md) — управляемый блок, `.gitignore`, конфиг ролей;
  машинный источник перечня ролей `roles.py`.
- [grilling/](grilling/SKILL.md) — интервью по фронтиру, выход в спеку
  на план-гейт.
- [to-tickets/](to-tickets/SKILL.md) — нарезка спеки на tracer-bullet
  тикеты.
- [ship/](ship/SKILL.md) — один проход: worktree, тесты, ревью-панель,
  merge.
- [testing/](testing/SKILL.md) — классы тестов и планка качества.
- [critic/](critic/SKILL.md) — критика плана до первого ship.
- [onto-doc/](onto-doc/SKILL.md) — тяжёлая док-часть: fan-out кураторов
  по плану.

Новый скилл появляется бандлом в `scripts/install.sh`, строкой здесь и
кортежем в `tests/test_install.py` — одним коммитом; паритет держит тот же
тест.
Строка «Раскладки» в `AGENTS.md` ведёт сюда.
