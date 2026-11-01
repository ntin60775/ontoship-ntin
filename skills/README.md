---
node_type: index
title: Скиллы — бандлы установщика
service: _platform
status: active
updated: 2026-11-01
tags: [index, skills, installer]
links:
  part_of: [../README.md]
  relates_to: [../docs/ops/continue.md]
---

# Скиллы

Бандлы установщика `scripts/install.sh` — он же машинный источник состава;
установка ставит их в `<project>/.agents/skills/`. Ядро KB — `kb-search`,
`kb-curate`, `init`; фазы метода — `grilling`, `to-tickets`, `ship`;
правило качества — `testing`; ревью плана — `critic`; док-часть — `onto-doc`.

- [kb-search/](kb-search/SKILL.md) — движок GitMark и поиск по KB.
- [kb-curate/](kb-curate/SKILL.md) — CREATE, UPDATE, DEPRECATE, LINK,
  REINDEX; модель онтологии.
- [init/](init/SKILL.md) — управляемый блок, `.gitignore`, конфиг ролей,
  генератор `gen_agents.py`.
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

Новый скилл появляется бандлом в `scripts/install.sh` и строкой здесь — одним
коммитом; строка «Раскладки» в `AGENTS.md` ведёт сюда.
